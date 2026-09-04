from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess
import sys

import trimesh

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/vx4800/web"

subprocess.run([sys.executable, str(ROOT / "scripts/generate_web_geometry.py")], check=True)
manifest = json.loads((OUT / "manifest.json").read_text())
glb = OUT / manifest["file"]
errors = []

def req(condition, message):
    if not condition:
        errors.append(message)

req(glb.exists(), "GLB missing")
if glb.exists():
    req(hashlib.sha256(glb.read_bytes()).hexdigest() == manifest["sha256"], "GLB SHA mismatch")
    req(glb.stat().st_size == manifest["byteLength"], "GLB byte length mismatch")
    try:
        scene = trimesh.load(glb, force="scene")
        geom_names = set(scene.geometry.keys())
        req({"butterfly-S", "butterfly-M", "butterfly-L"}.issubset(geom_names), f"Missing butterfly meshes: {geom_names}")
        nodes = set(scene.graph.nodes)
        req(sum(n.startswith("element-VX-") for n in nodes) == 240, "Expected 240 butterfly element nodes")
        req(sum(n.startswith("cable-VX-") for n in nodes) == 240, "Expected 240 cable nodes")
        req(sum(n.startswith("led-LED-") for n in nodes) == 14, "Expected 14 LED nodes")
        bounds = scene.bounds
        ext = bounds[1] - bounds[0]
        req(ext[1] <= 5.05, f"Vertical scene extent suspicious: {ext[1]:.3f} m")
        req(ext[0] <= 2.6 and ext[2] <= 1.8, f"Plan extents suspicious: {ext}")
    except Exception as exc:
        errors.append(f"GLB load failed: {exc}")

if errors:
    print("WEB GEOMETRY QA FAILED")
    for e in errors:
        print("-", e)
    raise SystemExit(1)
print("WEB GEOMETRY QA PASSED - 240 elements + 240 cables + 14 fixed heads; coordination authority only")
