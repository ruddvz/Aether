from __future__ import annotations

from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "fixtures/vx4800/presentation/v5.2.0/assets/architectural-background.webp"
CHUNK_GLOB = ".architectural-background.webp.b64.*"

def materialize_background() -> Path:
    if ASSET.exists():
        return ASSET
    chunks = sorted(ASSET.parent.glob(CHUNK_GLOB))
    if not chunks:
        raise FileNotFoundError(f"Missing {ASSET} and recovery chunks {CHUNK_GLOB}")
    encoded = "".join(p.read_text(encoding="ascii").strip() for p in chunks)
    ASSET.write_bytes(base64.b64decode(encoded, validate=True))
    return ASSET

if __name__ == "__main__":
    print(materialize_background())
