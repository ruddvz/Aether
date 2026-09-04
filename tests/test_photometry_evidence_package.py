from pathlib import Path
import importlib.util
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/assemble_photometry_evidence.py"
SCHEMA = ROOT / "schemas/aether-photometry-evidence-package.schema.json"
PRECISION = ROOT / "fixtures/vx4800/photometry/candidates/precision-evo16.json"


def load_module():
    spec = importlib.util.spec_from_file_location("assemble_photometry_evidence", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_report(path: Path, value: dict) -> Path:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


def controlled_candidate(ies_sha: str) -> dict:
    return {
        "fixtureId": "vx4800-bf-01",
        "candidateId": "test-head",
        "manufacturer": "Test Manufacturer",
        "family": "Test Family",
        "configurations": [
            {
                "role": "mid-field spot",
                "exactModelCode": "TEST-30K-16",
                "opticCode": "ME",
                "cctK": 3000,
                "photometryStatus": "verified",
                "iesSha256": ies_sha,
            }
        ],
        "review": {"exactConfigurationConfirmed": True},
    }


def radiance_report(configuration_id: str, ies_sha: str) -> dict:
    return {
        "fixtureId": "vx4800-bf-01",
        "source": {
            "filename": "exact.ies",
            "sha256": ies_sha,
            "provenanceStatus": "laboratory",
            "syntheticTest": False,
            "configurationId": configuration_id,
            "configurationControlled": True,
        },
        "summary": {
            "pipelinePass": True,
            "numericalCrossCheckPass": True,
            "productPhotometryApproved": False,
        },
    }


def spectral_report(configuration_id: str, spd_sha: str) -> dict:
    return {
        "fixtureId": "vx4800-bf-01",
        "source": {
            "sourceClass": "laboratory",
            "sha256": spd_sha,
        },
        "configuration": {
            "configurationId": configuration_id,
            "controlled": True,
        },
        "eligibility": {
            "spectralEvidenceEligible": True,
            "tm3024PrimaryEvidenceControlled": True,
            "productPhotometryApproved": False,
        },
        "primaryEvidenceReference": "LAB-TM30-24-TEST-001",
    }


def test_fully_consistent_exact_configuration_can_only_become_eligible_for_review(tmp_path):
    module = load_module()
    ies_sha = "1" * 64
    spd_sha = "2" * 64
    configuration_id = "test-head-me-30k-lab-001"
    angular_path = write_report(tmp_path / "radiance.json", radiance_report(configuration_id, ies_sha))
    spectral_path = write_report(tmp_path / "spectral.json", spectral_report(configuration_id, spd_sha))

    package = module.assemble_package(
        candidate=controlled_candidate(ies_sha),
        role="mid-field spot",
        configuration_id=configuration_id,
        radiance_report=module.load_json(angular_path),
        radiance_report_path=angular_path,
        spectral_report=module.load_json(spectral_path),
        spectral_report_path=spectral_path,
        package_id="test-head-me-30k-evidence",
    )

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(package))
    assert not errors, [error.message for error in errors]
    assert package["status"] == "eligible-for-further-review"
    assert package["consistency"]["allExactConfigurationChecksPass"] is True
    assert package["eligibility"]["packageEligibleForFurtherReview"] is True
    assert package["eligibility"]["productPhotometryApproved"] is False


def test_configuration_mismatch_hard_blocks_package_eligibility(tmp_path):
    module = load_module()
    ies_sha = "3" * 64
    angular_path = write_report(tmp_path / "radiance.json", radiance_report("CONFIG-A", ies_sha))
    spectral_path = write_report(tmp_path / "spectral.json", spectral_report("CONFIG-B", "4" * 64))

    package = module.assemble_package(
        candidate=controlled_candidate(ies_sha),
        role="mid-field spot",
        configuration_id="CONFIG-A",
        radiance_report=module.load_json(angular_path),
        radiance_report_path=angular_path,
        spectral_report=module.load_json(spectral_path),
        spectral_report_path=spectral_path,
        package_id="mismatch-test",
    )

    assert package["status"] == "incomplete"
    assert package["consistency"]["spectralAndPackageConfigurationMatch"] is False
    assert package["consistency"]["angularAndSpectralConfigurationMatch"] is False
    assert package["eligibility"]["packageEligibleForFurtherReview"] is False
    assert package["eligibility"]["productPhotometryApproved"] is False


def test_candidate_ies_hash_mismatch_hard_blocks_eligibility(tmp_path):
    module = load_module()
    angular_path = write_report(tmp_path / "radiance.json", radiance_report("CONFIG-A", "5" * 64))
    spectral_path = write_report(tmp_path / "spectral.json", spectral_report("CONFIG-A", "6" * 64))

    package = module.assemble_package(
        candidate=controlled_candidate("7" * 64),
        role="mid-field spot",
        configuration_id="CONFIG-A",
        radiance_report=module.load_json(angular_path),
        radiance_report_path=angular_path,
        spectral_report=module.load_json(spectral_path),
        spectral_report_path=spectral_path,
        package_id="hash-mismatch-test",
    )

    assert package["consistency"]["candidateIesHashMatches"] is False
    assert package["eligibility"]["controlledAngularSource"] is False
    assert package["eligibility"]["packageEligibleForFurtherReview"] is False


def test_synthetic_or_uncontrolled_spectral_evidence_cannot_pass(tmp_path):
    module = load_module()
    ies_sha = "8" * 64
    angular_path = write_report(tmp_path / "radiance.json", radiance_report("CONFIG-A", ies_sha))
    spectral = spectral_report("CONFIG-A", "9" * 64)
    spectral["source"]["sourceClass"] = "synthetic-test-only"
    spectral["source"]["sha256"] = None
    spectral["eligibility"]["spectralEvidenceEligible"] = False
    spectral["eligibility"]["tm3024PrimaryEvidenceControlled"] = False
    spectral["primaryEvidenceReference"] = None
    spectral_path = write_report(tmp_path / "spectral.json", spectral)

    package = module.assemble_package(
        candidate=controlled_candidate(ies_sha),
        role="mid-field spot",
        configuration_id="CONFIG-A",
        radiance_report=module.load_json(angular_path),
        radiance_report_path=angular_path,
        spectral_report=module.load_json(spectral_path),
        spectral_report_path=spectral_path,
        package_id="synthetic-spectral-test",
    )

    assert package["eligibility"]["controlledSpectralSource"] is False
    assert package["eligibility"]["currentTm3024EvidenceControlled"] is False
    assert package["eligibility"]["packageEligibleForFurtherReview"] is False


def test_current_precision_candidate_remains_blocked_by_real_evidence_gaps():
    candidate = json.loads(PRECISION.read_text(encoding="utf-8"))
    assert candidate["review"]["exactConfigurationConfirmed"] is False
    for config in candidate["configurations"]:
        assert config["photometryStatus"] != "verified"
        assert config["iesSha256"] is None


def test_script_has_no_product_approval_switch():
    text = SCRIPT.read_text(encoding="utf-8")
    assert '"productPhotometryApproved": False' in text
    assert "--product-photometry-approved" not in text
