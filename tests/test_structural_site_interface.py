from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "fixtures/vx4800/structural/interface-brief-v1.json"
SCHEMA = ROOT / "schemas/aether-structural-site-interface.schema.json"
FIXTURE = ROOT / "fixtures/vx4800/fixture.json"
RELEASE_GATE = ROOT / "fixtures/vx4800/compliance/release-gate-v1.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_structural_interface_schema_and_identity():
    brief = load_json(BRIEF)
    schema = load_json(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(brief))
    assert not errors, [e.message for e in errors]
    assert brief["fixtureId"] == "vx4800-bf-01"
    assert brief["designRevision"] == "1.3.0"
    assert brief["authority"] == "qualification-plan"
    assert brief["status"] == "open"


def test_structural_baseline_matches_fixture_without_promoting_unknown_mass():
    brief = load_json(BRIEF)
    fixture = load_json(FIXTURE)
    baseline = brief["controlledBaseline"]
    mounting = fixture["physical"]["mounting"]

    assert baseline["canopyEnvelopeMm"] == fixture["physical"]["canopyEnvelopeMm"]
    assert baseline["interfaceZoneCount"] == mounting["interfaceZoneCount"] == 8
    assert baseline["siteStructuralDesignRequired"] is True
    assert fixture["physical"]["massKg"]["status"] == "unknown"


def test_exactly_eight_interface_zone_ids_exist_without_reactions():
    brief = load_json(BRIEF)
    zones = brief["interfaceZones"]
    assert len(zones) == 8
    assert [zone["id"] for zone in zones] == [f"SITE-IF-{i:02d}" for i in range(1, 9)]
    assert all(zone["positionStatus"] == "manufacturing-interface-geometry-required" for zone in zones)
    assert all(zone["reactionStatus"] == "not-calculated" for zone in zones)
    assert brief["reactionOutputs"]["currentStatus"] == "no-numeric-reactions-approved"


def test_no_false_ceiling_decorative_skin_or_services_are_structural_support():
    brief = load_json(BRIEF)
    boundary = brief["supportBoundary"]
    assert boundary["falseCeilingStructuralSupportPermitted"] is False
    assert boundary["decorativeCanopySkinStructuralSupportPermitted"] is False
    assert boundary["servicesAsStructuralSupportPermitted"] is False
    assert boundary["siteStructureMustBeIdentifiedBeforeAnchorSelection"] is True
    assert boundary["anchorSelectionIsProjectSpecific"] is True
    assert boundary["secondaryRetentionMustTerminateToValidFixedStructure"] is True


def test_unknown_product_and_site_inputs_remain_unknown():
    brief = load_json(BRIEF)
    product = {entry["id"]: entry for entry in brief["requiredProductInputs"]}
    site = {entry["id"]: entry for entry in brief["requiredSiteInputs"]}

    for key in [
        "TOTAL-INSTALLED-MASS",
        "ROTATING-MASS",
        "CENTER-OF-GRAVITY",
        "NORMAL-MOTION-REACTIONS",
        "FAULT-STOP-REACTIONS",
        "IMBALANCE-REACTIONS",
        "SECONDARY-RETENTION-ENGAGEMENT",
    ]:
        assert product[key]["status"] == "unknown"

    assert all(entry["status"] == "unknown" for entry in site.values())


def test_all_required_structural_load_cases_are_uncomputed():
    brief = load_json(BRIEF)
    cases = {entry["id"]: entry for entry in brief["requiredLoadCases"]}
    expected = {
        "LC-DEAD",
        "LC-NORMAL-MOTION",
        "LC-NORMAL-STOP",
        "LC-FAULT-STOP",
        "LC-IMBALANCE",
        "LC-SECONDARY-RETENTION",
        "LC-SERVICE",
        "LC-INSTALLATION",
    }
    assert expected <= set(cases)
    assert all(entry["status"] == "not-calculated" for entry in cases.values())


def test_equal_eighth_reaction_sharing_and_premature_anchor_selection_are_forbidden():
    brief = load_json(BRIEF)
    text = " ".join(brief["forbiddenAssumptions"]).lower()
    requirements = " ".join(brief["analysisRequirements"]).lower()
    assert "eight interface zones share reactions equally" in text
    assert "select anchors from a catalog before actual substrate" in text
    assert "without assuming equal 1/8 sharing" in requirements


def test_project_structural_release_requires_all_prerequisite_gates():
    brief = load_json(BRIEF)
    gates = brief["promotionGate"]
    prerequisites = [name for name in gates if name != "projectStructuralReleaseApproved"]
    if gates["projectStructuralReleaseApproved"]:
        assert all(gates[name] for name in prerequisites)
        assert brief["authority"] == "controlled"
        assert brief["status"] == "approved"
        assert brief["reactionOutputs"]["currentStatus"] == "approved"
        assert all(zone["positionStatus"] == "controlled" for zone in brief["interfaceZones"])
        assert all(zone["reactionStatus"] == "approved" for zone in brief["interfaceZones"])
    else:
        assert gates["projectStructuralReleaseApproved"] is False
        assert not all(gates[name] for name in prerequisites)


def test_approved_metadata_cannot_exist_with_open_structural_gates():
    brief = load_json(BRIEF)
    gates = brief["promotionGate"]
    if brief["status"] == "approved" or brief["authority"] == "controlled":
        assert brief["status"] == "approved"
        assert brief["authority"] == "controlled"
        assert all(gates.values())
        assert brief["reactionOutputs"]["currentStatus"] == "approved"


def test_current_structural_release_and_global_release_gate_remain_open():
    brief = load_json(BRIEF)
    release = load_json(RELEASE_GATE)
    assert all(value is False for value in brief["promotionGate"].values())
    assert release["promotionGate"]["structuralCalculationApproved"] is False
    assert release["promotionGate"]["constructionReleaseApproved"] is False
    assert release["promotionGate"]["productionReleaseApproved"] is False


def test_structural_interface_does_not_change_kinetic_or_geometry_authority():
    brief = load_json(BRIEF)
    baseline = brief["controlledBaseline"]
    assert baseline["repositoryGeometryAuthority"] == "coordination-only"
    assert "external controlled" in baseline["manufacturingGeometryAuthority"]
    dependencies = " ".join(brief["dependencies"]).lower()
    assert "rotating-carrier engineering track" in dependencies
