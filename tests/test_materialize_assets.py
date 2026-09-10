import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "materialize_assets.py"
SPEC = importlib.util.spec_from_file_location("aether_materialize_assets", MODULE_PATH)
assert SPEC and SPEC.loader
materialize_assets = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = materialize_assets
SPEC.loader.exec_module(materialize_assets)


def _write_chunks(tmp_path: Path, count: int):
    paths = []
    expected = {}
    for index in range(count):
        path = tmp_path / f"asset.b64.{index}"
        data = f"chunk-{index}".encode("ascii")
        path.write_bytes(data)
        paths.append(path)
        expected[index] = materialize_assets._git_blob_sha1(data)
    return paths, expected


def test_validated_chunks_sorts_numeric_suffixes_not_lexicographically(tmp_path: Path):
    paths, expected = _write_chunks(tmp_path, 11)
    ordered = materialize_assets._validated_chunks(list(reversed(paths)), expected)
    assert [materialize_assets._chunk_index(path) for path in ordered] == list(range(11))


def test_validated_chunks_rejects_missing_sequence_index(tmp_path: Path):
    paths, expected = _write_chunks(tmp_path, 3)
    with pytest.raises(RuntimeError, match="sequence mismatch"):
        materialize_assets._validated_chunks(paths[:-1], expected)


def test_validated_chunks_rejects_content_drift(tmp_path: Path):
    paths, expected = _write_chunks(tmp_path, 2)
    paths[1].write_bytes(b"changed")
    with pytest.raises(RuntimeError, match="integrity mismatch"):
        materialize_assets._validated_chunks(paths, expected)


def test_validate_webp_checks_container_and_declared_length():
    payload = b"VP8 " + b"\x00" * 8
    size = 4 + len(payload)
    data = b"RIFF" + size.to_bytes(4, "little") + b"WEBP" + payload
    materialize_assets._validate_webp(data, len(data))

    with pytest.raises(RuntimeError, match="length mismatch"):
        materialize_assets._validate_webp(data, len(data) + 1)

    corrupt = b"NOPE" + data[4:]
    with pytest.raises(RuntimeError, match="not a valid RIFF/WebP"):
        materialize_assets._validate_webp(corrupt, len(corrupt))
