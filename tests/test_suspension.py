from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SHORTLIST = ROOT / "fixtures/vx4800/suspension/qualification/shortlist-v1.json"
SCHEMA = ROOT / "schemas/aether-suspension-qualification.schema.json"
BRIEF = ROOT / "fixtures/vx4800/suspension/selection-brief.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_suspension_shortlist_schema_and_identity():
    shortlist = load_json(SHORTLIST)
    schema = load_json(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(shortlist))
    assert not errors, [e.message for e in errors]
    assert shortlist["fixtureId"] == "vx4800-bf-01"
    assert shortlist["currentArchitecture"]["lineCount"] == 240


def test_suspension_final_approval_requires_every_promotion_gate():
    shortlist = load_json(SHORTLIST)
    gates = shortlist["promotionGate"]
    if shortlist["finalSystemApproved"]:
        assert all(gates.values()), f"Final suspension approval has open gates: {gates}"
        assert shortlist["authority"] == "controlled"
        assert shortlist["status"] == "approved"
    else:
        assert shortlist["authority"] != "controlled"
        assert shortlist["status"] != "approved"


def test_suspension_current_unknown_loads_block_final_approval():
    shortlist = load_json(SHORTLIST)
    brief = load_json(BRIEF)
    assert brief["controlledInputs"]["actualElementMassStatus"] == "unknown"
    assert brief["controlledInputs"]["dynamicDesignLoadStatus"] == "unknown"
    assert shortlist["promotionGate"]["actualElementMassControlled"] is False
    assert shortlist["promotionGate"]["dynamicLineDesignLoadControlled"] is False
    assert shortlist["finalSystemApproved"] is False


def test_suspension_lower_bridle_remains_custom_engineering():
    shortlist = load_json(SHORTLIST)
    lower = shortlist["lowerBridle"]
    assert lower["status"] == "custom-engineering-required"
    assert shortlist["promotionGate"]["lowerBridleEngineered"] is False
    assert len(lower["requiredDevelopment"]) >= 6


def test_reutlinger_reference_preserves_published_static_values():
    shortlist = load_json(SHORTLIST)
    candidate = next(c for c in shortlist["candidates"] if c["candidateId"] == "reutlinger-type12-stainless")
    loads = {entry["diameterMm"]: entry["workingLoadKg"] for entry in candidate["publishedStainlessWorkingLoads"]}
    assert loads[0.81] == 6
    assert loads[1.0] == 8
    assert candidate["publishedOperatingCoefficient"] == 5
    assert candidate["status"] != "approved"


def test_griplock_reference_preserves_published_static_values():
    shortlist = load_json(SHORTLIST)
    candidate = next(c for c in shortlist["candidates"] if c["candidateId"] == "griplock-type12-1mm-stainless")
    assert candidate["publishedGripperWorkingLoad"]["stainlessWorkingLoadLb"] == 20
    assert candidate["publishedCableWorkingLoad"]["stainlessWorkingLoadLb"] == 17
    assert candidate["status"] != "approved"


def test_selection_brief_forbids_static_wll_as_kinetic_proof():
    brief = load_json(BRIEF)
    rejection_rules = " ".join(brief["rejectionRules"]).lower()
    assert "static wll" in rejection_rules
    assert "kinetic" in rejection_rules
    assert "blender" in rejection_rules
