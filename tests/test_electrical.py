from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "fixtures/vx4800/electrical/architecture-v1.json"
SCHEMA = ROOT / "schemas/aether-electrical-service-architecture.schema.json"
FIXTURE = ROOT / "fixtures/vx4800/fixture.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_electrical_architecture_schema_and_identity():
    architecture = load_json(ARCH)
    schema = load_json(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(architecture))
    assert not errors, [e.message for e in errors]
    assert architecture["fixtureId"] == "vx4800-bf-01"
    assert architecture["controlledInputs"]["fixedAccentHeadCount"] == 14


def test_rotating_field_has_no_planned_electrical_load():
    architecture = load_json(ARCH)
    boundary = architecture["fixedRotatingBoundary"]
    rotating = " ".join(boundary["rotatingCarrierContains"]).lower()
    assert "no planned electrical loads" in rotating
    assert boundary["slipRingStatus"] == "not-required-by-current-architecture"
    assert "new controlled rotary power/data transfer review" in boundary["changeControl"]


def test_lighting_and_kinetic_domains_are_independently_isolatable():
    architecture = load_json(ARCH)
    domains = {entry["id"]: entry for entry in architecture["electricalDomains"]}
    assert domains["LIGHTING"]["independentIsolationRequired"] is True
    assert domains["KINETIC"]["independentIsolationRequired"] is True
    assert domains["LIGHTING"]["location"] == "fixed-canopy"
    assert domains["KINETIC"]["location"] == "fixed-canopy"


def test_optical_roles_are_not_hardwired_groups():
    architecture = load_json(ARCH)
    lighting = architecture["lightingArchitecture"]
    domains = {entry["id"]: entry for entry in architecture["electricalDomains"]}
    assert "software/commissioning group intent" in domains["LIGHTING"]["notes"]
    assert "commissioning software" in lighting["controlGoal"]


def test_reference_24v_candidate_is_not_canonical_architecture():
    architecture = load_json(ARCH)
    reference = architecture["lightingArchitecture"]["referenceCandidateImplementation"]
    assert reference["status"] == "reference-only-not-canonical"
    assert reference["headInput"] == "24 V constant voltage according to current manufacturer page"
    assert architecture["controlledInputs"]["finalHeadStatus"] == "not-selected"
    assert architecture["controlledInputs"]["finalDriverTopologyStatus"] == "not-selected"


def test_bearing_cannot_be_intentional_protective_earth_path():
    architecture = load_json(ARCH)
    segregation = " ".join(architecture["serviceArchitecture"]["segregation"]).lower()
    assert "do not use the bearing as an intentional protective-earth current path" in segregation


def test_final_control_status_requires_all_promotion_gates():
    architecture = load_json(ARCH)
    gates = architecture["promotionGate"]
    if architecture["authority"] == "controlled":
        assert all(gates.values()), f"Controlled electrical architecture has open gates: {gates}"
        assert architecture["status"] == "approved"
    else:
        assert architecture["status"] != "approved"
        assert not all(gates.values())


def test_fixture_still_marks_electrical_and_photometry_conceptual():
    fixture = load_json(FIXTURE)
    assert fixture["electrical"]["status"] == "conceptual"
    assert fixture["optical"]["status"] == "conceptual"
    assert fixture["electrical"]["notes"].endswith("TBD.")
