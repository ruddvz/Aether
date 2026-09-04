from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ifcopenshell = pytest.importorskip("ifcopenshell")
util_element = pytest.importorskip("ifcopenshell.util.element")

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SCRIPT_PATH = SCRIPTS / "export_vx4800_ifc.py"
FIXTURE_PATH = ROOT / "fixtures/vx4800/fixture.json"
PROFILE_PATH = ROOT / "fixtures/vx4800/interchange/export-profile-v1.json"

spec = importlib.util.spec_from_file_location("export_vx4800_ifc", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def get_fixture(model):
    fixtures = model.by_type("IfcLightFixture")
    assert len(fixtures) == 1
    return fixtures[0]


def test_ifc4_model_has_expected_spatial_and_fixture_structure():
    fixture = json.loads(FIXTURE_PATH.read_text())
    loss_report = module.build_report(FIXTURE_PATH, PROFILE_PATH, "ifc")
    model = module.create_model(fixture, loss_report)

    assert model.schema == "IFC4"
    assert len(model.by_type("IfcProject")) == 1
    assert len(model.by_type("IfcSite")) == 1
    assert len(model.by_type("IfcBuilding")) == 1
    assert len(model.by_type("IfcBuildingStorey")) == 1

    entity = get_fixture(model)
    assert entity.Name == "AETHERIA VORTEX VX4800-BF-01"
    assert entity.Tag == "VX4800-BF-01"
    assert entity.ObjectType == "KINETIC_SCULPTURAL_LIGHTING"
    assert str(entity.PredefinedType) == "USERDEFINED"
    assert entity.ContainedInStructure
    assert entity.ContainedInStructure[0].RelatingStructure.is_a("IfcBuildingStorey")


def test_coordination_property_sets_preserve_controlled_counts_and_boundaries():
    fixture = json.loads(FIXTURE_PATH.read_text())
    loss_report = module.build_report(FIXTURE_PATH, PROFILE_PATH, "ifc")
    model = module.create_model(fixture, loss_report)
    entity = get_fixture(model)
    psets = util_element.get_psets(entity)

    coordination = psets["AETHERIA_Coordination"]
    assert coordination["FixtureId"] == "vx4800-bf-01"
    assert coordination["ProductCode"] == "VX4800-BF-01"
    assert coordination["DesignRevision"] == "1.3.0"
    assert coordination["PresentationRevision"] == "5.2.0"
    assert coordination["ExportAuthority"] == "coordination-only"
    assert coordination["GeometryAuthority"] == "coordination-only"
    assert coordination["ElementCount"] == 240
    assert coordination["FamilySCount"] == 66
    assert coordination["FamilyMCount"] == 144
    assert coordination["FamilyLCount"] == 30
    assert coordination["SuspensionLineCount"] == 240
    assert coordination["FixedHeadCount"] == 14
    assert coordination["MaximumDropMm"] == 4800
    assert coordination["MassStatus"] == "unknown"
    assert "MassKg" not in coordination

    authority = psets["AETHERIA_AuthorityBoundary"]
    assert authority["ManufacturingAuthority"] is False
    assert authority["StructuralAuthority"] is False
    assert authority["PhotometryAuthority"] is False
    assert authority["KineticSafetyAuthority"] is False
    assert authority["ConstructionReleaseAuthority"] is False
    assert authority["LossReportTarget"] == "ifc"
    expected_sha = hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()
    assert authority["LossReportFixtureSha256"] == expected_sha


def test_coordination_envelope_is_2500_by_1650_by_4800_mm():
    fixture = json.loads(FIXTURE_PATH.read_text())
    loss_report = module.build_report(FIXTURE_PATH, PROFILE_PATH, "ifc")
    model = module.create_model(fixture, loss_report)
    entity = get_fixture(model)

    representation = entity.Representation.Representations[0]
    assert representation.RepresentationIdentifier == "Body"
    item = representation.Items[0]
    assert item.is_a("IfcPolygonalFaceSet")
    coords = [tuple(float(value) for value in row) for row in item.Coordinates.CoordList]
    mins = [min(row[index] for row in coords) for index in range(3)]
    maxs = [max(row[index] for row in coords) for index in range(3)]
    extents = [maxs[index] - mins[index] for index in range(3)]
    assert extents == pytest.approx([2500.0, 1650.0, 4800.0], abs=1e-6)
    assert mins[2] == pytest.approx(-4800.0, abs=1e-6)
    assert maxs[2] == pytest.approx(0.0, abs=1e-6)


def test_export_round_trip_reopens_with_same_semantics(tmp_path):
    output = tmp_path / "VX4800-BF-01.ifc"
    report = tmp_path / "ifc-loss-report.json"
    module.export_ifc(FIXTURE_PATH, PROFILE_PATH, output, report)

    reopened = ifcopenshell.open(str(output))
    entity = get_fixture(reopened)
    psets = util_element.get_psets(entity)
    assert reopened.schema == "IFC4"
    assert psets["AETHERIA_Coordination"]["ElementCount"] == 240
    assert psets["AETHERIA_AuthorityBoundary"]["ConstructionReleaseAuthority"] is False

    loss = json.loads(report.read_text())
    assert loss["summary"]["exportEligible"] is True
    assert loss["summary"]["exportAuthority"] == "coordination-only"
    assert loss["summary"]["blockingLosses"] == 0


def test_primary_entity_guids_are_stable_across_rebuilds():
    fixture = json.loads(FIXTURE_PATH.read_text())
    loss_report = module.build_report(FIXTURE_PATH, PROFILE_PATH, "ifc")
    first = module.create_model(fixture, loss_report)
    second = module.create_model(fixture, loss_report)

    assert first.by_type("IfcProject")[0].GlobalId == second.by_type("IfcProject")[0].GlobalId
    assert get_fixture(first).GlobalId == get_fixture(second).GlobalId
    first_psets = {pset.Name: pset.GlobalId for pset in first.by_type("IfcPropertySet")}
    second_psets = {pset.Name: pset.GlobalId for pset in second.by_type("IfcPropertySet")}
    assert first_psets == second_psets


def test_ifc_export_refuses_noneligible_or_authority_escalated_loss_report():
    fixture = json.loads(FIXTURE_PATH.read_text())
    blocked = module.build_report(FIXTURE_PATH, PROFILE_PATH, "ifc")
    blocked["summary"]["exportEligible"] = False
    with pytest.raises(ValueError, match="does not currently permit"):
        module.create_model(fixture, blocked)

    escalated = module.build_report(FIXTURE_PATH, PROFILE_PATH, "ifc")
    escalated["authorityBoundary"]["manufacturingAuthority"] = True
    with pytest.raises(ValueError, match="may not claim"):
        module.create_model(fixture, escalated)
