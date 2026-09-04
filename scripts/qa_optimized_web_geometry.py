from __future__ import annotations

from pathlib import Path
import hashlib
import json
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/vx4800/web"

subprocess.run([sys.executable, str(ROOT / "scripts/optimize_web_geometry.py")], check=True)
manifest = json.loads((OUT / "optimization-manifest.json").read_text())
source = OUT / manifest["source"]["file"]
optimized = OUT / manifest["optimized"]["file"]
errors: list[str] = []


def req(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError("GLB is too short")
    magic, version, total_length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or total_length != len(data):
        raise ValueError("Invalid GLB header")
    offset = 12
    while offset + 8 <= len(data):
        chunk_length, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset:offset + chunk_length]
        offset += chunk_length
        if chunk_type == 0x4E4F534A:
            return json.loads(chunk.rstrip(b"\x00 \t\r\n").decode("utf-8"))
    raise ValueError("GLB JSON chunk not found")


req(manifest["authority"] == "coordination-only-derived-web-asset", "optimized authority label changed")
req(manifest["constraints"]["mayReplaceControlledCoordinationGlb"] is False, "optimized asset must not replace source coordination GLB")
req(manifest["constraints"]["mayBecomeManufacturingAuthority"] is False, "optimized asset must not become manufacturing authority")
req(manifest["constraints"]["rawFileSizeReductionRequired"] is False, "raw-size policy must remain explicit for compact instanced source")
req(source.exists(), "source coordination GLB missing")
req(optimized.exists(), "optimized coordination GLB missing")

if source.exists():
    req(sha256(source) == manifest["source"]["sha256"], "source GLB SHA mismatch")
    req(source.stat().st_size == manifest["source"]["byteLength"], "source byte length mismatch")
if optimized.exists():
    req(sha256(optimized) == manifest["optimized"]["sha256"], "optimized GLB SHA mismatch")
    req(optimized.stat().st_size == manifest["optimized"]["byteLength"], "optimized byte length mismatch")
    req(
        optimized.stat().st_size - source.stat().st_size == manifest["optimized"]["rawByteDelta"],
        "optimized raw byte delta mismatch",
    )
    req(
        abs((optimized.stat().st_size / source.stat().st_size) - manifest["optimized"]["rawByteRatio"]) < 0.0000015,
        "optimized raw byte ratio mismatch",
    )
    req(optimized.stat().st_size <= source.stat().st_size * 2, "Meshopt derived GLB overhead is unexpectedly large")

try:
    source_doc = glb_json(source)
    optimized_doc = glb_json(optimized)
    source_names = {n.get("name", "") for n in source_doc.get("nodes", [])}
    optimized_names = {n.get("name", "") for n in optimized_doc.get("nodes", [])}
    req(source_names == optimized_names, "node identity changed during optimization")
    req(sum(n.startswith("element-VX-") for n in optimized_names) == 240, "optimized GLB must preserve 240 element nodes")
    req(sum(n.startswith("cable-VX-") for n in optimized_names) == 240, "optimized GLB must preserve 240 cable nodes")
    req(sum(n.startswith("led-LED-") for n in optimized_names) == 14, "optimized GLB must preserve 14 LED nodes")
    extensions = set(optimized_doc.get("extensionsUsed", []))
    req("EXT_meshopt_compression" in extensions, f"expected EXT_meshopt_compression, got {sorted(extensions)}")
    req(len(source_doc.get("nodes", [])) == len(optimized_doc.get("nodes", [])), "node count changed during optimization")
    req(len(source_doc.get("meshes", [])) == len(optimized_doc.get("meshes", [])), "mesh count changed during optimization")
except Exception as exc:
    errors.append(f"optimized GLB structure check failed: {exc}")

if errors:
    print("OPTIMIZED WEB GEOMETRY QA FAILED")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

ratio = manifest["optimized"]["rawByteRatio"]
delta = manifest["optimized"]["rawByteDelta"]
print(f"OPTIMIZED WEB GEOMETRY QA PASSED - Meshopt encoded; raw ratio={ratio:.3f}, delta={delta:+d} bytes; coordination authority unchanged")
