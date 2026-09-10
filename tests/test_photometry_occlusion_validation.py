from pathlib import Path
import copy
import json
import math

import pytest
from jsonschema import Draft202012Validator

from scripts.validate_vx4800_photometry_occlusion import (
    object_intersects_segment,
    segment_intersects_triangle,
    validate_occlusion,
)

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "tests/fixtures/photometry/vx4800-occlusion-synthetic.json"
MODEL_SCHEMA = ROOT / "schemas/aether-photometry-occlusion-model.schema.json"
REPORT_SCHEMA = ROOT / "schemas/aether-photometry-occlusion-report.schema.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_occlusion_model_and_report_schemas_are_valid():
    model_schema = load_json(MODEL_SCHEMA)
    report_schema = load_json(REPORT_SCHEMA)
    Draft202012Validator.check_schema(model_schema)
    Draft202012Validator.check_schema(report_schema)
    errors = list(Draft202012Validator(model_schema).iter_errors(load_json(MODEL)))
    assert not errors, [error.message for error in errors]
    summary = report_schema["properties"]["summary"]["properties"]
    assert summary["productPhotometryApproved"]["const"] is False
    assert summary["full14HeadPhotometricValidationCompleted"]["const"] is False


def test_open_segment_triangle_intersection_hits_interior_and_excludes_endpoints():
    triangle = [[-1.0, -1.0, 1.0], [1.0, -1.0, 1.0], [0.0, 1.0, 1.0]]
    assert segment_intersects_triangle([0.0, 0.0, 0.0], [0.0, 0.0, 2.0], triangle) is True
    assert segment_intersects_triangle([2.0, 2.0, 0.0], [2.0, 2.0, 2.0], triangle) is False
    endpoint_triangle = [[-1.0, -1.0, 2.0], [1.0, -1.0, 2.0], [0.0, 1.0, 2.0]]
    assert segment_intersects_triangle([0.0, 0.0, 0.0], [0.0, 0.0, 2.0], endpoint_triangle) is False


def test_object_applies_once_even_when_mesh_has_two_triangles():
    obj = {
        "triangles": [
            [[-2.0, -2.0, 1.0], [2.0, -2.0, 1.0], [2.0, 2.0, 1.0]],
            [[-2.0, -2.0, 1.0], [2.0, 2.0, 1.0], [-2.0, 2.0, 1.0]],
        ]
    }
    assert object_intersects_segment([0.0, 0.0, 0.0], [0.0, 0.0, 2.0], obj) is True


def test_synthetic_opaque_plane_blocks_all_14_head_direct_paths_without_promoting_product_authority():
    report = validate_occlusion(MODEL)
    errors = list(Draft202012Validator(load_json(REPORT_SCHEMA)).iter_errors(report))
    assert not errors, [error.message for error in errors]

    assert report["status"] == "pipeline-pass"
    assert report["sourceClass"] == "synthetic-test-only"
    assert report["summary"]["pipelinePass"] is True
    assert report["bindings"]["systemSceneHashMatch"] is True
    assert report["baseline"]["headCount"] == 14
    assert report["baseline"]["sensorCount"] == 9
    assert report["baseline"]["directDistributionValidated"] is False
    assert report["model"]["objectCount"] == 1
    assert report["model"]["triangleCount"] == 2
    assert report["model"]["rayObjectIntersectionCount"] == 14 * 9
    assert report["model"]["controlledGeometryReady"] is False

    for sensor in report["occlusionLayer"]["sensors"]:
        assert sensor["baselineIlluminanceLux"] > 0
        assert sensor["occludedIlluminanceLux"] == pytest.approx(0.0)
        assert sensor["lossFraction"] == pytest.approx(1.0)
        assert len(sensor["contributions"]) == 14
        for row in sensor["contributions"]:
            assert row["directTransmissionFactor"] == pytest.approx(0.0)
            assert row["intersectedObjects"] == ["SYNTHETIC-OPAQUE-PLANE"]
            assert row["occludedIlluminanceLux"] == pytest.approx(0.0)

    assert report["summary"]["maximumLossFraction"] == pytest.approx(1.0)
    assert report["summary"]["averageLossFraction"] == pytest.approx(1.0)
    assert report["summary"]["controlledInputsReady"] is False
    assert report["summary"]["occlusionAssessmentCompleted"] is False
    assert report["summary"]["reflectanceAssessmentCompletedWhereRequired"] is False
    assert report["summary"]["toleranceSensitivityValidated"] is False
    assert report["summary"]["full14HeadPhotometricValidationCompleted"] is False
    assert report["summary"]["applicationPerformanceValidated"] is False
    assert report["summary"]["productPhotometryApproved"] is False
    assert any("Synthetic obstruction geometry" in warning for warning in report["warnings"])


def test_controlled_occlusion_labels_cannot_overcome_synthetic_unvalidated_l1_baseline(tmp_path):
    model = copy.deepcopy(load_json(MODEL))
    model["authority"] = "controlled-occlusion-input"
    model["status"] = "controlled"
    model["controlState"] = {
        "geometry": "controlled",
        "directTransmissionAssumptions": "controlled",
        "coverageComplete": True,
    }
    for obj in model["objects"]:
        obj["sourceReference"] = "controlled-review-placeholder"
        obj["sourceSha256"] = "0" * 64
    model["acceptanceCriteria"] = {
        "status": "released",
        "sensorLimits": [{"sensorId": "GRID-05", "maximumLossFraction": 1.0}],
    }
    path = tmp_path / "fake-controlled-occlusion.json"
    path.write_text(json.dumps(model), encoding="utf-8")
    report = validate_occlusion(path)
    assert report["summary"]["pipelinePass"] is True
    assert report["model"]["controlledGeometryReady"] is True
    assert report["baseline"]["directDistributionValidated"] is False
    assert report["summary"]["controlledInputsReady"] is False
    assert report["summary"]["occlusionAssessmentCompleted"] is False
    assert report["summary"]["productPhotometryApproved"] is False
