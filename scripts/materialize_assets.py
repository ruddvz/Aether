from __future__ import annotations

from pathlib import Path
import base64
import hashlib

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "fixtures/vx4800/presentation/v5.2.0/assets/architectural-background.webp"
CHUNK_GLOB = ".architectural-background.webp.b64.*"
EXPECTED_ASSET_BYTES = 18_988
EXPECTED_CHUNK_GIT_SHA1 = {
    0: "e64431e3faccf605ee09d13aecd05ecea5fec9f9",
    1: "e4335c41070afea2bb7126f11abe90642e605ff8",
    2: "fcaa8ceb5eebf4f4d219f4e4cc645a4825891b8a",
    3: "bae87f356b6469c35c65ff1355ff08d1e88eafb0",
    4: "ac34cb2f962c5e4ab9b2021e0409cefbd3612af0",
    5: "f93514a9ca9f63a7da582067ddb4d17d4daee2e9",
    6: "3082f02fc4099e9d0765ce968c9e0067c601e0bb",
    7: "bd03e8ada47fb0984fb3ffb12cdeeb4640e1bfec",
    8: "ebe064ab0c4a5e41e7cbf72eee0fa1899b0dd346",
}


def _chunk_index(path: Path) -> int:
    suffix = path.name.rsplit(".", 1)[-1]
    if not suffix.isdigit():
        raise RuntimeError(f"Recovery chunk has non-numeric suffix: {path.name}")
    return int(suffix)


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _validated_chunks(chunks: list[Path], expected_sha1: dict[int, str]) -> list[Path]:
    indexed = [(_chunk_index(path), path) for path in chunks]
    indices = [index for index, _ in indexed]
    if len(indices) != len(set(indices)):
        raise RuntimeError(f"Duplicate recovery chunk index detected: {indices}")

    actual = sorted(indices)
    expected = sorted(expected_sha1)
    if actual != expected:
        raise RuntimeError(f"Recovery chunk sequence mismatch: expected {expected}, found {actual}")

    ordered = [path for _, path in sorted(indexed, key=lambda item: item[0])]
    for index, path in zip(expected, ordered):
        raw = path.read_bytes()
        actual_sha1 = _git_blob_sha1(raw)
        if actual_sha1 != expected_sha1[index]:
            raise RuntimeError(
                f"Recovery chunk integrity mismatch for {path.name}: "
                f"expected git blob {expected_sha1[index]}, found {actual_sha1}"
            )
    return ordered


def _validate_webp(data: bytes, expected_bytes: int) -> None:
    if len(data) != expected_bytes:
        raise RuntimeError(
            f"Reassembled WebP length mismatch: expected {expected_bytes}, found {len(data)}"
        )
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise RuntimeError("Reassembled asset is not a valid RIFF/WebP container")
    declared_bytes = int.from_bytes(data[4:8], "little") + 8
    if declared_bytes != len(data):
        raise RuntimeError(
            f"Reassembled WebP RIFF length mismatch: header declares {declared_bytes}, "
            f"file contains {len(data)}"
        )


def materialize_background() -> Path:
    if ASSET.exists():
        return ASSET
    chunks = list(ASSET.parent.glob(CHUNK_GLOB))
    if not chunks:
        raise FileNotFoundError(f"Missing {ASSET} and recovery chunks {CHUNK_GLOB}")

    ordered = _validated_chunks(chunks, EXPECTED_CHUNK_GIT_SHA1)
    encoded = "".join(path.read_text(encoding="ascii").strip() for path in ordered)
    data = base64.b64decode(encoded, validate=True)
    _validate_webp(data, EXPECTED_ASSET_BYTES)
    ASSET.write_bytes(data)
    return ASSET


if __name__ == "__main__":
    print(materialize_background())
