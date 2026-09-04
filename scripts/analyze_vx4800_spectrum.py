#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

FIXTURE_ID = "vx4800-bf-01"
PRODUCT_MIN_NM = 380.0
PRODUCT_MAX_NM = 780.0
PRODUCT_MAX_STEP_NM = 5.0


class SpectralValidationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_spd_csv(path: Path) -> tuple[list[float], list[float]]:
    wavelengths: list[float] = []
    powers: list[float] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise SpectralValidationError("SPD CSV must have a header")
        normalized = {name.strip().lower(): name for name in reader.fieldnames}
        wavelength_key = normalized.get("wavelength_nm") or normalized.get("wavelength")
        power_key = normalized.get("power") or normalized.get("relative_power")
        if wavelength_key is None or power_key is None:
            raise SpectralValidationError(
                "SPD CSV requires wavelength_nm (or wavelength) and power (or relative_power) columns"
            )
        for row_number, row in enumerate(reader, start=2):
            try:
                wavelength = float(row[wavelength_key])
                power = float(row[power_key])
            except (TypeError, ValueError) as exc:
                raise SpectralValidationError(f"invalid numeric SPD value on row {row_number}") from exc
            if power < 0:
                raise SpectralValidationError(f"negative spectral power on row {row_number}")
            wavelengths.append(wavelength)
            powers.append(power)

    if len(wavelengths) < 2:
        raise SpectralValidationError("SPD requires at least two wavelength samples")
    if any(b <= a for a, b in zip(wavelengths, wavelengths[1:])):
        raise SpectralValidationError("SPD wavelengths must be strictly increasing")
    if max(powers) <= 0:
        raise SpectralValidationError("SPD must contain positive spectral power")
    return wavelengths, powers


def maximum_step(wavelengths: Iterable[float]) -> float:
    values = list(wavelengths)
    return max(b - a for a, b in zip(values, values[1:]))


def validate_product_sampling(wavelengths: list[float]) -> None:
    if wavelengths[0] > PRODUCT_MIN_NM or wavelengths[-1] < PRODUCT_MAX_NM:
        raise SpectralValidationError(
            f"product SPD must cover at least {PRODUCT_MIN_NM:.0f}-{PRODUCT_MAX_NM:.0f} nm"
        )
    step = maximum_step(wavelengths)
    if step > PRODUCT_MAX_STEP_NM + 1e-9:
        raise SpectralValidationError(
            f"product SPD maximum wavelength step {step:g} nm exceeds AETHERIA precondition {PRODUCT_MAX_STEP_NM:g} nm"
        )


def xy_to_uv1960(x: float, y: float) -> tuple[float, float]:
    denominator = -2.0 * x + 12.0 * y + 3.0
    if abs(denominator) < 1e-15:
        raise SpectralValidationError("cannot convert degenerate xy chromaticity to CIE 1960 UCS")
    return 4.0 * x / denominator, 6.0 * y / denominator


def compute_metrics(sd) -> dict[str, float]:
    import colour
    import numpy as np

    cri = colour.colour_rendering_index(sd, additional_data=True, method="CIE 1995")
    cie_rf = colour.colour_fidelity_index(sd, additional_data=False, method="CIE 2017")
    tm30 = colour.colour_fidelity_index(
        sd, additional_data=True, method="ANSI/IES TM-30-18"
    )

    xyz = np.asarray(colour.sd_to_XYZ(sd), dtype=float)
    total = float(np.sum(xyz))
    if total <= 0:
        raise SpectralValidationError("SPD produced non-positive XYZ tristimulus sum")
    x = float(xyz[0] / total)
    y = float(xyz[1] / total)
    u, v = xy_to_uv1960(x, y)
    cct, duv = colour.uv_to_CCT(np.array([u, v]), method="Ohno 2013")

    return {
        "cctK": float(cct),
        "duv": float(duv),
        "criRa": float(cri.Q_a),
        "criR9": float(cri.Q_as[9].Q_a),
        "cie2017Rf": float(cie_rf),
        "tm3018Rf": float(tm30.R_f),
        "tm3018Rg": float(tm30.R_g),
    }


def make_synthetic_blackbody(temperature_k: float):
    import colour

    if temperature_k <= 0:
        raise SpectralValidationError("synthetic blackbody temperature must be positive")
    shape = colour.SpectralShape(PRODUCT_MIN_NM, PRODUCT_MAX_NM, PRODUCT_MAX_STEP_NM)
    sd = colour.sd_blackbody(float(temperature_k), shape=shape)
    sd.name = f"AETHERIA synthetic blackbody {temperature_k:g} K"
    wavelengths = [float(value) for value in sd.wavelengths]
    return sd, wavelengths


