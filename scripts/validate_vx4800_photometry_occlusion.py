#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from scripts.validate_vx4800_photometry_system import (
    FIXTURE_ID,
    DESIGN_REVISION,
    load_json,
    resolve_repo_path,
    sha256_file,
    validate_system,
)


class OcclusionValidationError(RuntimeError):
    pass


def subtract(a: list[float], b: list[float]) -> list[float]:
    return [float(a[i]) - float(b[i]) for i in range(3)]


def dot(a: list[float], b: list[float]) -> float:
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def segment_intersects_triangle(
    origin: list[float],
    target: list[float],
    triangle: list[list[float]],
    *,
    epsilon: float = 1e-9,
) -> bool:
    """Return True when the open segment origin->target intersects the triangle.

    Möller-Trumbore is evaluated with the full segment vector, so t is the
    normalized segment parameter and must remain strictly inside (0, 1).
    Endpoint hits are excluded to prevent a source/sensor surface from
    self-occluding purely because the ray begins or ends on that surface.
    """
    if len(triangle) != 3:
        raise OcclusionValidationError("triangle must contain exactly three vertices")
    direction = subtract(target, origin)
    edge1 = subtract(triangle[1], triangle[0])
    edge2 = subtract(triangle[2], triangle[0])
    h = cross(direction, edge2)
    determinant = dot(edge1, h)
    if abs(determinant) <= epsilon:
        return False
    inv_det = 1.0 / determinant
    s = subtract(origin, triangle[0])
    u = inv_det * dot(s, h)
    if u < -epsilon or u > 1.0 + epsilon:
        return False
    q = cross(s, edge1)
    v = inv_det * dot(direction, q)
    if v < -epsilon or u + v > 1.0 + epsilon:
        return False
    t = inv_det * dot(edge2, q)
    return epsilon < t < 1.0 - epsilon


def object_intersects_segment(origin: list[float], target: list[float], obj: dict) -> bool:
    return any(segment_intersects_triangle(origin, target, triangle) for triangle in obj["triangles"])


def evaluate_criteria(criteria: dict, sensor_rows: list[dict]) -> tuple[bool | None, list[dict]]:
    if criteria["status"] != "released":
        return None, []
    by_id = {row["sensorId"]: row for row in sensor_rows}
    results: list[dict] = []
    all_pass = True
    for rule in criteria["sensorLimits"]:
        sensor_id = rule["sensorId"]
        if sensor_id not in by_id:
            raise OcclusionValidationError(f"released occlusion criterion references unknown sensor: {sensor_id}")
        row = by_id[sensor_id]
        passed = True
        max_loss = rule.get("maximumLossFraction")
        min_lux = rule.get("minimumOccludedLux")
        if max_loss is not None:
            passed = passed and row["lossFraction"] <= float(max_loss)
        if min_lux is not None:
            passed = passed and row["occludedIlluminanceLux"] >= float(min_lux)
        all_pass = all_pass and passed
        results.append(
            {
                "sensorId": sensor_id,
                "lossFraction": row["lossFraction"],
                "occludedIlluminanceLux": row["occludedIlluminanceLux"],
                "maximumLossFraction": max_loss,
                "minimumOccludedLux": min_lux,
                "pass": passed,
            }
        )
    return all_pass, results


