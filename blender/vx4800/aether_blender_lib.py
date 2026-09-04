# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import bmesh
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
    set_socket(bsdf, ("Coat Roughness",), 0.08)
    set_socket(bsdf, ("Anisotropic IOR Level", "Anisotropic"), anisotropic)
    return m


def add_micro_roughness(material: bpy.types.Material, low: float, high: float, scale: float) -> None:
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if not bsdf or not bsdf.inputs.get("Roughness"):
        return
    tex = nodes.new("ShaderNodeTexCoord")
    tex.name = "AETHERIA_MICRO_TEXCOORD"
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = "AETHERIA_MICRO_ROUGHNESS"
    noise.noise_dimensions = "3D"
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.45
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.name = "AETHERIA_ROUGHNESS_RANGE"
    ramp.color_ramp.elements[0].color = (low, low, low, 1.0)
    ramp.color_ramp.elements[1].color = (high, high, high, 1.0)
    links.new(tex.outputs["Generated"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])


def mark_visual_finish(material: bpy.types.Material, status: str = "visualization-finish-study") -> bpy.types.Material:
    material["aetheria_authority"] = "visualization-only"
    material["aetheria_finish_status"] = status
    return material


def make_glass_material() -> bpy.types.Material:
    m = principled_material(
        "MAT_BUTTERFLY_OPTICAL_GLASS",
        "#FAFDFF",
        metallic=0.0,
        roughness=0.014,
        transmission=1.0,
        ior=1.50,
        coat=0.06,
    )
    m.diffuse_color = rgba("#FAFDFF")
    m["aetheria_authority"] = "visualization-only"
    m["aetheria_material_status"] = "optical-glass-visualization-study-not-commercially-locked"
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf and bsdf.inputs.get("Roughness"):
        tex = nodes.new("ShaderNodeTexCoord")
        tex.name = "AETHERIA_GLASS_TEXCOORD"
        noise = nodes.new("ShaderNodeTexNoise")
        noise.name = "AETHERIA_GLASS_MICRO_ROUGHNESS"
        noise.noise_dimensions = "3D"
        noise.inputs["Scale"].default_value = 420.0
        noise.inputs["Detail"].default_value = 1.2
        noise.inputs["Roughness"].default_value = 0.32
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.name = "AETHERIA_GLASS_ROUGHNESS_RANGE"
        ramp.color_ramp.elements[0].color = (0.008, 0.008, 0.008, 1.0)
        ramp.color_ramp.elements[1].color = (0.024, 0.024, 0.024, 1.0)
        links.new(tex.outputs["Generated"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])
    output = nodes.get("Material Output")
    absorption = nodes.new("ShaderNodeVolumeAbsorption")
    absorption.name = "AETHERIA_EDGE_ABSORPTION"
    absorption.inputs["Color"].default_value = rgba("#E8F3F5")
    absorption.inputs["Density"].default_value = 0.035
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
    m["aetheria_authority"] = "visualization-only"
    return m


