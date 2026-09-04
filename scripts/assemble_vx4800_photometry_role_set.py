#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ID = "vx4800-bf-01"
REQUIRED_ROLES = ("deep-tail narrow", "mid-field spot", "upper-field flood")


class RoleSetError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_product_bindings(fixture_path: Path, selection_brief_path: Path) -> tuple[dict, dict, dict]:
    fixture = load_json(fixture_path)
    brief = load_json(selection_brief_path)
    if fixture.get("identity", {}).get("fixtureId") != FIXTURE_ID:
        raise RoleSetError("fixture identity does not match VX4800")
    if brief.get("fixtureId") != FIXTURE_ID:
        raise RoleSetError("selection brief identity does not match VX4800")

    emitters = fixture.get("optical", {}).get("emitters", [])
    if len(emitters) != 1:
        raise RoleSetError("expected one controlled VX4800 accent-head emitter family")
    head_count = emitters[0].get("quantity")
    if head_count != 14:
        raise RoleSetError(f"controlled VX4800 accent-head quantity must remain 14, got {head_count!r}")

    led_assets = [asset for asset in fixture.get("assets", []) if asset.get("id") == "led-setout-engineering-1.3.0"]
    if len(led_assets) != 1:
        raise RoleSetError("controlled LED setout asset is missing or ambiguous")
    led_asset = led_assets[0]

    return fixture, brief, led_asset


