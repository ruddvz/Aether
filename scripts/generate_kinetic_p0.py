from pathlib import Path
import json
import math
import re

import ezdxf
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures/vx4800"
DEFAULT_OUT = ROOT / "build/vx4800/kinetics"


def rounded_rectangle_points(width, depth, radius, segments_per_corner=16):
    points = []
    centers = [
        (width / 2 - radius, depth / 2 - radius),
        (-width / 2 + radius, depth / 2 - radius),
        (-width / 2 + radius, -depth / 2 + radius),
        (width / 2 - radius, -depth / 2 + radius),
    ]
    starts = [0, 90, 180, 270]
    for (cx, cy), start in zip(centers, starts):
        for index in range(segments_per_corner + 1):
            angle = math.radians(start + index * 90 / segments_per_corner)
            points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def assert_p0_boundary(interface):
    if interface["finalInterfaceControlReleased"]:
        raise ValueError("P0 generator is for the unreleased interface-control state only")
    unresolved = interface["interfaceParameters"]
    if not unresolved:
        raise ValueError("P0 interface package must contain explicit interface parameters")
    for parameter in unresolved:
        if parameter["status"] != "tbd" or parameter["value"] is not None:
            raise ValueError(
                f"P0 generator refuses partially frozen interface parameter {parameter['id']}; "
                "use the controlled post-P0 drawing workflow instead"
            )


