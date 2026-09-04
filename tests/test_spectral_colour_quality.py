from pathlib import Path
import importlib.util
import json

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "fixtures/vx4800/photometry/spectral/validation-plan-v1.json"
PLAN_SCHEMA = ROOT / "schemas/aether-spectral-validation-plan.schema.json"
REPORT_SCHEMA = ROOT / "schemas/aether-spectral-validation-report.schema.json"
SCRIPT = ROOT / "scripts/analyze_vx4800_spectrum.py"
REQUIREMENTS = ROOT / "requirements-spectral.txt"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_script_module():
    spec = importlib.util.spec_from_file_location("analyze_vx4800_spectrum", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_spectral_plan_schema_and_current_open_state():
    plan = load_json(PLAN)
    schema = load_json(PLAN_SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(plan))
    assert not errors, [error.message for error in errors]
    assert plan["authority"] == "qualification-plan"
    assert plan["status"] == "open"
    assert all(value is False for value in plan["promotionGate"].values())


def test_current_tm30_authority_is_not_confused_with_open_source_method():
    plan = load_json(PLAN)
    refs = {entry["id"]: entry for entry in plan["standardsReferences"]}
    assert "ANSI-IES-TM-30-24" in refs
    toolchain = plan["softwareToolchain"]
    assert toolchain["version"] == "0.4.7"
    assert "TM-30-18" in toolchain["knownAuthorityLimit"]
    assert "not TM-30-24" in toolchain["knownAuthorityLimit"]
    assert REQUIREMENTS.read_text(encoding="utf-8").strip() == "colour-science==0.4.7"


def test_no_tm30_or_duv_threshold_is_invented():
    targets = load_json(PLAN)["currentProductTargets"]
    assert targets["cctK"] == 3000
    assert targets["criRaMinimum"] == 92
    assert targets["tm30Thresholds"] == "not-yet-released"
    assert targets["duvThreshold"] == "not-yet-released"


def test_product_spd_sampling_preconditions_are_explicit():
    requirements = load_json(PLAN)["sourceRequirements"]
    assert requirements["minimumProductCoverageNm"] == [380, 780]
    assert requirements["maximumProductSampleStepNm"] == 5
    assert requirements["exactRawSpdBytesRequired"] is True
    assert requirements["sha256Required"] is True
    assert requirements["exactHeadOpticConfigurationRequired"] is True


def test_csv_loader_rejects_negative_power_and_bad_sampling(tmp_path):
    module = load_script_module()
    good = tmp_path / "good.csv"
    good.write_text("wavelength_nm,power\n380,0.2\n385,0.5\n390,0.3\n", encoding="utf-8")
    wavelengths, powers = module.load_spd_csv(good)
    assert wavelengths == [380.0, 385.0, 390.0]
    assert powers == [0.2, 0.5, 0.3]

    negative = tmp_path / "negative.csv"
    negative.write_text("wavelength_nm,power\n380,0.2\n385,-0.1\n", encoding="utf-8")
    with pytest.raises(module.SpectralValidationError):
        module.load_spd_csv(negative)

    with pytest.raises(module.SpectralValidationError):
        module.validate_product_sampling([380.0, 386.0, 780.0])


def test_xy_to_uv_reference_conversion_is_stable():
    module = load_script_module()
    u, v = module.xy_to_uv1960(0.3127, 0.3290)
    assert u == pytest.approx(0.19783, abs=5e-5)
    assert v == pytest.approx(0.31221, abs=5e-5)


def test_report_schema_hard_blocks_synthetic_product_eligibility():
    schema = load_json(REPORT_SCHEMA)
    report = {
        "schemaVersion": "1.0.0",
        "fixtureId": "vx4800-bf-01",
        "generatedAt": "2026-09-04T00:00:00+00:00",
        "source": {
            "sourceClass": "synthetic-test-only",
            "description": "test",
            "sha256": None,
            "coverageNm": [380, 780],
            "maximumStepNm": 5
        },
        "configuration": {"configurationId": None, "controlled": False},
        "toolchain": {"package": "colour-science", "version": "0.4.7"},
        "methods": {
            "cri": "CIE 1995",
            "cieFidelity": "CIE 2017",
            "cctDuv": "Ohno 2013 independent cross-check",
            "tm30Compatibility": "ANSI/IES TM-30-18",
            "currentTm30Authority": "ANSI/IES TM-30-24"
        },
        "metrics": {
            "cctK": 3000,
            "duv": 0,
            "criRa": 100,
            "criR9": 100,
            "cie2017Rf": 100,
            "tm3018Rf": 100,
            "tm3018Rg": 100
        },
        "eligibility": {
            "exactSpdControlled": False,
            "exactConfigurationControlled": False,
            "supplierOrLabSource": False,
            "spectralEvidenceEligible": False,
            "tm3024PrimaryEvidenceControlled": False,
            "productPhotometryApproved": False
        }
    }
    assert not list(Draft202012Validator(schema).iter_errors(report))

    report["eligibility"]["spectralEvidenceEligible"] = True
    errors = list(Draft202012Validator(schema).iter_errors(report))
    assert errors


def test_script_never_exposes_product_approval_cli_switch():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "productPhotometryApproved\": False" in text
    assert "--product-photometry-approved" not in text
    assert "TM-30-18 compatibility values are not TM-30-24" in text
