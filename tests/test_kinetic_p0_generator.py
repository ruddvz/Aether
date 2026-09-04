from copy import deepcopy
from pathlib import Path
import importlib.util
import json

import ezdxf
import pytest

ROOT = Path(__file__).resolve().parents[1]
INTERFACE = ROOT / "fixtures/vx4800/kinetics/interface-control-v1.json"
GENERATOR = ROOT / "scripts/generate_kinetic_p0.py"

_spec = importlib.util.spec_from_file_location("generate_kinetic_p0", GENERATOR)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
assert_p0_boundary = _module.assert_p0_boundary
build = _module.build


def layer_entities(modelspace, layer):
    return [entity for entity in modelspace if entity.dxf.layer == layer]


def test_p0_generator_preserves_controlled_counts_and_draws_no_interface_footprints(tmp_path):
    drawing_path, manifest_path = build(tmp_path)
    assert drawing_path.exists()
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text())
    assert manifest["status"] == "p0-interface-coordination-not-manufacturing-authority"
    assert manifest["controlledGeometry"]["suspensionLocations"] == 240
    assert manifest["controlledGeometry"]["fixedAccentHeads"] == 14
    assert manifest["physicalInterfaceFootprintsDrawn"] is False
    assert manifest["rotationAxisXYPhysicalDatumDrawn"] is False

    interface = json.loads(INTERFACE.read_text())
    assert manifest["interfaceIds"] == [item["id"] for item in interface["mechanicalInterfaces"]]
    assert manifest["tbdParameterIds"] == [item["id"] for item in interface["interfaceParameters"]]

    doc = ezdxf.readfile(drawing_path)
    model = doc.modelspace()
    cable_markers = layer_entities(model, "CONTROLLED_CABLE_EXITS")
    led_markers = layer_entities(model, "CONTROLLED_FIXED_LEDS")
    assert len(cable_markers) == 240
    assert len(led_markers) == 14
    assert all(entity.dxftype() == "CIRCLE" for entity in cable_markers)
    assert all(entity.dxftype() == "CIRCLE" for entity in led_markers)

    interface_callouts = layer_entities(model, "INTERFACE_CALLOUTS")
    tbd_callouts = layer_entities(model, "TBD_PARAMETERS")
    assert len(interface_callouts) == len(interface["mechanicalInterfaces"])
    assert len(tbd_callouts) == len(interface["interfaceParameters"])
    assert all(entity.dxftype() == "TEXT" for entity in interface_callouts)
    assert all(entity.dxftype() == "TEXT" for entity in tbd_callouts)


def test_p0_drawing_contains_authority_warning_and_no_fake_mating_geometry(tmp_path):
    drawing_path, _ = build(tmp_path)
    doc = ezdxf.readfile(drawing_path)
    model = doc.modelspace()

    notes = [entity.dxf.text for entity in layer_entities(model, "NOTES") if entity.dxftype() == "TEXT"]
    assert any("NOT MANUFACTURING AUTHORITY" in text for text in notes)
    assert any("FOOTPRINTS ARE INTENTIONALLY NOT DRAWN" in text for text in notes)
    assert any("24 mm" in text and "NOT AN AVAILABLE MECHANISM STACK HEIGHT" in text for text in notes)

    for layer in ["INTERFACE_CALLOUTS", "TBD_PARAMETERS"]:
        assert all(entity.dxftype() == "TEXT" for entity in layer_entities(model, layer))

    functional = layer_entities(model, "FUNCTIONAL_DATUM")
    assert functional
    assert all(entity.dxftype() == "TEXT" for entity in functional)
    functional_text = " ".join(entity.dxf.text for entity in functional)
    assert "XY PHYSICAL DATUM LOCATION / FEATURE TBD" in functional_text
    assert "COMPOSITION ORIGIN IS NOT SUBSTITUTED" in functional_text


def test_p0_generator_fails_closed_if_somebody_partially_freezes_interface_values():
    interface = json.loads(INTERFACE.read_text())
    assert_p0_boundary(interface)

    fake = deepcopy(interface)
    fake["interfaceParameters"][0]["status"] = "controlled"
    fake["interfaceParameters"][0]["value"] = 999
    with pytest.raises(ValueError, match="refuses partially frozen interface parameter"):
        assert_p0_boundary(fake)

    released = deepcopy(interface)
    released["finalInterfaceControlReleased"] = True
    with pytest.raises(ValueError, match="unreleased interface-control state only"):
        assert_p0_boundary(released)


def test_p0_interface_callouts_name_every_separate_mechanical_function(tmp_path):
    drawing_path, _ = build(tmp_path)
    doc = ezdxf.readfile(drawing_path)
    model = doc.modelspace()
    callout_text = " ".join(
        entity.dxf.text for entity in layer_entities(model, "INTERFACE_CALLOUTS") if entity.dxftype() == "TEXT"
    )
    for interface_id in [
        "KI-BEARING",
        "KI-DRIVE",
        "KI-BRAKE",
        "KI-SERVICE-LOCK",
        "KI-SECONDARY-RETENTION",
        "KI-FEEDBACK-PRIMARY",
        "KI-FEEDBACK-DIVERSE",
        "KI-BALANCE-TRIM",
        "KI-SERVICE-ACCESS",
    ]:
        assert interface_id in callout_text