def build(output_dir=None):
    params = json.loads((FIX / "geometry/parameters-v1.3.0.json").read_text())
    interface = json.loads((FIX / "kinetics/interface-control-v1.json").read_text())
    assert_p0_boundary(interface)

    schedule = pd.read_csv(FIX / "composition/engineering-v1.3.0.csv")
    leds = pd.read_csv(FIX / "photometry/led-setout-engineering-v1.3.0.csv")
    if len(schedule) != 240:
        raise ValueError(f"Expected 240 controlled suspension locations, found {len(schedule)}")
    if len(leds) != 14:
        raise ValueError(f"Expected 14 controlled fixed LED locations, found {len(leds)}")

    out = Path(output_dir) if output_dir is not None else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)

    document = ezdxf.new("R12")
    document.units = 4
    layers = [
        ("CONTROLLED_FIXED_CANOPY", 7),
        ("CONTROLLED_ROTATING_CARRIER", 3),
        ("CONTROLLED_CABLE_EXITS", 8),
        ("CONTROLLED_FIXED_LEDS", 2),
        ("FUNCTIONAL_DATUM", 6),
        ("INTERFACE_CALLOUTS", 4),
        ("TBD_PARAMETERS", 1),
        ("NOTES", 7),
    ]
    for name, color in layers:
        document.layers.add(name, color=color)

    model = document.modelspace()
    canopy = params["canopy"]
    carrier = params["rotatingCarrier"]

    model.add_polyline2d(
        rounded_rectangle_points(canopy["widthMm"], canopy["depthMm"], canopy["cornerRadiusMm"]),
        close=True,
        dxfattribs={"layer": "CONTROLLED_FIXED_CANOPY"},
    )
    model.add_polyline2d(
        rounded_rectangle_points(carrier["widthMm"], carrier["depthMm"], carrier["cornerRadiusMm"]),
        close=True,
        dxfattribs={"layer": "CONTROLLED_ROTATING_CARRIER"},
    )

    for _, row in schedule.iterrows():
        model.add_circle(
            (float(row.ceiling_x_mm), float(row.ceiling_y_mm)),
            2.0,
            dxfattribs={"layer": "CONTROLLED_CABLE_EXITS"},
        )
    for _, row in leds.iterrows():
        model.add_circle(
            (float(row.x_mm), float(row.y_mm)),
            8.0,
            dxfattribs={"layer": "CONTROLLED_FIXED_LEDS"},
        )

    # The architecture controls only that the rotation axis is vertical. It does not yet
    # establish an XY physical datum feature. Do not infer that the composition origin is
    # the bearing/shaft axis merely because the controlled setout is centered around it.
    model.add_text(
        "KD-B VERTICAL ROTATION AXIS - XY PHYSICAL DATUM LOCATION / FEATURE TBD; COMPOSITION ORIGIN IS NOT SUBSTITUTED",
        dxfattribs={"height": 14, "layer": "FUNCTIONAL_DATUM"},
    ).set_placement((-1120, 700))

    model.add_text(
        "AETHERIA VX4800 KINETIC P0 INTERFACE CONTROL - NOT MANUFACTURING AUTHORITY",
        dxfattribs={"height": 22, "layer": "NOTES"},
    ).set_placement((-1180, -820))
    model.add_text(
        "CONTROLLED SETOUT SHOWN; LOAD/SELECTION-DEPENDENT MECHANISM FOOTPRINTS ARE INTENTIONALLY NOT DRAWN",
        dxfattribs={"height": 14, "layer": "NOTES"},
    ).set_placement((-1180, -850))
    model.add_text(
        "24 mm ROTATING-CARRIER PARAMETER IS NOT AN AVAILABLE MECHANISM STACK HEIGHT",
        dxfattribs={"height": 14, "layer": "NOTES"},
    ).set_placement((-1180, -875))

    # Interface callouts are annotation-only. No fake bearing/brake/lock/retention/sensor
    # footprints are generated while their controlled parameters remain TBD.
    x_callout = 1260
    y_callout = 670
    for index, interface_item in enumerate(interface["mechanicalInterfaces"]):
        model.add_text(
            f"{interface_item['id']}: FOOTPRINT / MATING GEOMETRY TBD",
            dxfattribs={"height": 13, "layer": "INTERFACE_CALLOUTS"},
        ).set_placement((x_callout, y_callout - index * 24))

    x_parameter = 1260
    y_parameter = 360
    for index, parameter in enumerate(interface["interfaceParameters"]):
        model.add_text(
            f"{parameter['id']} = TBD ({parameter['dependency']})",
            dxfattribs={"height": 10, "layer": "TBD_PARAMETERS"},
        ).set_placement((x_parameter, y_parameter - index * 18))

    drawing_path = out / "vx4800-kinetic-p0-interface-v1.dxf"
    document.saveas(drawing_path)
    text = drawing_path.read_text()
    text = re.sub(r"(\$TDCREATE\s+40\s+)\S+", r"\g<1>2461288.5", text)
    text = re.sub(r"(\$TDUPDATE\s+40\s+)\S+", r"\g<1>2461288.5", text)
    text = re.sub(r"(\$TDUCREATE\s+40\s+)\S+", r"\g<1>0.0", text)
    text = re.sub(r"(\$TDUUPDATE\s+40\s+)\S+", r"\g<1>0.0", text)
    text = re.sub(r"1\.4\.4 @ [^\r\n]+", "1.4.4 @ 2026-09-04T00:00:00+00:00", text)
    drawing_path.write_text(text)

    manifest = {
        "fixtureId": "vx4800-bf-01",
        "drawing": drawing_path.name,
        "status": "p0-interface-coordination-not-manufacturing-authority",
        "controlledGeometry": {
            "suspensionLocations": 240,
            "fixedAccentHeads": 14,
            "canopySource": "fixtures/vx4800/geometry/parameters-v1.3.0.json",
            "carrierSource": "fixtures/vx4800/geometry/parameters-v1.3.0.json",
            "suspensionSource": "fixtures/vx4800/composition/engineering-v1.3.0.csv",
            "fixedLedSource": "fixtures/vx4800/photometry/led-setout-engineering-v1.3.0.csv",
        },
        "interfaceControlSource": "fixtures/vx4800/kinetics/interface-control-v1.json",
        "physicalInterfaceFootprintsDrawn": False,
        "rotationAxisXYPhysicalDatumDrawn": False,
        "reason": "All load/selection-dependent interface parameters remain TBD/null; P0 must not invent mating geometry or infer a physical rotation-axis XY datum from the composition origin.",
        "interfaceIds": [item["id"] for item in interface["mechanicalInterfaces"]],
        "tbdParameterIds": [item["id"] for item in interface["interfaceParameters"]],
    }
    manifest_path = out / "vx4800-kinetic-p0-interface-v1.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return drawing_path, manifest_path


if __name__ == "__main__":
    drawing, manifest = build()
    print(drawing)
    print(manifest)
