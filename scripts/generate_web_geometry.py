from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math

import numpy as np
import pandas as pd
import trimesh

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures/vx4800"
OUT = ROOT / "build/vx4800/web"


def prism_from_xz(points: list[tuple[float, float]], thickness: float) -> trimesh.Trimesh:
    """Create a thin convex prism from an X/Z polygon, extruded along Y."""
    n = len(points)
    y0, y1 = -thickness / 2, thickness / 2
    vertices = []
    for x, z in points:
        vertices.append([x, y0, z])
    for x, z in points:
        vertices.append([x, y1, z])

    faces: list[list[int]] = []
    # bottom/top fan; reverse bottom winding
    for i in range(1, n - 1):
        faces.append([0, i + 1, i])
        faces.append([n, n + i, n + i + 1])
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j])
        faces.append([i, n + j, n + i])
    return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)


def butterfly_mesh(span_mm: float, length_mm: float, thickness_mm: float, fold_deg: float) -> trimesh.Trimesh:
    w = span_mm / 1000.0
    l = length_mm / 1000.0
    t = max(0.0018, thickness_mm / 1000.0 * 0.36)

    fore = [
        (0.008*w, 0.020*l), (0.110*w, 0.190*l), (0.335*w, 0.430*l),
        (0.490*w, 0.350*l), (0.420*w, 0.090*l), (0.175*w, -0.005*l)
    ]
    hind = [
        (0.008*w, -0.015*l), (0.185*w, -0.045*l), (0.405*w, -0.220*l),
        (0.245*w, -0.440*l), (0.055*w, -0.205*l)
    ]

    meshes: list[trimesh.Trimesh] = []
    for side in (-1, 1):
        for points, trim in ((fore, 0.0), (hind, -3.0)):
            pts = [(side*x, z) for x, z in points]
            m = prism_from_xz(pts, t)
            angle = math.radians(side * (fold_deg + trim))
            m.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1]))
            meshes.append(m)

    body = trimesh.creation.cylinder(radius=max(0.0025, w * 0.022), height=l * 0.52, sections=12)
    body.apply_translation([0, 0, l * 0.035])
    meshes.append(body)
    out = trimesh.util.concatenate(meshes)
    out.process(validate=True)
    return out


def node_transform(position: tuple[float, float, float], yaw_deg: float = 0.0, scale: tuple[float, float, float] | None = None) -> np.ndarray:
    T = trimesh.transformations.rotation_matrix(math.radians(yaw_deg), [0, 1, 0])
    if scale is not None:
        S = np.eye(4)
        S[0, 0], S[1, 1], S[2, 2] = scale
        T = T @ S
    T[:3, 3] = np.array(position)
    return T


def build() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    params = json.loads((FIX / "geometry/parameters-v1.3.0.json").read_text())
    sched = pd.read_csv(FIX / "composition/engineering-v1.3.0.csv")
    leds = pd.read_csv(FIX / "photometry/led-setout-engineering-v1.3.0.csv")

    scene = trimesh.Scene()

    canopy_p = params["canopy"]
    canopy = trimesh.creation.box(extents=[canopy_p["widthMm"]/1000, canopy_p["heightMm"]/1000, canopy_p["depthMm"]/1000])
    canopy.visual.face_colors = [63, 48, 35, 255]
    scene.geometry["canopy-coordination"] = canopy
    scene.graph.update(frame_to="canopy-fixed", matrix=node_transform((0, canopy_p["heightMm"]/2000, 0)), geometry="canopy-coordination")

    carrier_p = params["rotatingCarrier"]
    carrier = trimesh.creation.box(extents=[carrier_p["widthMm"]/1000, carrier_p["thicknessMm"]/1000, carrier_p["depthMm"]/1000])
    carrier.visual.face_colors = [40, 33, 27, 255]
    scene.geometry["carrier-coordination"] = carrier
    scene.graph.update(frame_to="carrier-rotating", matrix=node_transform((0, -carrier_p["thicknessMm"]/2000, 0)), geometry="carrier-coordination")

    for key, p in params["butterflies"].items():
        geom = butterfly_mesh(p["spanMm"], p["lengthMm"], p["thicknessMm"], 42.0)
        colors = {"S": [220, 235, 240, 235], "M": [232, 238, 236, 235], "L": [238, 225, 207, 235]}
        geom.visual.face_colors = colors[key]
        scene.geometry[f"butterfly-{key}"] = geom

    cable = trimesh.creation.cylinder(radius=0.0005, height=1.0, sections=6)
    cable.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0]))
    cable.visual.face_colors = [160, 168, 174, 130]
    scene.geometry["suspension-cable"] = cable

    led = trimesh.creation.cylinder(radius=0.0225, height=0.020, sections=18)
    led.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0]))
    led.visual.face_colors = [45, 40, 36, 255]
    scene.geometry["fixed-led-head"] = led

    for _, r in sched.iterrows():
        x = float(r.ceiling_x_mm) / 1000.0
        z = -float(r.ceiling_y_mm) / 1000.0
        drop = float(r.element_origin_drop_mm) / 1000.0
        cable_len = float(r.finished_main_cable_mm) / 1000.0
        eid = str(r.element_id)
        scene.graph.update(
            frame_to=f"element-{eid}",
            matrix=node_transform((x, -drop, z), float(r.target_yaw_deg)),
            geometry=f"butterfly-{r['size']}",
        )
        scene.graph.update(
            frame_to=f"cable-{eid}",
            matrix=node_transform((x, -cable_len/2, z), scale=(1, cable_len, 1)),
            geometry="suspension-cable",
        )

    for _, r in leds.iterrows():
        x = float(r.x_mm) / 1000.0
        z = -float(r.y_mm) / 1000.0
        scene.graph.update(
            frame_to=f"led-{r.led_id}",
            matrix=node_transform((x, -0.012, z)),
            geometry="fixed-led-head",
        )

    scene.metadata.update({
        "fixtureId": "vx4800-bf-01",
        "designRevision": "1.3.0",
        "authority": "coordination-only",
        "elementCount": 240,
        "suspensionCount": 240,
        "fixedLedCount": 14,
        "units": "metres",
    })

    out = OUT / "vx4800-coordination-v1.3.0.glb"
    data = scene.export(file_type="glb")
    out.write_bytes(data)

    manifest = {
        "schemaVersion": "1.0.0",
        "fixtureId": "vx4800-bf-01",
        "designRevision": "1.3.0",
        "authority": "coordination-only",
        "file": out.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "byteLength": len(data),
        "expected": {
            "elements": 240,
            "suspensionCables": 240,
            "fixedLedHeads": 14,
            "sharedButterflyMeshes": 3
        }
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return out


if __name__ == "__main__":
    p = build()
    print(p)
    print(hashlib.sha256(p.read_bytes()).hexdigest())
