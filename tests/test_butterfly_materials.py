from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SHORTLIST = ROOT / "fixtures/vx4800/materials/qualification/shortlist-v1.json"
BRIEF = ROOT / "fixtures/vx4800/materials/butterfly-selection-brief.json"
SCHEMA = ROOT / "schemas/aether-butterfly-material-qualification.schema.json"
GEOMETRY = ROOT / "fixtures/vx4800/geometry/parameters-v1.3.0.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_material_shortlist_schema_and_identity():
    shortlist = load_json(SHORTLIST)
    schema = load_json(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(shortlist))
    assert not errors, [e.message for e in errors]
    assert shortlist["fixtureId"] == "vx4800-bf-01"


def test_commercial_tiers_are_explicit_and_art_has_no_generic_properties():
    shortlist = load_json(SHORTLIST)
    tiers = {entry["tier"]: entry for entry in shortlist["tiers"]}
    assert {"ARC", "LUX", "ART"}.issubset(tiers)
    assert tiers["ART"]["manufacturer"] is None
    assert tiers["ART"]["publishedProperties"] is None
    assert tiers["ART"]["status"] == "supplier-required"


def test_final_material_approval_requires_every_promotion_gate():
    shortlist = load_json(SHORTLIST)
    gates = shortlist["promotionGate"]
    if shortlist["finalMaterialSystemApproved"]:
        assert all(gates.values()), f"Final material approval has open gates: {gates}"
        assert shortlist["authority"] == "controlled"
        assert shortlist["status"] == "approved"
    else:
        assert shortlist["authority"] != "controlled"
        assert shortlist["status"] != "approved"


def test_current_rfq_thicknesses_are_not_final_material_specifications():
    brief = load_json(BRIEF)
    geometry = load_json(GEOMETRY)
    assert brief["controlledContext"]["parameterStatus"].startswith("RFQ/prototype")
    assert geometry["butterflies"]["S"]["thicknessMm"] == 5
    assert geometry["butterflies"]["M"]["thicknessMm"] == 6
    assert geometry["butterflies"]["L"]["thicknessMm"] == 7
    rejection_rules = " ".join(brief["rejectionRules"]).lower()
    assert "5/6/7 mm" in rejection_rules
    assert "final material thickness" in rejection_rules


def test_mass_must_be_measured_not_derived_from_bounding_box():
    brief = load_json(BRIEF)
    requirements = " ".join(brief["massControlRequirements"]).lower()
    rejection_rules = " ".join(brief["rejectionRules"]).lower()
    assert "measure complete suspended assembly mass" in requirements
    assert "bounding-box volume" in requirements
    assert "bounding box" in rejection_rules
    assert brief["controlledContext"]["actualMassStatus"] == "unknown"


def test_published_reference_densities_stay_candidate_scoped():
    shortlist = load_json(SHORTLIST)
    tiers = {entry["candidateId"]: entry for entry in shortlist["tiers"]}
    assert tiers["plexiglas-gs-clear"]["publishedProperties"]["densityGPerCm3"] == 1.19
    assert tiers["schott-borofloat-33"]["publishedProperties"]["densityGPerCm3"] == 2.23
    assert tiers["corning-gorilla-glass-3"]["publishedProperties"]["densityGPerCm3"] == 2.39
    assert tiers["artisan-glassmaker-tbd"]["publishedProperties"] is None


def test_attachment_concepts_remain_unapproved_and_risk_controlled():
    shortlist = load_json(SHORTLIST)
    concepts = {entry["id"]: entry for entry in shortlist["attachmentConcepts"]}
    assert concepts["three-point-drilled-mechanical"]["status"] == "prototype-concept"
    assert "stress concentration" in concepts["three-point-drilled-mechanical"]["risks"]
    assert concepts["bonded-metal-pad"]["status"] == "research-only"
    assert "independent retention" in concepts["bonded-metal-pad"]["requiredControls"]
    assert shortlist["promotionGate"]["attachmentDetailFrozen"] is False
    assert shortlist["promotionGate"]["proofLoadPassed"] is False


def test_visualization_material_cannot_become_manufacturing_authority():
    brief = load_json(BRIEF)
    rejection_rules = " ".join(brief["rejectionRules"]).lower()
    attachment_principles = " ".join(brief["attachmentPrinciples"]).lower()
    assert "presentation/render material" in rejection_rules
    assert "blender" in attachment_principles
    assert brief["controlledContext"]["repositoryGeometryAuthority"] == "coordination-only"
