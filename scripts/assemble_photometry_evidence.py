#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

FIXTURE_ID = "vx4800-bf-01"
CONTROLLED_PROVENANCE = {"supplier", "laboratory"}


class EvidencePackageError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_configuration(candidate: dict, role: str) -> dict:
    matches = [entry for entry in candidate.get("configurations", []) if entry.get("role") == role]
    if len(matches) != 1:
        raise EvidencePackageError(f"expected exactly one candidate configuration for role {role!r}, found {len(matches)}")
    config = matches[0]
    for field in ("exactModelCode", "opticCode", "cctK"):
        if config.get(field) in (None, ""):
            raise EvidencePackageError(f"candidate configuration {role!r} lacks {field}")
    return config


def assemble_package(
    *,
    candidate: dict,
    role: str,
    configuration_id: str,
    radiance_report: dict,
    radiance_report_path: Path,
    spectral_report: dict,
    spectral_report_path: Path,
    package_id: str,
) -> dict:
    if candidate.get("fixtureId") != FIXTURE_ID:
        raise EvidencePackageError("candidate fixtureId does not match VX4800")
    if radiance_report.get("fixtureId") != FIXTURE_ID:
        raise EvidencePackageError("Radiance report fixtureId does not match VX4800")
    if spectral_report.get("fixtureId") != FIXTURE_ID:
        raise EvidencePackageError("spectral report fixtureId does not match VX4800")
    if not configuration_id:
        raise EvidencePackageError("configuration_id must be non-empty")

    config = find_configuration(candidate, role)
    candidate_exact = bool(candidate.get("review", {}).get("exactConfigurationConfirmed"))
    candidate_photometry_verified = config.get("photometryStatus") == "verified"

    angular_source = radiance_report.get("source", {})
    angular_summary = radiance_report.get("summary", {})
    spectral_source = spectral_report.get("source", {})
    spectral_configuration = spectral_report.get("configuration", {})
    spectral_eligibility = spectral_report.get("eligibility", {})

    angular_config_id = angular_source.get("configurationId")
    spectral_config_id = spectral_configuration.get("configurationId")

    angular_match = angular_config_id == configuration_id
    spectral_match = spectral_config_id == configuration_id
    angular_spectral_match = angular_config_id is not None and angular_config_id == spectral_config_id
    candidate_config_controlled = candidate_exact and bool(angular_source.get("configurationControlled")) and bool(spectral_configuration.get("controlled"))

    candidate_ies_sha = config.get("iesSha256")
    angular_ies_sha = angular_source.get("sha256")
    candidate_ies_hash_matches = bool(candidate_ies_sha and angular_ies_sha and candidate_ies_sha == angular_ies_sha)

    all_config_checks = all(
        [
            angular_match,
            spectral_match,
            angular_spectral_match,
            candidate_config_controlled,
            candidate_photometry_verified,
            candidate_ies_hash_matches,
        ]
    )

    controlled_angular_source = (
        angular_source.get("provenanceStatus") in CONTROLLED_PROVENANCE
        and not bool(angular_source.get("syntheticTest"))
        and bool(angular_source.get("configurationControlled"))
        and candidate_ies_hash_matches
    )
    radiance_pass = bool(angular_summary.get("pipelinePass")) and bool(angular_summary.get("numericalCrossCheckPass"))
    controlled_spectral_source = (
        spectral_source.get("sourceClass") in CONTROLLED_PROVENANCE
        and spectral_source.get("sha256") is not None
        and bool(spectral_configuration.get("controlled"))
        and bool(spectral_eligibility.get("spectralEvidenceEligible"))
    )
    tm3024_controlled = bool(spectral_eligibility.get("tm3024PrimaryEvidenceControlled")) and bool(
        spectral_report.get("primaryEvidenceReference")
    )

    package_eligible = all(
        [
            candidate_exact,
            all_config_checks,
            controlled_angular_source,
            radiance_pass,
            controlled_spectral_source,
            tm3024_controlled,
        ]
    )

    return {
        "$schema": "../../../schemas/aether-photometry-evidence-package.schema.json",
        "schemaVersion": "1.0.0",
        "fixtureId": FIXTURE_ID,
        "packageId": package_id,
        "authority": "derived-evidence-package",
        "status": "eligible-for-further-review" if package_eligible else "incomplete",
        "configuration": {
            "configurationId": configuration_id,
            "candidateId": candidate["candidateId"],
            "manufacturer": candidate["manufacturer"],
            "family": candidate["family"],
            "role": role,
            "exactModelCode": config["exactModelCode"],
            "opticCode": config["opticCode"],
            "cctK": config["cctK"],
            "candidateExactConfigurationConfirmed": candidate_exact,
        },
        "angular": {
            "radianceReportPath": str(radiance_report_path),
            "radianceReportSha256": sha256_file(radiance_report_path),
            "iesFilename": angular_source.get("filename", ""),
            "iesSha256": angular_ies_sha or "",
            "provenanceStatus": angular_source.get("provenanceStatus", "unknown"),
            "configurationId": angular_config_id,
            "configurationControlled": bool(angular_source.get("configurationControlled")),
            "syntheticTest": bool(angular_source.get("syntheticTest")),
            "radiancePipelinePass": bool(angular_summary.get("pipelinePass")),
            "radianceNumericalCrossCheckPass": bool(angular_summary.get("numericalCrossCheckPass")),
        },
        "spectral": {
            "spectralReportPath": str(spectral_report_path),
            "spectralReportSha256": sha256_file(spectral_report_path),
            "spdSha256": spectral_source.get("sha256"),
            "sourceClass": spectral_source.get("sourceClass", "synthetic-test-only"),
            "configurationId": spectral_config_id,
            "configurationControlled": bool(spectral_configuration.get("controlled")),
            "spectralEvidenceEligible": bool(spectral_eligibility.get("spectralEvidenceEligible")),
            "tm3024PrimaryEvidenceControlled": bool(spectral_eligibility.get("tm3024PrimaryEvidenceControlled")),
            "tm3024PrimaryEvidenceReference": spectral_report.get("primaryEvidenceReference"),
        },
        "consistency": {
            "angularAndPackageConfigurationMatch": angular_match,
            "spectralAndPackageConfigurationMatch": spectral_match,
            "angularAndSpectralConfigurationMatch": angular_spectral_match,
            "candidateConfigurationControlled": candidate_config_controlled,
            "candidatePhotometryVerified": candidate_photometry_verified,
            "candidateIesHashMatches": candidate_ies_hash_matches,
            "allExactConfigurationChecksPass": all_config_checks,
        },
        "eligibility": {
            "exactCandidateConfigurationConfirmed": candidate_exact,
            "controlledAngularSource": controlled_angular_source,
            "radianceCrossCheckPassed": radiance_pass,
            "controlledSpectralSource": controlled_spectral_source,
            "currentTm3024EvidenceControlled": tm3024_controlled,
            "packageEligibleForFurtherReview": package_eligible,
            "productPhotometryApproved": False,
        },
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble one exact VX4800 photometry configuration evidence package")
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--configuration-id", required=True)
    parser.add_argument("--radiance-report", type=Path, required=True)
    parser.add_argument("--spectral-report", type=Path, required=True)
    parser.add_argument("--package-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package = assemble_package(
        candidate=load_json(args.candidate),
        role=args.role,
        configuration_id=args.configuration_id,
        radiance_report=load_json(args.radiance_report),
        radiance_report_path=args.radiance_report,
        spectral_report=load_json(args.spectral_report),
        spectral_report_path=args.spectral_report,
        package_id=args.package_id,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(package, indent=2))
    return 0 if package["eligibility"]["packageEligibleForFurtherReview"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
