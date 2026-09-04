"""Small, dependency-free LM-63 ingestion helper for AETHERIA.

It intentionally parses only the standard numeric photometric block plus labels.
The raw IES file remains the controlled source asset. Parsed reports are derived.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable
import math
import re


class IESParseError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedIES:
    version: str
    labels: dict[str, str]
    tilt: str
    number_of_lamps: int
    lumens_per_lamp: float
    candela_multiplier: float
    vertical_angles: list[float]
    horizontal_angles: list[float]
    photometric_type: int
    units_type: int
    width: float
    length: float
    height: float
    ballast_factor: float
    future_use: float
    input_watts: float
    candela: list[list[float]]
    sha256: str
    byte_length: int

    @property
    def max_candela(self) -> tuple[float, float, float]:
        best = (-1.0, 0.0, 0.0)
        for hi, h in enumerate(self.horizontal_angles):
            for vi, v in enumerate(self.vertical_angles):
                cd = self.candela[hi][vi]
                if cd > best[0]:
                    best = (cd, h, v)
        return best


def _tokenize_numeric(lines: Iterable[str]) -> list[float]:
    tokens: list[float] = []
    for line in lines:
        for tok in line.replace(",", " ").split():
            try:
                tokens.append(float(tok))
            except ValueError as exc:
                raise IESParseError(f"Non-numeric token in photometric block: {tok!r}") from exc
    return tokens


def _take(values: list[float], idx: int, count: int, name: str) -> tuple[list[float], int]:
    end = idx + count
    if end > len(values):
        raise IESParseError(f"Unexpected end of file while reading {name}")
    return values[idx:end], end


def parse_ies(path: str | Path) -> ParsedIES:
    p = Path(path)
    raw = p.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    if not lines or not lines[0]:
        raise IESParseError("Empty IES file")

    version = lines[0]
    if not version.upper().startswith("IES"):
        raise IESParseError(f"Unrecognized LM-63 header: {version!r}")

    labels: dict[str, str] = {}
    tilt_index = None
    label_re = re.compile(r"^\[([^\]]+)\]\s*(.*)$")
    for i, line in enumerate(lines[1:], start=1):
        if line.upper().startswith("TILT="):
            tilt_index = i
            break
        m = label_re.match(line)
        if m:
            labels[m.group(1).strip().upper()] = m.group(2).strip()

    if tilt_index is None:
        raise IESParseError("Missing TILT= line")

    tilt = lines[tilt_index].split("=", 1)[1].strip().upper()
    if tilt != "NONE":
        raise IESParseError(
            f"TILT={tilt} is not supported by the initial AETHERIA ingestor; preserve the raw file and add a reviewed tilt parser before use"
        )

    values = _tokenize_numeric(lines[tilt_index + 1 :])
    if len(values) < 13:
        raise IESParseError("Incomplete LM-63 numeric header")

    i = 0
    number_of_lamps = int(values[i]); i += 1
    lumens_per_lamp = values[i]; i += 1
    candela_multiplier = values[i]; i += 1
    nv = int(values[i]); i += 1
    nh = int(values[i]); i += 1
    photometric_type = int(values[i]); i += 1
    units_type = int(values[i]); i += 1
    width, length, height = values[i:i+3]; i += 3
    ballast_factor, future_use, input_watts = values[i:i+3]; i += 3

    if nv <= 0 or nh <= 0:
        raise IESParseError("Angle counts must be positive")
    if candela_multiplier <= 0:
        raise IESParseError("Candela multiplier must be positive")

    vertical, i = _take(values, i, nv, "vertical angles")
    horizontal, i = _take(values, i, nh, "horizontal angles")
    flat, i = _take(values, i, nv * nh, "candela values")

    candela: list[list[float]] = []
    for h in range(nh):
        row = [max(0.0, flat[h * nv + v] * candela_multiplier) for v in range(nv)]
        candela.append(row)

    if any(vertical[j] > vertical[j+1] for j in range(len(vertical)-1)):
        raise IESParseError("Vertical angles must be nondecreasing")
    if any(horizontal[j] > horizontal[j+1] for j in range(len(horizontal)-1)):
        raise IESParseError("Horizontal angles must be nondecreasing")

    return ParsedIES(
        version=version,
        labels=labels,
        tilt=tilt,
        number_of_lamps=number_of_lamps,
        lumens_per_lamp=lumens_per_lamp,
        candela_multiplier=candela_multiplier,
        vertical_angles=vertical,
        horizontal_angles=horizontal,
        photometric_type=photometric_type,
        units_type=units_type,
        width=width,
        length=length,
        height=height,
        ballast_factor=ballast_factor,
        future_use=future_use,
        input_watts=input_watts,
        candela=candela,
        sha256=sha256(raw).hexdigest(),
        byte_length=len(raw),
    )


def infer_symmetry(horizontal_angles: list[float]) -> str:
    if not horizontal_angles:
        return "unknown"
    if len(horizontal_angles) == 1:
        return "single-plane-or-axial"
    span = horizontal_angles[-1] - horizontal_angles[0]
    if span <= 90.0 + 1e-6:
        return "quadrant"
    if span <= 180.0 + 1e-6:
        return "bilateral"
    if span <= 360.0 + 1e-6:
        return "full"
    return "unknown"


def _crossing_angle(angles: list[float], values: list[float], threshold: float, peak_index: int, direction: int) -> float | None:
    i = peak_index
    while 0 <= i + direction < len(values):
        j = i + direction
        a0, a1 = angles[i], angles[j]
        v0, v1 = values[i], values[j]
        if (v0 - threshold) * (v1 - threshold) <= 0 and v0 != v1:
            t = (threshold - v0) / (v1 - v0)
            return a0 + t * (a1 - a0)
        i = j
    return None


def estimate_beam(parsed: ParsedIES, horizontal_plane_index: int = 0) -> dict | None:
    if not parsed.candela:
        return None
    values = parsed.candela[horizontal_plane_index]
    if not values or max(values) <= 0:
        return None
    peak_index = max(range(len(values)), key=values.__getitem__)
    peak = values[peak_index]

    def width_at(frac: float) -> float | None:
        threshold = peak * frac
        left = _crossing_angle(parsed.vertical_angles, values, threshold, peak_index, -1)
        right = _crossing_angle(parsed.vertical_angles, values, threshold, peak_index, 1)
        if left is None and parsed.vertical_angles[peak_index] == 0:
            left = -right if right is not None else None
        if right is None and parsed.vertical_angles[peak_index] == 180:
            right = 360 - left if left is not None else None
        if left is None or right is None:
            return None
        return abs(right - left)

    return {
        "horizontalPlaneDeg": parsed.horizontal_angles[horizontal_plane_index],
        "fullWidthHalfMaximumDeg": width_at(0.5),
        "fieldAngleDeg": width_at(0.1),
        "method": "interpolated-from-candela-relative-to-plane-maximum",
    }


def to_report(parsed: ParsedIES, *, filename: str, provenance_status: str = "unknown", manufacturer: str | None = None,
              model: str | None = None, source_url: str | None = None, received_at: str | None = None,
              notes: str | None = None) -> dict:
    max_cd, h, v = parsed.max_candela
    warnings: list[str] = []
    if parsed.photometric_type not in (1, 2, 3):
        warnings.append(f"Unknown photometric type {parsed.photometric_type}")
    if parsed.units_type not in (1, 2):
        warnings.append(f"Unknown units type {parsed.units_type}")
    if parsed.lumens_per_lamp < 0:
        warnings.append("Negative lumens-per-lamp indicates absolute photometry in some LM-63 workflows; preserve source semantics and verify with supplier")
    if provenance_status in ("unknown", "synthetic-test"):
        warnings.append("This report is not approved product photometry")

    return {
        "schemaVersion": "1.0.0",
        "source": {
            "filename": filename,
            "manufacturer": manufacturer,
            "model": model,
            "provenanceStatus": provenance_status,
            "sourceUrl": source_url,
            "receivedAt": received_at,
            "notes": notes,
        },
        "lm63": {
            "version": parsed.version,
            "tilt": parsed.tilt,
            "numberOfLamps": parsed.number_of_lamps,
            "lumensPerLamp": parsed.lumens_per_lamp,
            "candelaMultiplier": parsed.candela_multiplier,
            "verticalAngleCount": len(parsed.vertical_angles),
            "horizontalAngleCount": len(parsed.horizontal_angles),
            "photometricType": parsed.photometric_type,
            "unitsType": parsed.units_type,
            "width": parsed.width,
            "length": parsed.length,
            "height": parsed.height,
            "ballastFactor": parsed.ballast_factor,
            "futureUse": parsed.future_use,
            "inputWatts": parsed.input_watts,
        },
        "photometry": {
            "verticalAnglesDeg": parsed.vertical_angles,
            "horizontalAnglesDeg": parsed.horizontal_angles,
            "candela": parsed.candela,
            "maxCandela": max_cd,
            "maxCandelaLocation": {"horizontalDeg": h, "verticalDeg": v},
            "symmetry": infer_symmetry(parsed.horizontal_angles),
            "estimatedBeam": estimate_beam(parsed),
        },
        "integrity": {"sha256": parsed.sha256, "byteLength": parsed.byte_length},
        "warnings": warnings,
    }