def assemble_role_set(
    *,
    fixture_path: Path,
    selection_brief_path: Path,
    role_package_paths: dict[str, Path],
) -> dict:
    fixture, brief, led_asset = load_product_bindings(fixture_path, selection_brief_path)
    optics = {entry["role"]: entry for entry in brief.get("optics", [])}
    if set(optics) != set(REQUIRED_ROLES):
        raise RoleSetError("selection brief must define exactly the three controlled VX4800 optical roles")

    role_keys_exact = set(role_package_paths) == set(REQUIRED_ROLES)
    if not role_keys_exact:
        missing = sorted(set(REQUIRED_ROLES) - set(role_package_paths))
        extra = sorted(set(role_package_paths) - set(REQUIRED_ROLES))
        raise RoleSetError(f"role package map mismatch; missing={missing}, extra={extra}")

    target_cct = brief.get("lightQuality", {}).get("cctK")
    if target_cct != 3000:
        raise RoleSetError(f"controlled first photometry package CCT must remain 3000 K, got {target_cct!r}")

    roles: list[dict] = []
    package_eligibility: list[bool] = []
    role_matches: list[bool] = []
    cct_matches: list[bool] = []
    configuration_ids: list[str] = []
    manufacturer_family_pairs: list[tuple[str, str]] = []

    for role in REQUIRED_ROLES:
        path = role_package_paths[role]
        if not path.is_file():
            raise RoleSetError(f"evidence package not found for {role}: {path}")
        package = load_json(path)
        if package.get("fixtureId") != FIXTURE_ID:
            raise RoleSetError(f"{role} package fixtureId does not match VX4800")

        config = package.get("configuration", {})
        eligibility = package.get("eligibility", {})
        role_match = config.get("role") == role
        cct_match = config.get("cctK") == target_cct
        package_eligible = (
            package.get("status") == "eligible-for-further-review"
            and bool(eligibility.get("packageEligibleForFurtherReview"))
            and eligibility.get("productPhotometryApproved") is False
        )

        configuration_id = config.get("configurationId")
        if not configuration_id:
            raise RoleSetError(f"{role} evidence package lacks configurationId")
        configuration_ids.append(configuration_id)
        manufacturer_family_pairs.append((str(config.get("manufacturer", "")), str(config.get("family", ""))))
        package_eligibility.append(package_eligible)
        role_matches.append(role_match)
        cct_matches.append(cct_match)

        optic = optics[role]
        roles.append(
            {
                "role": role,
                "quantity": int(optic["quantity"]),
                "targetBeamDeg": optic["targetBeamDeg"],
                "acceptableRangeDeg": optic["acceptableRangeDeg"],
                "evidencePackagePath": str(path),
                "evidencePackageSha256": sha256_file(path),
                "packageId": package.get("packageId", ""),
                "configurationId": configuration_id,
                "candidateId": config.get("candidateId", ""),
                "manufacturer": config.get("manufacturer", ""),
                "family": config.get("family", ""),
                "exactModelCode": config.get("exactModelCode", ""),
                "opticCode": config.get("opticCode", ""),
                "cctK": config.get("cctK"),
                "packageEligibleForFurtherReview": package_eligible,
                "roleMatchesPackage": role_match,
                "cctMatchesProduct": cct_match,
            }
        )

    quantities = {entry["role"]: entry["quantity"] for entry in roles}
    expected_quantities = {entry["role"]: entry["quantity"] for entry in brief["optics"]}
    quantities_match = quantities == expected_quantities == {
        "deep-tail narrow": 4,
        "mid-field spot": 6,
        "upper-field flood": 4,
    }
    total_head_count = sum(quantities.values())
    setout_match = total_head_count == fixture["optical"]["emitters"][0]["quantity"] == 14
    config_ids_unique = len(configuration_ids) == len(set(configuration_ids)) == 3
    single_family = len(set(manufacturer_family_pairs)) == 1

    all_system_inputs = all(
        [
            quantities_match,
            setout_match,
            all(package_eligibility),
            all(role_matches),
            all(cct_matches),
            config_ids_unique,
        ]
    )

    return {
        "$schema": "../../../schemas/aether-photometry-role-set.schema.json",
        "schemaVersion": "1.0.0",
        "fixtureId": FIXTURE_ID,
        "designRevision": fixture["identity"]["designRevision"],
        "authority": "derived-system-review-input",
        "status": "eligible-for-system-validation" if all_system_inputs else "incomplete",
        "productBindings": {
            "selectionBriefPath": str(selection_brief_path),
            "selectionBriefSha256": sha256_file(selection_brief_path),
            "ledSetoutPath": f"fixtures/vx4800/{led_asset['path']}",
            "ledSetoutSha256": led_asset["sha256"],
            "headCount": 14,
            "cctK": target_cct,
        },
        "roles": roles,
        "consistency": {
            "requiredRolesPresentExactlyOnce": role_keys_exact,
            "quantitiesMatchSelectionBrief": quantities_match,
            "totalHeadCountMatchesSetout": setout_match,
            "allRolePackagesEligible": all(package_eligibility),
            "allRoleNamesMatchPackages": all(role_matches),
            "allCctMatch": all(cct_matches),
            "configurationIdsUnique": config_ids_unique,
            "singleManufacturerFamily": single_family,
            "allSystemInputChecksPass": all_system_inputs,
        },
        "eligibility": {
            "roleSetEligibleForSystemValidation": all_system_inputs,
            "full14HeadPhotometricValidationCompleted": False,
            "applicationPerformanceValidated": False,
            "productPhotometryApproved": False,
        },
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble the three exact VX4800 photometry role packages into a system-validation input")
    parser.add_argument("--narrow", type=Path, required=True, help="deep-tail narrow evidence package")
    parser.add_argument("--spot", type=Path, required=True, help="mid-field spot evidence package")
    parser.add_argument("--flood", type=Path, required=True, help="upper-field flood evidence package")
    parser.add_argument("--fixture", type=Path, default=ROOT / "fixtures/vx4800/fixture.json")
    parser.add_argument("--selection-brief", type=Path, default=ROOT / "fixtures/vx4800/photometry/selection-brief.json")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = assemble_role_set(
        fixture_path=args.fixture,
        selection_brief_path=args.selection_brief,
        role_package_paths={
            "deep-tail narrow": args.narrow,
            "mid-field spot": args.spot,
            "upper-field flood": args.flood,
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["eligibility"]["roleSetEligibleForSystemValidation"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