def build_materials() -> dict[str, bpy.types.Material]:
    champagne = mark_visual_finish(principled_material("MAT_PVD_DARK_CHAMPAGNE", "#544231", 0.94, 0.17, coat=0.24, anisotropic=0.20))
    black_titanium = mark_visual_finish(principled_material("MAT_PVD_BLACK_TITANIUM", "#151515", 0.92, 0.20, coat=0.18, anisotropic=0.10))
    brass = mark_visual_finish(principled_material("MAT_BRUSHED_BRASS", "#A87D45", 0.94, 0.22, coat=0.16, anisotropic=0.30))
    nickel = mark_visual_finish(principled_material("MAT_SATIN_NICKEL", "#969894", 0.92, 0.29, coat=0.10, anisotropic=0.18))
    cable = mark_visual_finish(principled_material("MAT_CABLE_STAINLESS", "#474D52", 0.92, 0.38), "visualization-cable-appearance")
    body = mark_visual_finish(principled_material("MAT_BUTTERFLY_BODY_CHAMPAGNE", "#8F6E4D", 0.92, 0.20, coat=0.20), "visualization-butterfly-spine-finish")
    led_head = mark_visual_finish(principled_material("MAT_LED_HEAD_TITANIUM", "#151513", 0.92, 0.19, coat=0.18), "visualization-head-finish")
    stage = principled_material("MAT_STAGE_IVORY", "#D9D3C8", 0.0, 0.68)
    dark_stage = principled_material("MAT_STAGE_DARK", "#080706", 0.0, 0.90)
    for material, low, high, scale in (
        (champagne, 0.13, 0.22, 180.0),
        (black_titanium, 0.16, 0.25, 210.0),
        (brass, 0.18, 0.28, 150.0),
        (nickel, 0.24, 0.34, 190.0),
        (cable, 0.32, 0.46, 260.0),
        (body, 0.16, 0.25, 220.0),
        (led_head, 0.15, 0.24, 220.0),
    ):
        add_micro_roughness(material, low, high, scale)
    return {
        "glass": make_glass_material(),
        "champagne": champagne,
        "black_titanium": black_titanium,
        "brass": brass,
        "nickel": nickel,
        "cable": cable,
        "body": body,
        "led_head": led_head,
        "led_lens": make_emission_material("MAT_LED_LENS_3000K", "#FFD0A0", 2.0),
        "stage": stage,
        "dark_stage": dark_stage,
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
    bevel.segments = 4
    bevel.limit_method = "ANGLE"
    return obj


def bezier_segment(p0, p1, p2, p3, steps: int = 12):
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


def polygon_signed_area(points) -> float:
    return 0.5 * sum(
        points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1]
        for i in range(len(points))
    )


def polygon_centroid(points) -> tuple[float, float]:
    area2 = 2.0 * polygon_signed_area(points)
    if abs(area2) < 1e-12:
        return (
            sum(p[0] for p in points) / len(points),
            sum(p[1] for p in points) / len(points),
        )
    cx = 0.0
    cy = 0.0
    for i in range(len(points)):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % len(points)]
        cross = x0 * y1 - x1 * y0
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    return cx / (3.0 * area2), cy / (3.0 * area2)


def faceted_wing_mesh(name: str, points, thickness: float) -> bpy.types.Mesh:
    points = list(points)
    if polygon_signed_area(points) < 0.0:
        points.reverse()
    n = len(points)
    cx, cy = polygon_centroid(points)
    outer_z = thickness * 0.20
    inner_z = thickness * 0.46
    inset = 0.70
    top_outer = [(x, y, outer_z) for x, y in points]
    top_inner = [
        (cx + (x - cx) * inset, cy + (y - cy) * inset, inner_z)
        for x, y in points
    ]
    bottom_outer = [(x, y, -outer_z) for x, y in points]
    bottom_inner = [
        (cx + (x - cx) * inset, cy + (y - cy) * inset, -inner_z)
        for x, y in points
    ]
    verts = top_outer + top_inner + bottom_outer + bottom_inner
    to = 0
    ti = n
    bo = 2 * n
    bi = 3 * n
    faces: list[tuple[int, ...]] = [
        tuple(ti + i for i in range(n)),
        tuple(reversed([bi + i for i in range(n)])),
    ]
    for i in range(n):
        j = (i + 1) % n
        faces.append((to + i, to + j, ti + j, ti + i))
        faces.append((bo + j, bo + i, bi + i, bi + j))
        faces.append((to + j, to + i, bo + i, bo + j))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


def add_proto_mesh(collection, name, mesh, material, rotation_y=0.0, edge_bevel=0.00055):
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.rotation_euler.y = rotation_y
    bevel = obj.modifiers.new("AETHERIA_CRYSTAL_EDGE", "BEVEL")
    bevel.width = edge_bevel
    bevel.segments = 3
    bevel.limit_method = "ANGLE"
    obj["aetheria_geometry_status"] = "visualization-optical-sculpting-within-controlled-envelope"
    return obj