def make_file_spectrum(path: Path):
    import colour

    wavelengths, powers = load_spd_csv(path)
    sd = colour.SpectralDistribution(dict(zip(wavelengths, powers)), name=path.name)
    return sd, wavelengths


def build_report(args: argparse.Namespace) -> dict:
    import colour

    if args.synthetic_blackbody is not None:
        if args.spd_csv is not None:
            raise SpectralValidationError("choose either --synthetic-blackbody or --spd-csv, not both")
        if args.source_class != "synthetic-test-only":
            raise SpectralValidationError("synthetic mode requires --source-class synthetic-test-only")
        sd, wavelengths = make_synthetic_blackbody(args.synthetic_blackbody)
        source_hash = None
        source_description = f"generated Planckian radiator {args.synthetic_blackbody:g} K"
        exact_spd = False
    else:
        if args.spd_csv is None:
            raise SpectralValidationError("--spd-csv or --synthetic-blackbody is required")
        if args.source_class == "synthetic-test-only":
            raise SpectralValidationError("file mode requires supplier or laboratory source class")
        path = args.spd_csv.resolve()
        if not path.is_file():
            raise SpectralValidationError(f"SPD file not found: {path}")
        sd, wavelengths = make_file_spectrum(path)
        validate_product_sampling(wavelengths)
        source_hash = sha256_file(path)
        if not args.expected_sha256:
            raise SpectralValidationError("product-source SPD requires --expected-sha256")
        if source_hash.lower() != args.expected_sha256.lower():
            raise SpectralValidationError(
                f"SPD SHA-256 mismatch: expected {args.expected_sha256.lower()}, got {source_hash.lower()}"
            )
        source_description = str(path)
        exact_spd = True

    metrics = compute_metrics(sd)
    max_step = maximum_step(wavelengths)
    supplier_or_lab = args.source_class in {"supplier", "laboratory"}
    exact_configuration = bool(args.configuration_controlled and args.configuration_id)
    spectral_eligible = bool(exact_spd and supplier_or_lab and exact_configuration)
    tm3024_controlled = bool(args.tm30_24_primary_ref and supplier_or_lab and exact_configuration)

    return {
        "schemaVersion": "1.0.0",
        "fixtureId": FIXTURE_ID,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": {
            "sourceClass": args.source_class,
            "description": source_description,
            "sha256": source_hash,
            "coverageNm": [float(wavelengths[0]), float(wavelengths[-1])],
            "maximumStepNm": float(max_step),
        },
        "configuration": {
            "configurationId": args.configuration_id,
            "controlled": exact_configuration,
        },
        "toolchain": {
            "package": "colour-science",
            "version": str(colour.__version__),
        },
        "methods": {
            "cri": "CIE 1995",
            "cieFidelity": "CIE 2017",
            "cctDuv": "Ohno 2013 independent cross-check",
            "tm30Compatibility": "ANSI/IES TM-30-18",
            "currentTm30Authority": "ANSI/IES TM-30-24",
        },
        "metrics": metrics,
        "eligibility": {
            "exactSpdControlled": exact_spd,
            "exactConfigurationControlled": exact_configuration,
            "supplierOrLabSource": supplier_or_lab,
            "spectralEvidenceEligible": spectral_eligible,
            "tm3024PrimaryEvidenceControlled": tm3024_controlled,
            "productPhotometryApproved": False,
        },
        "primaryEvidenceReference": args.tm30_24_primary_ref,
        "notes": [
            "TM-30-18 compatibility values are not TM-30-24 product results.",
            "Ohno 2013 CCT/Duv is an independent cross-check and is not labelled ANSI/IES TM-40-24 output.",
            "This script never sets productPhotometryApproved=true; product approval remains a controlled repository release decision.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze VX4800 spectral colour-quality evidence")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--spd-csv", type=Path)
    source.add_argument("--synthetic-blackbody", type=float)
    parser.add_argument(
        "--source-class",
        choices=["synthetic-test-only", "supplier", "laboratory"],
        required=True,
    )
    parser.add_argument("--expected-sha256")
    parser.add_argument("--configuration-id")
    parser.add_argument("--configuration-controlled", action="store_true")
    parser.add_argument("--tm30-24-primary-ref")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
