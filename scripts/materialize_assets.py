from __future__ import annotations

from pathlib import Path
import base64
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/vx4800/fixture.json"
ASSET = ROOT / "fixtures/vx4800/presentation/v5.2.0/assets/architectural-background.webp"
ASSET_ID = "presentation-background-5.2.0"
CHUNK_GLOB = ".architectural-background.webp.b64.*"


def _expected_sha256() -> str:
    fixture = json.loads(FIXTURE.read_text())
    matches = [item for item in fixture.get("assets", []) if item.get("id") == ASSET_ID]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one fixture asset record for {ASSET_ID!r}, found {len(matches)}")
    digest = matches[0].get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError(f"Fixture asset {ASSET_ID!r} has no valid SHA-256")
    return digest.lower()


def _chunk_number(path: Path) -> int:
    suffix = path.name.rsplit(".", 1)[-1]
    if not suffix.isdigit():
        raise ValueError(f"Asset chunk has non-numeric suffix: {path.name}")
    return int(suffix)


def _ordered_chunks() -> list[Path]:
    chunks = list(ASSET.parent.glob(CHUNK_GLOB))
    if not chunks:
        raise FileNotFoundError(f"Missing {ASSET} and recovery chunks {CHUNK_GLOB}")

    numbered = sorted(((_chunk_number(path), path) for path in chunks), key=lambda item: item[0])
    numbers = [number for number, _ in numbered]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"Duplicate numeric asset chunk suffixes: {numbers}")
    expected = list(range(len(numbers)))
    if numbers != expected:
        raise ValueError(f"Asset chunks must be contiguous from 0; found {numbers}, expected {expected}")
    return [path for _, path in numbered]


def _verify_asset_bytes(data: bytes, expected_sha256: str) -> None:
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_sha256:
        raise ValueError(
            f"Reassembled asset SHA-256 mismatch for {ASSET.name}: expected {expected_sha256}, got {actual}"
        )


def materialize_background() -> Path:
    expected_sha256 = _expected_sha256()
    if ASSET.exists():
        _verify_asset_bytes(ASSET.read_bytes(), expected_sha256)
        return ASSET

    chunks = _ordered_chunks()
    encoded = "".join("".join(path.read_text(encoding="ascii").split()) for path in chunks)
    data = base64.b64decode(encoded, validate=True)
    _verify_asset_bytes(data, expected_sha256)
    ASSET.write_bytes(data)
    return ASSET


if __name__ == "__main__":
    print(materialize_background())
