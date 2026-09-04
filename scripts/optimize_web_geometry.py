from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/vx4800/web"
SOURCE = OUT / "vx4800-coordination-v1.3.0.glb"
OPTIMIZED = OUT / "vx4800-coordination-v1.3.0.optimized.glb"
MANIFEST = OUT / "optimization-manifest.json"
GLTF_TRANSFORM_PACKAGE = "@gltf-transform/cli@4.5.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/generate_web_geometry.py")], check=True)

    npx = shutil.which("npx")
    if npx is None:
        raise RuntimeError("npx is required to build the derived optimized coordination GLB")

    if OPTIMIZED.exists():
        OPTIMIZED.unlink()

    cmd = [
        npx,
        "--yes",
        "--package",
        GLTF_TRANSFORM_PACKAGE,
        "gltf-transform",
        "meshopt",
        str(SOURCE),
        str(OPTIMIZED),
        "--level",
        "medium",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)

    source_bytes = SOURCE.stat().st_size
    optimized_bytes = OPTIMIZED.stat().st_size
    byte_delta = optimized_bytes - source_bytes
    manifest = {
        "schemaVersion": "1.1.0",
        "fixtureId": "vx4800-bf-01",
        "designRevision": "1.3.0",
        "authority": "coordination-only-derived-web-asset",
        "source": {
            "file": SOURCE.name,
            "sha256": sha256(SOURCE),
            "byteLength": source_bytes,
        },
        "optimized": {
            "file": OPTIMIZED.name,
            "sha256": sha256(OPTIMIZED),
            "byteLength": optimized_bytes,
            "rawByteRatio": round(optimized_bytes / source_bytes, 6),
            "rawByteDelta": byte_delta,
            "extensionsExpected": ["EXT_meshopt_compression"],
            "performanceIntent": "Meshopt-encoded browser review asset; raw GLB size is not required to be smaller than the already compact instanced source.",
        },
        "optimizer": {
            "tool": "glTF-Transform CLI",
            "package": GLTF_TRANSFORM_PACKAGE,
            "command": "meshopt",
            "level": "medium",
        },
        "constraints": {
            "mayReplaceControlledCoordinationGlb": False,
            "mayBecomeManufacturingAuthority": False,
            "nodeIdentityMustBePreserved": True,
            "sourceGeometryRemainsAuthoritativeForCoordinationQa": True,
            "rawFileSizeReductionRequired": False,
        },
        "notes": [
            "The source GLB already reuses three butterfly meshes across 240 instances and is therefore unusually compact.",
            "EXT_meshopt_compression adds decoder metadata and may increase raw container bytes for this specific model.",
            "The derived asset exists to exercise a standard web delivery path and preserve a future optimization hook without changing source coordination authority."
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(OPTIMIZED)
    print(manifest["optimized"]["sha256"])
    print(f"source bytes={source_bytes} optimized bytes={optimized_bytes} delta={byte_delta:+d}")
    return OPTIMIZED


if __name__ == "__main__":
    build()
