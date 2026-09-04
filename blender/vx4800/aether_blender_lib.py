# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

MM = 0.001


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.materials,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)
    root_default = bpy.data.collections.get("Collection")
    if root_default:
        root_default.name = "AETHERIA_VX4800"


def ensure_collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    parent = parent or bpy.context.scene.collection
    if c.name not in parent.children:
        try:
            parent.children.link(c)
        except RuntimeError:
            pass
    return c


def link_object(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)


def rgba(hex_value: str) -> tuple[float, float, float, float]:
    h = hex_value.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)


def set_socket(node: bpy.types.Node, names: tuple[str, ...], value) -> None:
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            socket.default_value = value
            return


def principled_material(
    name: str,
    base: str,
    metallic: float = 0.0,
    roughness: float = 0.3,
    transmission: float = 0.0,
    ior: float = 1.45,
    coat: float = 0.0,
    anisotropic: float = 0.0,
) -> bpy.types.Material:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    set_socket(bsdf, ("Base Color",), rgba(base))
    set_socket(bsdf, ("Metallic",), metallic)
    set_socket(bsdf, ("Roughness",), roughness)
    set_socket(bsdf, ("Transmission Weight", "Transmission"), transmission)
    set_socket(bsdf, ("IOR",), ior)
    set_socket(bsdf, ("Coat Weight", "Coat"), coat)
    set_socket(bsdf, ("Anisotropic IOR Level", "Anisotropic"), anisotropic)
    return m


def make_glass_material() -> bpy.types.Material:
    m = principled_material(
        "MAT_BUTTERFLY_OPTICAL_GLASS",
        "#EEF8FA",
        metallic=0.0,
        roughness=0.035,
        transmission=1.0,
        ior=1.50,
        coat=0.12,
    )
    m.diffuse_color = rgba("#EEF8FA")
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    output = nodes.get("Material Output")
    absorption = nodes.new("ShaderNodeVolumeAbsorption")
    absorption.name = "AETHERIA_EDGE_ABSORPTION"
    absorption.inputs["Color"].default_value = rgba("#DCEFF2")
    absorption.inputs["Density"].default_value = 0.12
    links.new(absorption.outputs["Volume"], output.inputs["Volume"])
    return m


def make_emission_material(name: str, color: str, strength: float) -> bpy.types.Material:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = rgba(color)
    emission.inputs["Strength"].default_value = strength
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return m


def build_materials() -> dict[str, bpy.types.Material]:
    return {
        "glass": make_glass_material(),
        "champagne": principled_material("MAT_PVD_DARK_CHAMPAGNE", "#5D4936", 0.92, 0.17, coat=0.30, anisotropic=0.18),
        "black_titanium": principled_material("MAT_PVD_BLACK_TITANIUM", "#171717", 0.88, 0.20, coat=0.22),
        "brass": principled_material("MAT_BRUSHED_BRASS", "#B98A4A", 0.92, 0.23, coat=0.20, anisotropic=0.28),
        "nickel": principled_material("MAT_SATIN_NICKEL", "#A7A7A0", 0.90, 0.30, coat=0.10, anisotropic=0.15),
        "cable": principled_material("MAT_CABLE_STAINLESS", "#596169", 0.88, 0.28),
        "body": principled_material("MAT_BUTTERFLY_BODY_CHAMPAGNE", "#C89B61", 0.90, 0.15, coat=0.35),
        "led_head": principled_material("MAT_LED_HEAD_TITANIUM", "#181715", 0.90, 0.18, coat=0.22),
        "led_lens": make_emission_material("MAT_LED_LENS_3000K", "#FFD0A0", 2.3),
        "stage": principled_material("MAT_STAGE_IVORY", "#EEEAE2", 0.0, 0.72),
        "dark_stage": principled_material("MAT_STAGE_DARK", "#12100E", 0.0, 0.78),
    }


