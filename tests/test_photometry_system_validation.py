from pathlib import Path
import copy
import json
import math

import pytest
from jsonschema import Draft202012Validator

from scripts.validate_vx4800_photometry_system import (
    candela_at,
    reduce_horizontal_angle,
    validate_system,
)
from tools.photometry.ies_lm63 import parse_ies

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "tests/fixtures/photometry/vx4800-system-synthetic.json"
SCENE_SCHEMA = ROOT / "schemas/aether-photometry-system-scene.schema.json"
REPORT_SCHEMA = ROOT / "schemas/aether-photometry-system-report.schema.json"
SYNTHETIC_IES = ROOT / "tests/fixtures/photometry/synthetic-narrow.ies"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_system_scene_and_report_schemas_are_valid():
    scene_schema = load_json(SCENE_SCHEMA)
    report_schema = load_json(REPORT_SCHEMA)
    Draft202012Validator.check_schema(scene_schema)
    Draft202012Validator.check_schema(report_schema)
    errors = list(Draft202012Validator(scene_schema).iter_errors(load_json(SCENE)))
    assert not errors, [error.message for error in errors]
    assert report_schema["properties"]["summary"]["properties"]["productPhotometryApproved"]["const"] is False
    assert report_schema["properties"]["summary"]["properties"]["full14HeadPhotometricValidationCompleted"]["const"] is False


def test_synthetic_system_scene_uses_exact_controlled_xy_setout_and_4_6_4_roles():
    scene = load_json(SCENE)
    assert len(scene["heads"]) == 14
    counts = {}
    for head in scene["heads"]:
        counts[head["role"]] = counts.get(head["role"], 0) + 1
        assert head["positionM"][2] == pytest.approx(0.0)
        assert head["aimDirection"] == [0.0, 0.0, 1.0]
    assert counts == {"deep-tail narrow": 4, "mid-field spot": 6, "upper-field flood": 4}
    assert scene["bindings"]["ledSetoutSha256"] == "5006690468fb93f2341cd760e651f52e30ee5739f9fee3bb3915d42031a7ee8b"
    assert scene["authority"] == "synthetic-pipeline-test"
    assert scene["acceptanceCriteria"] == {"status": "not-released", "sensorLimits": []}


def test_type_c_candela_interpolation_is_linear_for_synthetic_fixture():
    parsed = parse_ies(SYNTHETIC_IES)
    assert parsed.photometric_type == 1
    assert candela_at(parsed, 0.0, 0.0) == pytest.approx(1000.0)
    assert candela_at(parsed, 1.0, 0.0) == pytest.approx(900.0)
    assert candela_at(parsed, 2.0, 0.0) == pytest.approx(800.0)
    assert candela_at(parsed, 45.0, 0.0) == pytest.approx(0.0)
    assert candela_at(parsed, 60.0, 0.0) == pytest.approx(0.0)


def test_horizontal_reduction_rules_do_not_invent_ambiguous_symmetry():
    assert reduce_horizontal_angle([0.0, 90.0], 120.0) == pytest.approx(60.0)
    assert reduce_horizontal_angle([0.0, 180.0], 270.0) == pytest.approx(90.0)
    assert reduce_horizontal_angle([0.0, 90.0, 180.0, 270.0, 360.0], 315.0) == pytest.approx(315.0)
    with pytest.raises(Exception, match="ambiguous"):
        reduce_horizontal_angle([0.0, 120.0], 60.0)


def test_synthetic_14_head_pipeline_passes_without_promoting_product_authority():
    report = validate_system(SCENE)
    errors = list(Draft202012Validator(load_json(REPORT_SCHEMA)).iter_errors(report))
    assert not errors, [error.message for error in errors]

    assert report["status"] == "pipeline-pass"
    assert report["sourceClass"] == "synthetic-test-only"
    assert report["summary"]["pipelinePass"] is True
    assert report["summary"]["headCount"] == 14
    assert report["summary"]["sensorCount"] == 9
    assert report["inputChecks"]["setoutShaAndPositionsMatch"] is True
    assert report["inputChecks"]["controlledRoleQuantitiesMatch"] is True
    assert report["inputChecks"]["sourceIntegrityPass"] is True
    assert report["inputChecks"]["syntheticSourcesOnlyWhenSynthetic"] is True
    assert report["inputChecks"]["exactRoleSetControlled"] is False
    assert report["summary"]["controlledInputsReady"] is False
    assert report["summary"]["acceptanceCriteriaReleased"] is False
    assert report["summary"]["directDistributionValidated"] is False
    assert report["summary"]["occlusionAssessmentCompleted"] is False
    assert report["summary"]["reflectanceAssessmentCompletedWhereRequired"] is False
    assert report["summary"]["toleranceSensitivityValidated"] is False
    assert report["summary"]["full14HeadPhotometricValidationCompleted"] is False
    assert report["summary"]["applicationPerformanceValidated"] is False
    assert report["summary"]["productPhotometryApproved"] is False
    assert all(math.isfinite(sensor["totalIlluminanceLux"]) and sensor["totalIlluminanceLux"] >= 0 for sensor in report["directLayer"]["sensors"])
    assert any(sensor["totalIlluminanceLux"] > 0 for sensor in report["directLayer"]["sensors"])
    assert all(len(sensor["contributions"]) == 14 for sensor in report["directLayer"]["sensors"])
    assert any("Synthetic 14-head scene" in warning for warning in report["warnings"])


def test_synthetic_scene_cannot_masquerade_as_supplier_source(tmp_path):
    scene = load_json(SCENE)
    scene["sources"][0]["provenanceStatus"] = "supplier"
    scene["sources"][0]["syntheticTest"] = False
    path = tmp_path / "bad-synthetic-source.json"
    path.write_text(json.dumps(scene), encoding="utf-8")
    report = validate_system(path)
    assert report["summary"]["pipelinePass"] is False
    assert report["summary"]["directDistributionValidated"] is False
    assert report["summary"]["productPhotometryApproved"] is False
    assert any("synthetic pipeline scene may use only synthetic-test sources" in warning for warning in report["warnings"])


def test_controlled_labels_without_role_set_or_real_evidence_cannot_validate_direct_layer(tmp_path):
    scene = copy.deepcopy(load_json(SCENE))
    scene["authority"] = "controlled-system-review-input"
    scene["status"] = "controlled"
    scene["controlState"] = {
        "headPositions": "controlled",
        "headRoles": "controlled",
        "headAiming": "controlled",
        "sensorDefinitions": "controlled",
        "acceptanceCriteria": "released",
    }
    scene["acceptanceCriteria"] = {
        "status": "released",
        "sensorLimits": [{"sensorId": "GRID-05", "minimumLux": 0.0}],
    }
    path = tmp_path / "fake-controlled.json"
    path.write_text(json.dumps(scene), encoding="utf-8")
    report = validate_system(path)
    assert report["summary"]["pipelinePass"] is True
    assert report["inputChecks"]["exactRoleSetControlled"] is False
    assert report["summary"]["controlledInputsReady"] is False
    assert report["summary"]["directDistributionValidated"] is False
    assert report["summary"]["productPhotometryApproved"] is False
    assert any("roleSetPath" in warning for warning in report["warnings"])
