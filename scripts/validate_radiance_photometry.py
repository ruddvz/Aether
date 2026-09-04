#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.photometry.ies_lm63 import ParsedIES, parse_ies

TOOLCHAIN_PATH = ROOT / "fixtures/vx4800/photometry/radiance/toolchain-v1.json"


class RadianceValidationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Sample:
    angle_deg: float
    x_m: float
    y_m: float
    z_m: float
    expected_candela: float
    expected_ratio: float


def load_toolchain(path: Path = TOOLCHAIN_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def interpolate(angles: Sequence[float], values: Sequence[float], angle: float) -> float:
    if len(angles) != len(values) or not angles:
        raise ValueError("angles and values must be non-empty and have equal length")
    if angle < angles[0] - 1e-9 or angle > angles[-1] + 1e-9:
        raise ValueError(f"angle {angle} outside available range {angles[0]}..{angles[-1]}")
    for idx, known in enumerate(angles):
        if abs(angle - known) <= 1e-9:
            return float(values[idx])
        if known > angle:
            a0, a1 = angles[idx - 1], known
            v0, v1 = values[idx - 1], values[idx]
            t = (angle - a0) / (a1 - a0)
            return float(v0 + t * (v1 - v0))
    return float(values[-1])


def make_samples(parsed: ParsedIES, angles_deg: Sequence[float], distance_m: float) -> list[Sample]:
    if distance_m <= 0:
        raise ValueError("sampling distance must be positive")
    if not parsed.candela or not parsed.horizontal_angles:
        raise RadianceValidationError("IES contains no candela distribution")

    plane = parsed.candela[0]
    i0 = interpolate(parsed.vertical_angles, plane, 0.0)
    if i0 <= 0:
        raise RadianceValidationError("0-degree reference candela must be positive for this initial cross-check")

    samples: list[Sample] = []
    for angle in angles_deg:
        theta = math.radians(angle)
        candela = interpolate(parsed.vertical_angles, plane, angle)
        ratio = (candela / i0) * (math.cos(theta) ** 3)
        samples.append(
            Sample(
                angle_deg=float(angle),
                x_m=distance_m * math.tan(theta),
                y_m=0.0,
                z_m=-distance_m,
                expected_candela=candela,
                expected_ratio=ratio,
            )
        )
    return samples


def require_executable(name: str) -> str:
    executable = shutil.which(name)
    if not executable:
        raise RadianceValidationError(f"Required Radiance executable not found on PATH: {name}")
    return executable


def run_checked(command: Sequence[str], *, cwd: Path, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        list(command),
        cwd=cwd,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RadianceValidationError(
            f"Command failed ({proc.returncode}): {' '.join(command)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc


def radiance_version(rtrace: str, *, cwd: Path) -> str:
    proc = subprocess.run([rtrace, "-version"], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    text = (proc.stdout + "\n" + proc.stderr).strip()
    return text.splitlines()[0] if text else "unknown"


def parse_rtrace_rgb(stdout: str, expected_rows: int) -> list[tuple[float, float, float]]:
    rows: list[tuple[float, float, float]] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 3:
            raise RadianceValidationError(f"Unexpected rtrace output row: {line!r}")
        rows.append((float(parts[0]), float(parts[1]), float(parts[2])))
    if len(rows) != expected_rows:
        raise RadianceValidationError(f"Expected {expected_rows} rtrace rows, received {len(rows)}")
    return rows


def rgb_scalar(rgb: tuple[float, float, float]) -> float:
    # Relative distribution is what matters here. A positive linear combination
    # cancels the lamp spectrum when all samples use the same converted source.
    return sum(rgb) / 3.0


def relative_error(observed: float, expected: float) -> float:
    if expected == 0:
        return 0.0 if observed == 0 else math.inf
    return abs(observed - expected) / abs(expected)


def validate(
    ies_path: Path,
    out_dir: Path,
    *,
    provenance: str,
    allow_synthetic_test: bool,
    toolchain: dict,
) -> dict:
    if provenance == "synthetic-test" and not allow_synthetic_test:
        raise RadianceValidationError("Synthetic test photometry requires --allow-synthetic-test")

    parsed = parse_ies(ies_path)
    method = toolchain["method"]
    samples = make_samples(parsed, method["defaultAnglesDeg"], float(method["defaultSamplingDistanceM"]))

    ies2rad = require_executable("ies2rad")
    oconv = require_executable("oconv")
    rtrace = require_executable("rtrace")

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = "crosscheck"
    local_ies = out_dir / ies_path.name
    if local_ies.resolve() != ies_path.resolve():
        shutil.copyfile(ies_path, local_ies)

    convert = run_checked([ies2rad, "-o", stem, local_ies.name], cwd=out_dir)
    rad_path = out_dir / f"{stem}.rad"
    dat_path = out_dir / f"{stem}.dat"
    if not rad_path.is_file() or not dat_path.is_file():
        raise RadianceValidationError("ies2rad did not create the expected .rad and .dat files")

    oct_path = out_dir / f"{stem}.oct"
    compiled = run_checked([oconv, rad_path.name], cwd=out_dir)
    oct_path.write_bytes(compiled.stdout.encode("latin-1"))
    # subprocess text mode is unsuitable for an octree. Rebuild in binary mode.
    with oct_path.open("wb") as oct_file:
        proc = subprocess.run([oconv, rad_path.name], cwd=out_dir, stdout=oct_file, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0 or not oct_path.is_file() or oct_path.stat().st_size == 0:
        stderr = proc.stderr.decode(errors="replace") if isinstance(proc.stderr, bytes) else str(proc.stderr)
        raise RadianceValidationError(f"oconv failed to create a non-empty octree: {stderr}")

    sensor_text = "".join(f"{s.x_m:.9f} {s.y_m:.9f} {s.z_m:.9f} 0 0 1\n" for s in samples)
    traced = run_checked(
        [rtrace, "-I+", "-h", "-ov", "-ab", "0", "-dj", "0", "-ds", "0", oct_path.name],
        cwd=out_dir,
        input_text=sensor_text,
    )
    rgb_rows = parse_rtrace_rgb(traced.stdout, len(samples))
    scalars = [rgb_scalar(row) for row in rgb_rows]
    if not scalars or scalars[0] <= 0:
        raise RadianceValidationError("Radiance 0-degree reference irradiance must be positive")

    observed_ratios = [value / scalars[0] for value in scalars]
    tolerance = float(method["relativeTolerance"])
    result_rows: list[dict] = []
    errors: list[float] = []
    for sample, rgb, scalar, observed_ratio in zip(samples, rgb_rows, scalars, observed_ratios):
        error = relative_error(observed_ratio, sample.expected_ratio)
        errors.append(error)
        result_rows.append(
            {
                "angleDeg": sample.angle_deg,
                "pointM": [sample.x_m, sample.y_m, sample.z_m],
                "normal": [0.0, 0.0, 1.0],
                "iesCandela": sample.expected_candela,
                "expectedRelativeIrradiance": sample.expected_ratio,
                "radianceRgbIrradiance": list(rgb),
                "radianceScalar": scalar,
                "observedRelativeIrradiance": observed_ratio,
                "relativeError": error,
                "withinTolerance": error <= tolerance,
            }
        )

    max_error = max(errors) if errors else math.inf
    pipeline_pass = all(math.isfinite(value) for value in scalars) and rad_path.stat().st_size > 0 and dat_path.stat().st_size > 0
    numerical_pass = pipeline_pass and max_error <= tolerance
    is_product_evidence = provenance in {"supplier", "laboratory"}
    product_eligible = is_product_evidence and toolchain["validationBoundary"]["supplierOrLabRawIesRequiredForProductValidation"]

    report = {
        "$schema": "../../../../schemas/aether-radiance-validation-report.schema.json",
        "schemaVersion": "1.0.0",
        "fixtureId": "vx4800-bf-01",
        "status": "validation-pass" if numerical_pass else "validation-fail",
        "authority": "derived-cross-check",
        "source": {
            "filename": ies_path.name,
            "sha256": parsed.sha256,
            "byteLength": parsed.byte_length,
            "provenanceStatus": provenance,
            "syntheticTest": provenance == "synthetic-test",
        },
        "radiance": {
            "expectedRelease": toolchain["radiance"]["release"],
            "expectedTag": toolchain["radiance"]["tag"],
            "runtimeVersion": radiance_version(rtrace, cwd=out_dir),
            "executables": {"ies2rad": ies2rad, "oconv": oconv, "rtrace": rtrace},
        },
        "method": {
            "samplingDistanceM": method["defaultSamplingDistanceM"],
            "anglesDeg": method["defaultAnglesDeg"],
            "relativeTolerance": tolerance,
            "expectedRatioFormula": "E(theta)/E(0) = I(theta)/I(0) * cos(theta)^3 for a horizontal sensor plane at constant vertical offset",
            "horizontalPlaneDeg": parsed.horizontal_angles[0],
        },
        "results": result_rows,
        "summary": {
            "pipelinePass": pipeline_pass,
            "numericalCrossCheckPass": numerical_pass,
            "maxRelativeError": max_error,
            "productPhotometryEligibleForFurtherReview": bool(product_eligible and numerical_pass),
            "productPhotometryApproved": False,
        },
        "commands": {
            "ies2rad": {"stdout": convert.stdout.strip(), "stderr": convert.stderr.strip()},
            "rtrace": {"stderr": traced.stderr.strip()},
        },
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "warnings": [],
    }
    if provenance == "synthetic-test":
        report["warnings"].append("Synthetic test IES validates the Radiance pipeline only and is not product photometry evidence.")
    if provenance not in {"supplier", "laboratory"}:
        report["warnings"].append("Product validation requires controlled raw supplier or laboratory IES provenance.")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-check an LM-63 file using the independent Radiance toolchain")
    parser.add_argument("ies", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--provenance", choices=["supplier", "laboratory", "unknown", "synthetic-test"], default="unknown")
    parser.add_argument("--allow-synthetic-test", action="store_true")
    args = parser.parse_args()

    toolchain = load_toolchain()
    report = validate(args.ies.resolve(), args.out.resolve(), provenance=args.provenance, allow_synthetic_test=args.allow_synthetic_test, toolchain=toolchain)
    report_path = args.out / "radiance-validation.report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Radiance report: {report_path}")
    print(f"Status: {report['status']}")
    print(f"Max relative error: {report['summary']['maxRelativeError']:.6f}")
    print(f"Product photometry approved: {report['summary']['productPhotometryApproved']}")
    return 0 if report["summary"]["numericalCrossCheckPass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