def rounded_rect_mesh(name: str, width: float, depth: float, height: float, radius: float, segments: int = 16) -> bpy.types.Mesh:
    radius = min(radius, width / 2.0, depth / 2.0)
    pts: list[tuple[float, float]] = []
    centers = [
        (width / 2 - radius, depth / 2 - radius, 0.0),
        (-width / 2 + radius, depth / 2 - radius, 90.0),
        (-width / 2 + radius, -depth / 2 + radius, 180.0),
        (width / 2 - radius, -depth / 2 + radius, 270.0),
    ]
    for cx, cy, start in centers:
        for j in range(segments):
            a = math.radians(start + j * 90.0 / segments)
            pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    n = len(pts)
    z0, z1 = 0.0, height
    verts = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    faces: list[tuple[int, ...]] = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def add_beveled_rounded_box(name, collection, width, depth, height, radius, material, z, edge_bevel=0.006):
    mesh = rounded_rect_mesh(name + "_MESH", width, depth, height, radius)
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj, collection)
    obj.location.z = z
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("AETHERIA_EDGE_SOFTEN", "BEVEL")
    bevel.width = edge_bevel
    bevel.segments = 3
    bevel.limit_method = "ANGLE"
    return obj


def bezier_segment(p0, p1, p2, p3, steps: int = 14):
    out = []
    for i in range(steps):
        t = i / steps
        u = 1.0 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        out.append((x, y))
    return out


def wing_outline(kind: str, span: float, length: float, side: int):
    if kind == "fore":
        p0 = (0.013 * span, 0.024 * length)
        segs = [
            (p0, (0.09 * span, 0.19 * length), (0.30 * span, 0.44 * length), (0.49 * span, 0.37 * length)),
            ((0.49 * span, 0.37 * length), (0.54 * span, 0.33 * length), (0.50 * span, 0.18 * length), (0.425 * span, 0.082 * length)),
            ((0.425 * span, 0.082 * length), (0.31 * span, -0.018 * length), (0.115 * span, -0.035 * length), (0.013 * span, 0.005 * length)),
        ]
    else:
        p0 = (0.013 * span, -0.014 * length)
        segs = [
            (p0, (0.12 * span, -0.015 * length), (0.31 * span, -0.075 * length), (0.41 * span, -0.215 * length)),
            ((0.41 * span, -0.215 * length), (0.46 * span, -0.31 * length), (0.37 * span, -0.43 * length), (0.235 * span, -0.445 * length)),
            ((0.235 * span, -0.445 * length), (0.115 * span, -0.44 * length), (0.043 * span, -0.27 * length), (0.013 * span, -0.07 * length)),
        ]
    points = []
    for seg in segs:
        points.extend(bezier_segment(*seg))
    points.append(segs[-1][3])
    return [(side * x, y) for x, y in points]


def extruded_polygon_mesh(name: str, points, thickness: float):
    n = len(points)
    z0, z1 = -thickness / 2.0, thickness / 2.0
    verts = [(x, y, z0) for x, y in points] + [(x, y, z1) for x, y in points]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def add_proto_mesh(collection, name, mesh, material, rotation_y=0.0):
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.rotation_euler.y = rotation_y
    bevel = obj.modifiers.new("AETHERIA_CRYSTAL_EDGE", "BEVEL")
    bevel.width = 0.00055
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    return obj


def add_body(collection, span: float, length: float, mat) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=max(0.004, span * 0.033))
    thorax = bpy.context.object
    thorax.name = "THORAX"
    link_object(thorax, collection)
    thorax.scale = (0.72, 1.08, 0.72)
    thorax.location.y = length * 0.08
    thorax.data.materials.append(mat)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=max(0.0035, span * 0.025))
    head = bpy.context.object
    head.name = "HEAD"
    link_object(head, collection)
    head.location.y = length * 0.22
    head.data.materials.append(mat)
    for i in range(6):
        t = i / 5.0
        r = max(0.0024, span * (0.021 - 0.009 * t))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=8, radius=r)
        seg = bpy.context.object
        seg.name = f"ABDOMEN_{i+1:02d}"
        link_object(seg, collection)
        seg.scale = (0.72, 1.15, 0.72)
        seg.location.y = -length * (0.02 + i * 0.075)
        seg.data.materials.append(mat)
    for side in (-1, 1):
        curve = bpy.data.curves.new(f"ANTENNA_{side:+d}_CURVE", "CURVE")
        curve.dimensions = "3D"
        curve.bevel_depth = 0.0005
        curve.bevel_resolution = 3
        spline = curve.splines.new("BEZIER")
        spline.bezier_points.add(2)
        pts = [(side * 0.0025, length * 0.24, 0.002), (side * 0.010, length * 0.33, 0.008), (side * 0.025, length * 0.40, 0.004)]
        for bp, co in zip(spline.bezier_points, pts):
            bp.co = co
            bp.handle_left_type = "AUTO"
            bp.handle_right_type = "AUTO"
        obj = bpy.data.objects.new(f"ANTENNA_{side:+d}", curve)
        collection.objects.link(obj)
        obj.data.materials.append(mat)


