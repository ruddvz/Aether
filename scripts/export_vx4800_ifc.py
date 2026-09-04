#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Any

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.guid

from build_interchange_loss_report import DEFAULT_FIXTURE, DEFAULT_PROFILE, build_report

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "build/vx4800/interchange/VX4800-BF-01.ifc"
DEFAULT_LOSS_REPORT = ROOT / "build/vx4800/interchange/ifc-loss-report.json"
GUID_NAMESPACE = uuid.UUID("816805c2-2278-55b1-9ab4-6ffd15bf9bbb")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def stable_ifc_guid(key: str) -> str:
    return ifcopenshell.guid.compress(uuid.uuid5(GUID_NAMESPACE, key).hex)


def set_stable_guid(entity: Any, key: str) -> None:
    if hasattr(entity, "GlobalId"):
        entity.GlobalId = stable_ifc_guid(key)


def box_mesh_from_envelope_mm(envelope_mm: list[float]) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    """Return a centred XY / drop-negative-Z box in SI metres.

    The canonical fixture uses ceiling XY with drop-positive-down. IFC uses a
    conventional +Z-up model here, so the canopy underside datum is Z=0 and
    the coordination envelope extends downward to negative Z.
    """
    width_m, depth_m, height_m = [float(value) / 1000.0 for value in envelope_mm]
    x0, x1 = -width_m / 2.0, width_m / 2.0
    y0, y1 = -depth_m / 2.0, depth_m / 2.0
    z0, z1 = -height_m, 0.0
    vertices = [
        (x0, y0, z0),
        (x1, y0, z0),
        (x1, y1, z0),
        (x0, y1, z0),
        (x0, y0, z1),
        (x1, y0, z1),
        (x1, y1, z1),
        (x0, y1, z1),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
    return vertices, faces


def create_model(fixture: dict[str, Any], loss_report: dict[str, Any]) -> ifcopenshell.file:
    if loss_report["target"] != "ifc":
        raise ValueError("IFC exporter requires an IFC loss report")
    if loss_report["summary"]["exportEligible"] is not True:
        raise ValueError("IFC loss policy does not currently permit coordination export")
    if loss_report["summary"]["exportAuthority"] != "coordination-only":
        raise ValueError("IFC export authority must remain coordination-only")
    if any(loss_report["authorityBoundary"].values()):
        raise ValueError("IFC export may not claim engineering or release authority")

    model = ifcopenshell.api.project.create_file(version="IFC4")
    identity = fixture["identity"]

    project = ifcopenshell.api.root.create_entity(
        model,
        ifc_class="IfcProject",
        name=f"AETHERIA {identity['productCode']} coordination export",
    )
    set_stable_guid(project, f"{identity['fixtureId']}:project")
    ifcopenshell.api.unit.assign_unit(model)

    model_context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body_context = ifcopenshell.api.context.add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model_context,
    )

    site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name="Coordination Site")
    building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding", name="VX4800 Coordination Context")
    storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name="Mounting Datum")
    set_stable_guid(site, f"{identity['fixtureId']}:site")
    set_stable_guid(building, f"{identity['fixtureId']}:building")
    set_stable_guid(storey, f"{identity['fixtureId']}:storey")

    ifcopenshell.api.aggregate.assign_object(model, relating_object=project, products=[site])
    ifcopenshell.api.aggregate.assign_object(model, relating_object=site, products=[building])
    ifcopenshell.api.aggregate.assign_object(model, relating_object=building, products=[storey])

    fixture_entity = ifcopenshell.api.root.create_entity(
        model,
        ifc_class="IfcLightFixture",
        predefined_type="USERDEFINED",
        name=f"{identity['brand']} {identity['name']} {identity['productCode']}",
    )
    fixture_entity.ObjectType = "KINETIC_SCULPTURAL_LIGHTING"
    fixture_entity.Tag = identity["productCode"]
    set_stable_guid(fixture_entity, f"{identity['fixtureId']}:fixture")
    ifcopenshell.api.geometry.edit_object_placement(model, product=fixture_entity)

    vertices, faces = box_mesh_from_envelope_mm(fixture["physical"]["envelopeMm"])
    representation = ifcopenshell.api.geometry.add_mesh_representation(
        model,
        context=body_context,
        vertices=[vertices],
        faces=[faces],
    )
    ifcopenshell.api.geometry.assign_representation(model, product=fixture_entity, representation=representation)
    ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[fixture_entity])

    family_counts = {family["id"]: family["count"] for family in fixture["composition"]["families"]}
    pset = ifcopenshell.api.pset.add_pset(model, product=fixture_entity, name="AETHERIA_Coordination")
    set_stable_guid(pset, f"{identity['fixtureId']}:pset:coordination")
    ifcopenshell.api.pset.edit_pset(
        model,
        pset=pset,
        properties={
            "FixtureId": identity["fixtureId"],
            "ProductCode": identity["productCode"],
            "DesignRevision": identity["designRevision"],
            "PresentationRevision": identity["presentationRevision"],
            "Lifecycle": identity["lifecycle"],
            "ExportAuthority": "coordination-only",
            "GeometryAuthority": fixture["manufacturing"]["repositoryGeometryAuthority"],
            "ElementCount": fixture["composition"]["elementCount"],
            "FamilySCount": family_counts["S"],
            "FamilyMCount": family_counts["M"],
            "FamilyLCount": family_counts["L"],
            "SuspensionLineCount": fixture["composition"]["suspension"]["lineCount"],
            "FixedHeadCount": sum(item["quantity"] for item in fixture["optical"]["emitters"]),
            "MaximumDropMm": fixture["physical"]["maximumDropMm"],
            "MassStatus": fixture["physical"]["massKg"]["status"],
            "MotionStatus": fixture["kinematics"]["status"],
            "OpticalStatus": fixture["optical"]["status"],
        },
    )

    authority = ifcopenshell.api.pset.add_pset(model, product=fixture_entity, name="AETHERIA_AuthorityBoundary")
    set_stable_guid(authority, f"{identity['fixtureId']}:pset:authority")
    ifcopenshell.api.pset.edit_pset(
        model,
        pset=authority,
        properties={
            "ManufacturingAuthority": False,
            "StructuralAuthority": False,
            "PhotometryAuthority": False,
            "KineticSafetyAuthority": False,
            "ConstructionReleaseAuthority": False,
            "LossReportTarget": loss_report["target"],
            "LossReportFixtureSha256": loss_report["source"]["fixtureSha256"],
        },
    )

    limitations = ifcopenshell.api.pset.add_pset(model, product=fixture_entity, name="AETHERIA_Limitations")
    set_stable_guid(limitations, f"{identity['fixtureId']}:pset:limitations")
    ifcopenshell.api.pset.edit_pset(
        model,
        pset=limitations,
        properties={
            f"Limitation{index + 1}": text for index, text in enumerate(fixture["limitations"])
        },
    )

    return model


def export_ifc(fixture_path: Path, profile_path: Path, output_path: Path, loss_report_path: Path) -> tuple[Path, Path]:
    fixture_path = fixture_path.resolve()
    profile_path = profile_path.resolve()
    loss_report = build_report(fixture_path, profile_path, "ifc")
    fixture = load_json(fixture_path)
    model = create_model(fixture, loss_report)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    loss_report_path.parent.mkdir(parents=True, exist_ok=True)
    model.write(str(output_path))
    loss_report_path.write_text(json.dumps(loss_report, indent=2, sort_keys=True) + "\n")
    return output_path, loss_report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export VX4800 as an IFC4 coordination-only model")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--loss-report", type=Path, default=DEFAULT_LOSS_REPORT)
    args = parser.parse_args()

    output, report = export_ifc(args.fixture, args.profile, args.output, args.loss_report)
    print(output)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