def add_sculptural_spine(collection, span: float, length: float, thickness: float, mat) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0)
    spine = bpy.context.object
    spine.name = "CENTRAL_SPINE"
    link_object(spine, collection)
    spine.scale = (
        max(span * 0.026, 0.0028),
        max(length * 0.43, 0.024),
        max(thickness * 0.42, 0.0020),
    )
    spine.location.y = -length * 0.035
    spine.data.materials.append(mat)
    bevel = spine.modifiers.new("AETHERIA_SPINE_SOFTEN", "BEVEL")
    bevel.width = min(0.0006, thickness * 0.08)
    bevel.segments = 3
    spine["aetheria_geometry_status"] = "visualization-sculptural-abstraction"


def make_butterfly_prototype(size, span, length, thickness, fold_deg, mats):
    c = bpy.data.collections.new(f"PROTO_BUTTERFLY_{size}")
    edge_bevel = min(0.00065, max(0.00038, thickness * 0.082))
    for side, label in ((1, "L"), (-1, "R")):
        for kind, suffix, trim in (("fore", "FORE", 0.0), ("hind", "HIND", -3.0)):
            outline = wing_outline(kind, span, length, side)
            mesh = faceted_wing_mesh(f"PROTO_{size}_{label}_{suffix}_MESH", outline, thickness)
            add_proto_mesh(
                c,
                f"PROTO_{size}_{label}_{suffix}",
                mesh,
                mats["glass"],
                math.radians(side * (fold_deg + trim)),
                edge_bevel=edge_bevel,
            )
    add_sculptural_spine(c, span, length, thickness, mats["body"])
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
    data.clip_start = 0.05
    data.clip_end = 200.0
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    obj["aetheria_role"] = "render_camera"
    return obj


def create_area_light(
    name,
    location,
    target,
    energy,
    size,
    color,
    collection,
    shape="DISK",
    size_y=None,
    spread_deg=None,
):
    data = bpy.data.lights.new(name + "_DATA", "AREA")
    data.energy = energy
    data.shape = shape
    data.size = size
    if size_y is not None and hasattr(data, "size_y"):
        data.size_y = size_y
    if spread_deg is not None and hasattr(data, "spread"):
        data.spread = math.radians(spread_deg)
    data.color = color
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    obj["aetheria_light_class"] = "photographic-render-stage"
    obj["aetheria_authority"] = "visualization-only"
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
    obj["aetheria_light_class"] = "fixture-integrated-visual-study"
    return obj


def create_led_head(name, x, y, mat_body, mat_lens, collection):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=0.0225, depth=0.060, location=(x, y, -0.035))
    body = bpy.context.object
    body.name = name
    link_object(body, collection)
    body.data.materials.append(mat_body)
    bevel = body.modifiers.new("AETHERIA_HEAD_EDGE", "BEVEL")
    bevel.width = 0.0012
    bevel.segments = 3
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=0.0175, depth=0.0015, location=(x, y, -0.066))
    lens = bpy.context.object
    lens.name = name + "_LENS"
    link_object(lens, collection)
    lens.data.materials.append(mat_lens)
    return body


def build_stage(mats, collection) -> None:
    bpy.ops.mesh.primitive_plane_add(size=32.0, location=(0, 7.0, -1.3), rotation=(math.radians(90), 0, 0))
    wall = bpy.context.object
    wall.name = "STAGE_BACKDROP"
    link_object(wall, collection)
    wall.data.materials.append(mats["dark_stage"])
    wall["aetheria_stage_role"] = "seamless-dark-product-background"
    wall["aetheria_authority"] = "visualization-only"


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
    scene.view_settings.exposure = -0.45
    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("AETHERIA_WORLD")
        scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.008, 0.007, 0.006, 1.0)
        background.inputs["Strength"].default_value = 0.12
    world.color = (0.008, 0.007, 0.006)
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