def validate_occlusion(model_path: Path) -> dict:
    model = load_json(model_path)
    if model.get("fixtureId") != FIXTURE_ID or model.get("designRevision") != DESIGN_REVISION:
        raise OcclusionValidationError("occlusion model identity does not match controlled VX4800 revision")

    scene_path = resolve_repo_path(model["bindings"]["systemScenePath"])
    if not scene_path.is_file():
        raise OcclusionValidationError(f"bound system scene does not exist: {scene_path}")
    scene_hash_match = sha256_file(scene_path) == model["bindings"]["systemSceneSha256"]
    baseline = validate_system(scene_path)
    scene = load_json(scene_path)
    head_by_id = {head["ledId"]: head for head in scene["heads"]}

    object_rows: list[dict] = []
    model_errors: list[str] = []
    for obj in model["objects"]:
        transmission = float(obj["directTransmissionFactor"])
        if not 0.0 <= transmission <= 1.0:
            model_errors.append(f"{obj['objectId']} transmission factor outside 0..1")
        object_rows.append(
            {
                "objectId": obj["objectId"],
                "category": obj["category"],
                "directTransmissionFactor": transmission,
                "triangleCount": len(obj["triangles"]),
                "sourceReference": obj.get("sourceReference"),
                "sourceSha256": obj.get("sourceSha256"),
            }
        )

    sensor_rows: list[dict] = []
    total_hit_count = 0
    for sensor in baseline["directLayer"]["sensors"]:
        adjusted_contributions: list[dict] = []
        occluded_total = 0.0
        for contribution in sensor["contributions"]:
            head = head_by_id[contribution["ledId"]]
            factor = 1.0
            hit_objects: list[str] = []
            for obj in model["objects"]:
                if object_intersects_segment(head["positionM"], sensor["pointM"], obj):
                    hit_objects.append(obj["objectId"])
                    factor *= float(obj["directTransmissionFactor"])
            total_hit_count += len(hit_objects)
            adjusted = contribution["illuminanceLux"] * factor
            occluded_total += adjusted
            adjusted_contributions.append(
                {
                    "ledId": contribution["ledId"],
                    "role": contribution["role"],
                    "baselineIlluminanceLux": contribution["illuminanceLux"],
                    "directTransmissionFactor": factor,
                    "intersectedObjects": hit_objects,
                    "occludedIlluminanceLux": adjusted,
                }
            )
        baseline_total = float(sensor["totalIlluminanceLux"])
        loss = max(0.0, baseline_total - occluded_total)
        loss_fraction = loss / baseline_total if baseline_total > 0 else 0.0
        sensor_rows.append(
            {
                "sensorId": sensor["sensorId"],
                "category": sensor["category"],
                "pointM": sensor["pointM"],
                "baselineIlluminanceLux": baseline_total,
                "occludedIlluminanceLux": occluded_total,
                "lossIlluminanceLux": loss,
                "lossFraction": loss_fraction,
                "contributions": adjusted_contributions,
            }
        )

    criteria_pass, criteria_rows = evaluate_criteria(model["acceptanceCriteria"], sensor_rows)
    synthetic = model["authority"] == "synthetic-pipeline-test"
    controlled_geometry = (
        model["authority"] == "controlled-occlusion-input"
        and model["status"] == "controlled"
        and model["controlState"]["geometry"] == "controlled"
        and model["controlState"]["directTransmissionAssumptions"] == "controlled"
        and model["controlState"]["coverageComplete"] is True
        and all(obj.get("sourceReference") and obj.get("sourceSha256") for obj in model["objects"])
    )
    pipeline_pass = bool(
        scene_hash_match
        and baseline["summary"]["pipelinePass"]
        and not model_errors
        and all(math.isfinite(row["occludedIlluminanceLux"]) and row["occludedIlluminanceLux"] >= 0 for row in sensor_rows)
    )
    controlled_inputs_ready = bool(
        pipeline_pass
        and baseline["summary"]["directDistributionValidated"]
        and controlled_geometry
        and model["acceptanceCriteria"]["status"] == "released"
    )
    occlusion_completed = bool(controlled_inputs_ready and criteria_pass is True)

    warnings: list[str] = []
    if synthetic:
        warnings.append("Synthetic obstruction geometry validates L2 ray/attenuation software only and is not product photometry evidence.")
    if not scene_hash_match:
        warnings.append("Bound L1 system scene SHA-256 does not match the current file bytes.")
    if not controlled_geometry and not synthetic:
        warnings.append("Reviewed obstruction geometry and direct-transmission assumptions are not fully controlled.")
    if model["acceptanceCriteria"]["status"] != "released":
        warnings.append("Occlusion acceptance criteria are not released; L2 cannot be marked complete.")
    warnings.extend(model_errors)

    losses = [row["lossFraction"] for row in sensor_rows]
    return {
        "$schema": "../../../schemas/aether-photometry-occlusion-report.schema.json",
        "schemaVersion": "1.0.0",
        "fixtureId": FIXTURE_ID,
        "designRevision": DESIGN_REVISION,
        "authority": "derived-occlusion-review",
        "status": "occlusion-layer-pass" if occlusion_completed else ("pipeline-pass" if pipeline_pass else "pipeline-fail"),
        "sourceClass": "synthetic-test-only" if synthetic else "controlled-review-input",
        "bindings": {
            "modelPath": str(model_path),
            "modelSha256": sha256_file(model_path),
            "systemScenePath": model["bindings"]["systemScenePath"],
            "systemSceneSha256": model["bindings"]["systemSceneSha256"],
            "systemSceneHashMatch": scene_hash_match,
        },
        "baseline": {
            "systemStatus": baseline["status"],
            "pipelinePass": baseline["summary"]["pipelinePass"],
            "directDistributionValidated": baseline["summary"]["directDistributionValidated"],
            "headCount": baseline["summary"]["headCount"],
            "sensorCount": baseline["summary"]["sensorCount"],
        },
        "model": {
            "coordinateSystem": model["coordinateSystem"],
            "objects": object_rows,
            "objectCount": len(object_rows),
            "triangleCount": sum(row["triangleCount"] for row in object_rows),
            "rayObjectIntersectionCount": total_hit_count,
            "controlledGeometryReady": controlled_geometry,
        },
        "occlusionLayer": {
            "method": "open-segment Moller-Trumbore triangle intersection; each intersected object applies its controlled direct-transmission factor once per head-to-sensor ray",
            "limitations": [
                "Scalar direct-transmission factors do not model refraction, angular scattering, caustics or wavelength dependence.",
                "A transparent butterfly may require a more complete optical model before the controlled product L2 gate can close.",
                "The model evaluates direct source-to-sensor paths only; interreflection remains L3.",
            ],
            "sensors": sensor_rows,
            "acceptance": {
                "status": model["acceptanceCriteria"]["status"],
                "criteriaPass": criteria_pass,
                "results": criteria_rows,
            },
        },
        "summary": {
            "pipelinePass": pipeline_pass,
            "controlledInputsReady": controlled_inputs_ready,
            "maximumLossFraction": max(losses) if losses else None,
            "averageLossFraction": sum(losses) / len(losses) if losses else None,
            "occlusionAssessmentCompleted": occlusion_completed,
            "reflectanceAssessmentCompletedWhereRequired": False,
            "toleranceSensitivityValidated": False,
            "full14HeadPhotometricValidationCompleted": False,
            "applicationPerformanceValidated": False,
            "productPhotometryApproved": False,
        },
        "warnings": warnings,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the VX4800 L2 direct-path occlusion layer")
    parser.add_argument("model", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate_occlusion(args.model.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Occlusion report: {args.output}")
    print(f"Status: {report['status']}")
    print(f"Pipeline pass: {report['summary']['pipelinePass']}")
    print(f"Occlusion assessment completed: {report['summary']['occlusionAssessmentCompleted']}")
    print(f"Product photometry approved: {report['summary']['productPhotometryApproved']}")
    return 0 if report["summary"]["pipelinePass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
