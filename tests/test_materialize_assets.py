import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "materialize_assets.py"
SPEC = importlib.util.spec_from_file_location("aether_materialize_assets", MODULE_PATH)
assert SPEC and SPEC.loader
materialize = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = materialize
SPEC.loader.exec_module(materialize)


def _configure(monkeypatch, tmp_path, data: bytes):
    asset = tmp_path / "asset.webp"
    fixture = tmp_path / "fixture.json"
    fixture.write_text(
        json.dumps(
            {
                "assets": [
                    {
                        "id": "test-background",
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }
                ]
            }
        )
    )
    monkeypatch.setattr(materialize, "ASSET", asset)
    monkeypatch.setattr(materialize, "FIXTURE", fixture)
    monkeypatch.setattr(materialize, "ASSET_ID", "test-background")
    monkeypatch.setattr(materialize, "CHUNK_GLOB", ".asset.webp.b64.*")
    return asset


def test_materializer_orders_numeric_suffixes_not_lexicographic(monkeypatch, tmp_path):
    data = b"AETHERIA deterministic asset bytes for numeric chunk ordering"
    asset = _configure(monkeypatch, tmp_path, data)
    encoded = base64.b64encode(data).decode("ascii")

    width = max(1, len(encoded) // 11)
    parts = [encoded[index:index + width] for index in range(0, len(encoded), width)]
    for number, part in enumerate(parts):
        (tmp_path / f".asset.webp.b64.{number}").write_text(part, encoding="ascii")

    assert len(parts) > 10
    assert materialize.materialize_background() == asset
    assert asset.read_bytes() == data


def test_materializer_rejects_non_contiguous_chunks(monkeypatch, tmp_path):
    data = b"controlled"
    asset = _configure(monkeypatch, tmp_path, data)
    encoded = base64.b64encode(data).decode("ascii")
    (tmp_path / ".asset.webp.b64.0").write_text(encoded[:4], encoding="ascii")
    (tmp_path / ".asset.webp.b64.2").write_text(encoded[4:], encoding="ascii")

    with pytest.raises(ValueError, match="contiguous from 0"):
        materialize.materialize_background()
    assert not asset.exists()


def test_materializer_rejects_digest_mismatch_before_write(monkeypatch, tmp_path):
    expected = b"expected bytes"
    asset = _configure(monkeypatch, tmp_path, expected)
    encoded = base64.b64encode(b"different bytes").decode("ascii")
    (tmp_path / ".asset.webp.b64.0").write_text(encoded, encoding="ascii")

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        materialize.materialize_background()
    assert not asset.exists()