def make_butterfly_prototype(size, span, length, thickness, fold_deg, mats):
    c = bpy.data.collections.new(f"PROTO_BUTTERFLY_{size}")
    for side, label in ((1, "L"), (-1, "R")):
        for kind, suffix, trim in (("fore", "FORE", 0.0), ("hind", "HIND", -2.5)):
            mesh = extruded_polygon_mesh(f"PROTO_{size}_{label}_{suffix}_MESH", wing_outline(kind, span, length, side), thickness)
            add_proto_mesh(c, f"PROTO_{size}_{label}_{suffix}", mesh, mats["glass"], math.radians(side * (fold_deg + trim)))
    add_body(c, span, length, mats["body"])
    return c


def create_curve_object(name, collection, material, bevel_depth):
    curve = bpy.data.curves.new(name + "_CURVE", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 2
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    curve.materials.append(material)
    return obj


def add_poly_spline(curve_obj, points) -> None:
    spline = curve_obj.data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1.0)


def create_camera(name, location, target, lens_mm, collection):
    data = bpy.data.cameras.new(name + "_DATA")
    data.lens = lens_mm
    data.sensor_width = 36.0
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    obj["aetheria_role"] = "render_camera"
    return obj


def create_area_light(name, location, target, energy, size, color, collection):
    data = bpy.data.lights.new(name + "_DATA", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


def create_spot_light(name, position, target, beam_deg, energy, collection):
    data = bpy.data.lights.new(name + "_DATA", "SPOT")
    data.energy = energy
    data.color = (1.0, 0.74, 0.48)
    data.spot_size = math.radians(max(beam_deg, 1.0))
    data.spot_blend = 0.22
    data.shadow_soft_size = 0.012
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    obj["aetheria_photometry_status"] = "conceptual-render-only"
    return obj


def create_led_head(name, x, y, mat_body, mat_lens, collection):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.0225, depth=0.060, location=(x, y, -0.035))
    body = bpy.context.object
    body.name = name
    link_object(body, collection)
    body.data.materials.append(mat_body)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.0175, depth=0.0015, location=(x, y, -0.066))
    lens = bpy.context.object
    lens.name = name + "_LENS"
    link_object(lens, collection)
    lens.data.materials.append(mat_lens)
    return body


def build_stage(mats, collection) -> None:
    bpy.ops.mesh.primitive_plane_add(size=16.0, location=(0, 0, -5.15))
    floor = bpy.context.object
    floor.name = "STAGE_FLOOR"
    link_object(floor, collection)
    floor.data.materials.append(mats["stage"])
    bpy.ops.mesh.primitive_plane_add(size=16.0, location=(0, 4.8, -0.9), rotation=(math.radians(90), 0, 0))
    wall = bpy.context.object
    wall.name = "STAGE_BACKDROP"
    link_object(wall, collection)
    wall.data.materials.append(mats["stage"])


def configure_scene(scene) -> None:
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = 3840
    scene.render.resolution_y = 2160
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    scene.world.color = (0.018, 0.015, 0.012)
    scene.frame_start = 1
    scene.frame_end = 4001
    scene.render.fps = 24
    if hasattr(scene, "cycles"):
        scene.cycles.samples = 512
        scene.cycles.use_denoising = True
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.01
        scene.cycles.max_bounces = 12
        scene.cycles.transmission_bounces = 12
        scene.cycles.glossy_bounces = 8
