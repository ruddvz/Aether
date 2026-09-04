#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.photometry.ies_lm63 import ParsedIES, parse_ies

FIXTURE_ID = "vx4800-bf-01"
DESIGN_REVISION = "1.3.0"
ROLE_QUANTITIES = {
    "deep-tail narrow": 4,
    "mid-field spot": 6,
    "upper-field flood": 4,
}


class SystemValidationError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def dot(a: Iterable[float], b: Iterable[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


def cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def norm(v: Iterable[float]) -> float:
    return math.sqrt(dot(v, v))


def unit(v: Iterable[float]) -> list[float]:
    values = [float(x) for x in v]
    length = norm(values)
    if length <= 1e-12:
        raise SystemValidationError("zero-length vector is not permitted")
    return [x / length for x in values]


def subtract(a: Iterable[float], b: Iterable[float]) -> list[float]:
    return [float(x) - float(y) for x, y in zip(a, b)]


def scale(v: Iterable[float], factor: float) -> list[float]:
    return [float(x) * factor for x in v]


def interpolate_1d(angles: list[float], values: list[float], angle: float) -> float:
    if len(angles) != len(values) or not angles:
        raise SystemValidationError("invalid interpolation arrays")
    if angle < angles[0] - 1e-9 or angle > angles[-1] + 1e-9:
        return 0.0
    for idx, known in enumerate(angles):
        if abs(angle - known) <= 1e-9:
            return float(values[idx])
        if known > angle:
            a0, a1 = angles[idx - 1], known
            v0, v1 = values[idx - 1], values[idx]
            t = (angle - a0) / (a1 - a0)
            return float(v0 + t * (v1 - v0))
    return float(values[-1])


def reduce_horizontal_angle(horizontal_angles: list[float], angle_deg: float) -> float:
    if not horizontal_angles:
        raise SystemValidationError("IES contains no horizontal angles")
    if len(horizontal_angles) == 1:
        return float(horizontal_angles[0])
    if abs(horizontal_angles[0]) > 1e-6:
        raise SystemValidationError(
            "initial system validator requires horizontal photometry to begin at 0 degrees; review this source before use"
        )

    phi = angle_deg % 360.0
    last = float(horizontal_angles[-1])
    if last <= 90.0 + 1e-6:
        reduced = phi % 180.0
        if reduced > 90.0:
            reduced = 180.0 - reduced
    elif last <= 180.0 + 1e-6:
        reduced = phi
        if reduced > 180.0:
            reduced = 360.0 - reduced
    elif last >= 359.0:
        reduced = phi
    else:
        raise SystemValidationError(
            f"horizontal coverage 0..{last:g} degrees is ambiguous for the initial system validator"
        )
    if reduced > last + 1e-6:
        raise SystemValidationError(f"reduced horizontal angle {reduced:g} exceeds source coverage {last:g}")
    return min(max(reduced, horizontal_angles[0]), last)


def candela_at(parsed: ParsedIES, vertical_deg: float, horizontal_deg: float) -> float:
    if parsed.photometric_type != 1:
        raise SystemValidationError(
            f"initial 14-head system validator supports LM-63 Type C photometry only; received type {parsed.photometric_type}"
        )
    if vertical_deg < parsed.vertical_angles[0] - 1e-9 or vertical_deg > parsed.vertical_angles[-1] + 1e-9:
        return 0.0
    if len(parsed.horizontal_angles) == 1:
        return interpolate_1d(parsed.vertical_angles, parsed.candela[0], vertical_deg)

    reduced = reduce_horizontal_angle(parsed.horizontal_angles, horizontal_deg)
    for idx, known in enumerate(parsed.horizontal_angles):
        if abs(reduced - known) <= 1e-9:
            return interpolate_1d(parsed.vertical_angles, parsed.candela[idx], vertical_deg)
        if known > reduced:
            h0, h1 = parsed.horizontal_angles[idx - 1], known
            c0 = interpolate_1d(parsed.vertical_angles, parsed.candela[idx - 1], vertical_deg)
            c1 = interpolate_1d(parsed.vertical_angles, parsed.candela[idx], vertical_deg)
            t = (reduced - h0) / (h1 - h0)
            return float(c0 + t * (c1 - c0))
    return interpolate_1d(parsed.vertical_angles, parsed.candela[-1], vertical_deg)


def orientation_basis(aim_direction: list[float], roll_deg: float) -> tuple[list[float], list[float], list[float]]:
    w = unit(aim_direction)
    reference = [1.0, 0.0, 0.0]
    if abs(dot(reference, w)) > 0.95:
        reference = [0.0, 1.0, 0.0]
    projected = subtract(reference, scale(w, dot(reference, w)))
    u0 = unit(projected)
    v0 = unit(cross(w, u0))
    angle = math.radians(float(roll_deg))
    u = [math.cos(angle) * u0[i] + math.sin(angle) * v0[i] for i in range(3)]
    v = unit(cross(w, u))
    return unit(u), v, w


def source_angles(head: dict, direction_from_head: list[float]) -> tuple[float, float]:
    u, v, w = orientation_basis(head["aimDirection"], head["rollDeg"])
    d = unit(direction_from_head)
    cosine = max(-1.0, min(1.0, dot(w, d)))
    vertical = math.degrees(math.acos(cosine))
    horizontal = math.degrees(math.atan2(dot(d, v), dot(d, u))) % 360.0
    return vertical, horizontal


def read_led_setout(path: Path) -> dict[str, tuple[float, float]]:
    rows: dict[str, tuple[float, float]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows[row["led_id"]] = (float(row["x_mm"]) / 1000.0, float(row["y_mm"]) / 1000.0)
    return rows


def check_setout(scene: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    bindings = scene["bindings"]
    setout_path = resolve_repo_path(bindings["ledSetoutPath"])
    if not setout_path.is_file():
        raise SystemValidationError(f"controlled LED setout not found: {setout_path}")
    actual_sha = sha256_file(setout_path)
    if actual_sha != bindings["ledSetoutSha256"]:
        errors.append("scene LED setout SHA-256 does not match the controlled file bytes")

    setout = read_led_setout(setout_path)
    heads = scene["heads"]
    if len(setout) != 14 or len(heads) != 14:
        errors.append("VX4800 system validation requires exactly 14 setout rows and 14 scene heads")
    head_by_id = {head["ledId"]: head for head in heads}
    if set(head_by_id) != set(setout):
        errors.append("scene head IDs do not exactly match the controlled LED setout IDs")
    for led_id, (x_m, y_m) in setout.items():
        head = head_by_id.get(led_id)
        if not head:
            continue
        px, py, _ = head["positionM"]
        if abs(float(px) - x_m) > 1e-6 or abs(float(py) - y_m) > 1e-6:
            errors.append(f"{led_id} XY position does not match controlled engineering setout")
    return not errors, errors


def check_role_counts(scene: dict) -> tuple[bool, dict[str, int]]:
    counts = {role: 0 for role in ROLE_QUANTITIES}
    for head in scene["heads"]:
        role = head["role"]
        if role in counts:
            counts[role] += 1
        else:
            counts[role] = counts.get(role, 0) + 1
    return counts == ROLE_QUANTITIES, counts


def load_sources(scene: dict) -> tuple[dict[str, ParsedIES], list[dict], list[str]]:
    parsed_by_role: dict[str, ParsedIES] = {}
    source_rows: list[dict] = []
    errors: list[str] = []
    seen_roles: set[str] = set()

    for source in scene["sources"]:
        role = source["role"]
        if role in seen_roles:
            errors.append(f"duplicate source role: {role}")
            continue
        seen_roles.add(role)
        path = resolve_repo_path(source["iesPath"])
        if not path.is_file():
            raise SystemValidationError(f"IES source not found for {role}: {path}")
        actual_sha = sha256_file(path)
        if actual_sha != source["iesSha256"]:
            errors.append(f"{role} IES SHA-256 does not match scene binding")
        parsed = parse_ies(path)
        if parsed.sha256 != actual_sha:
            errors.append(f"{role} parser integrity SHA-256 mismatch")
        if parsed.photometric_type != 1:
            errors.append(f"{role} source is not LM-63 Type C")
        parsed_by_role[role] = parsed
        source_rows.append(
            {
                "role": role,
                "configurationId": source["configurationId"],
                "iesPath": source["iesPath"],
                "iesSha256": actual_sha,
                "provenanceStatus": source["provenanceStatus"],
                "syntheticTest": source["syntheticTest"],
                "photometricType": parsed.photometric_type,
                "horizontalPlaneCount": len(parsed.horizontal_angles),
                "verticalAngleCount": len(parsed.vertical_angles),
            }
        )
    if set(parsed_by_role) != set(ROLE_QUANTITIES):
        errors.append("scene must bind exactly one IES source for each of the three controlled optical roles")
    return parsed_by_role, source_rows, errors


def check_controlled_role_set(scene: dict, source_rows: list[dict]) -> tuple[bool, list[str], dict | None]:
    errors: list[str] = []
    if scene["authority"] == "synthetic-pipeline-test":
        return False, errors, None

    role_set_path_value = scene["bindings"].get("roleSetPath")
    role_set_sha = scene["bindings"].get("roleSetSha256")
    if not role_set_path_value or not role_set_sha:
        return False, ["controlled system review requires roleSetPath and roleSetSha256"], None
    role_set_path = resolve_repo_path(role_set_path_value)
    if not role_set_path.is_file():
        raise SystemValidationError(f"role set not found: {role_set_path}")
    if sha256_file(role_set_path) != role_set_sha:
        errors.append("role-set SHA-256 does not match scene binding")
    role_set = load_json(role_set_path)
    if role_set.get("status") != "eligible-for-system-validation":
        errors.append("role set is not eligible-for-system-validation")
    if not role_set.get("eligibility", {}).get("roleSetEligibleForSystemValidation"):
        errors.append("role-set eligibility gate is false")
    if role_set.get("eligibility", {}).get("productPhotometryApproved") is not False:
        errors.append("role-set input must not claim product approval")

    role_entries = {entry["role"]: entry for entry in role_set.get("roles", [])}
    sources = {entry["role"]: entry for entry in source_rows}
    for role in ROLE_QUANTITIES:
        role_entry = role_entries.get(role)
        source = sources.get(role)
        if not role_entry or not source:
            errors.append(f"missing controlled role/source binding for {role}")
            continue
        if source["configurationId"] != role_entry.get("configurationId"):
            errors.append(f"{role} configurationId differs from role-set package")
        package_path_value = role_entry.get("evidencePackagePath")
        if not package_path_value:
            errors.append(f"{role} role-set entry lacks evidencePackagePath")
            continue
        package_path = resolve_repo_path(package_path_value)
        if not package_path.is_file():
            errors.append(f"{role} evidence package path does not resolve")
            continue
        package = load_json(package_path)
        angular = package.get("angular", {})
        if angular.get("iesSha256") != source["iesSha256"]:
            errors.append(f"{role} scene IES hash differs from exact evidence package")
        if angular.get("iesFilename") != Path(source["iesPath"]).name:
            errors.append(f"{role} scene IES filename differs from exact evidence package")
        if source["provenanceStatus"] not in {"supplier", "laboratory"} or source["syntheticTest"]:
            errors.append(f"{role} controlled system review requires supplier/laboratory non-synthetic source")
    return not errors, errors, role_set


def contribution(head: dict, sensor: dict, parsed: ParsedIES) -> dict:
    ray = subtract(sensor["pointM"], head["positionM"])
    distance = norm(ray)
    if distance <= 1e-9:
        raise SystemValidationError(f"sensor {sensor['sensorId']} coincides with head {head['ledId']}")
    direction = scale(ray, 1.0 / distance)
    normal = unit(sensor["normal"])
    incidence = max(0.0, dot(normal, scale(direction, -1.0)))
    vertical, horizontal = source_angles(head, direction)
    intensity = candela_at(parsed, vertical, horizontal)
    lux = float(head["outputScale"]) * intensity * incidence / (distance * distance)
    return {
        "ledId": head["ledId"],
        "role": head["role"],
        "distanceM": distance,
        "verticalAngleDeg": vertical,
        "horizontalAngleDeg": horizontal,
        "candela": intensity,
        "incidenceCosine": incidence,
        "outputScale": float(head["outputScale"]),
        "illuminanceLux": lux,
    }


def evaluate_criteria(criteria: dict, sensor_results: list[dict]) -> tuple[bool | None, list[dict]]:
    if criteria["status"] != "released":
        return None, []
    by_id = {entry["sensorId"]: entry for entry in sensor_results}
    rows: list[dict] = []
    all_pass = True
    for rule in criteria["sensorLimits"]:
        sensor_id = rule["sensorId"]
        if sensor_id not in by_id:
            raise SystemValidationError(f"released criterion references unknown sensor: {sensor_id}")
        value = float(by_id[sensor_id]["totalIlluminanceLux"])
        minimum = rule.get("minimumLux")
        maximum = rule.get("maximumLux")
        passed = True
        if minimum is not None:
            passed = passed and value >= float(minimum)
        if maximum is not None:
            passed = passed and value <= float(maximum)
        all_pass = all_pass and passed
        rows.append(
            {
                "sensorId": sensor_id,
                "measuredLux": value,
                "minimumLux": minimum,
                "maximumLux": maximum,
                "pass": passed,
            }
        )
    return all_pass, rows


def validate_system(scene_path: Path) -> dict:
    scene = load_json(scene_path)
    if scene.get("fixtureId") != FIXTURE_ID or scene.get("designRevision") != DESIGN_REVISION:
        raise SystemValidationError("scene identity does not match controlled VX4800 design revision")

    setout_ok, setout_errors = check_setout(scene)
    roles_ok, role_counts = check_role_counts(scene)
    parsed_by_role, source_rows, source_errors = load_sources(scene)
    controlled_role_set_ok, role_set_errors, role_set = check_controlled_role_set(scene, source_rows)

    synthetic = scene["authority"] == "synthetic-pipeline-test"
    synthetic_sources_ok = all(row["syntheticTest"] and row["provenanceStatus"] == "synthetic-test" for row in source_rows)
    if synthetic and not synthetic_sources_ok:
        source_errors.append("synthetic pipeline scene may use only synthetic-test sources")

    sensor_results: list[dict] = []
    for sensor in scene["sensors"]:
        rows = [contribution(head, sensor, parsed_by_role[head["role"]]) for head in scene["heads"]]
        total = sum(row["illuminanceLux"] for row in rows)
        sensor_results.append(
            {
                "sensorId": sensor["sensorId"],
                "category": sensor["category"],
                "pointM": sensor["pointM"],
                "normal": sensor["normal"],
                "totalIlluminanceLux": total,
                "contributions": rows,
            }
        )

    criteria_pass, criteria_rows = evaluate_criteria(scene["acceptanceCriteria"], sensor_results)
    values = [float(row["totalIlluminanceLux"]) for row in sensor_results]
    finite = bool(values) and all(math.isfinite(value) and value >= 0.0 for value in values)
    pipeline_pass = finite and setout_ok and roles_ok and not source_errors

    controls = scene["controlState"]
    controlled_inputs = (
        scene["authority"] == "controlled-system-review-input"
        and scene["status"] == "controlled"
        and controlled_role_set_ok
        and controls["headPositions"] == "controlled"
        and controls["headRoles"] == "controlled"
        and controls["headAiming"] == "controlled"
        and controls["sensorDefinitions"] == "controlled"
        and controls["acceptanceCriteria"] == "released"
        and scene["acceptanceCriteria"]["status"] == "released"
        and all(row["provenanceStatus"] in {"supplier", "laboratory"} and not row["syntheticTest"] for row in source_rows)
    )
    direct_validated = bool(pipeline_pass and controlled_inputs and criteria_pass is True)

    warnings: list[str] = []
    if synthetic:
        warnings.append("Synthetic 14-head scene validates software aggregation only and is not product photometry evidence.")
    if not controlled_role_set_ok and not synthetic:
        warnings.append("Exact three-role evidence set is not controlled; direct product validation remains false.")
    if scene["acceptanceCriteria"]["status"] != "released":
        warnings.append("Acceptance criteria are not released; computed lux values cannot be promoted to a pass/fail product claim.")
    warnings.extend(setout_errors + source_errors + role_set_errors)

    role_set_binding = None
    if role_set is not None:
        role_set_binding = {
            "path": scene["bindings"]["roleSetPath"],
            "sha256": scene["bindings"]["roleSetSha256"],
            "status": role_set.get("status"),
        }

    return {
        "$schema": "../../../schemas/aether-photometry-system-report.schema.json",
        "schemaVersion": "1.0.0",
        "fixtureId": FIXTURE_ID,
        "designRevision": DESIGN_REVISION,
        "authority": "derived-system-review",
        "status": "direct-layer-pass" if direct_validated else ("pipeline-pass" if pipeline_pass else "pipeline-fail"),
        "sourceClass": "synthetic-test-only" if synthetic else "controlled-review-input",
        "scene": {
            "path": str(scene_path),
            "sha256": sha256_file(scene_path),
            "coordinateSystem": scene["coordinateSystem"],
            "roleSet": role_set_binding,
            "ledSetoutPath": scene["bindings"]["ledSetoutPath"],
            "ledSetoutSha256": scene["bindings"]["ledSetoutSha256"],
        },
        "inputChecks": {
            "setoutShaAndPositionsMatch": setout_ok,
            "controlledRoleQuantitiesMatch": roles_ok,
            "roleCounts": role_counts,
            "sourceIntegrityPass": not source_errors,
            "exactRoleSetControlled": controlled_role_set_ok,
            "syntheticSourcesOnlyWhenSynthetic": synthetic_sources_ok if synthetic else True,
            "allPipelineInputChecksPass": pipeline_pass,
        },
        "sources": source_rows,
        "directLayer": {
            "method": "sum per-head LM-63 Type C candela at each sensor using inverse-square distance and sensor incidence cosine",
            "coordinateConvention": "x/y horizontal; z positive downward; each head zero-degree axis follows aimDirection; rollDeg sets the C0 reference plane",
            "sensors": sensor_results,
            "acceptance": {
                "status": scene["acceptanceCriteria"]["status"],
                "criteriaPass": criteria_pass,
                "results": criteria_rows,
            },
        },
        "summary": {
            "pipelinePass": pipeline_pass,
            "headCount": len(scene["heads"]),
            "sensorCount": len(sensor_results),
            "minimumLux": min(values) if values else None,
            "maximumLux": max(values) if values else None,
            "averageLux": sum(values) / len(values) if values else None,
            "controlledInputsReady": controlled_inputs,
            "acceptanceCriteriaReleased": scene["acceptanceCriteria"]["status"] == "released",
            "directDistributionValidated": direct_validated,
            "occlusionAssessmentCompleted": False,
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
    parser = argparse.ArgumentParser(description="Validate the VX4800 14-head direct photometric system layer")
    parser.add_argument("scene", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = validate_system(args.scene.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"System photometry report: {args.output}")
    print(f"Status: {report['status']}")
    print(f"Pipeline pass: {report['summary']['pipelinePass']}")
    print(f"Direct distribution validated: {report['summary']['directDistributionValidated']}")
    print(f"Product photometry approved: {report['summary']['productPhotometryApproved']}")
    return 0 if report["summary"]["pipelinePass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
