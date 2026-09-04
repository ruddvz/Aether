from copy import deepcopy
from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RISK = ROOT / "fixtures/vx4800/kinetics/risk-register-v1.json"
RISK_SCHEMA = ROOT / "schemas/aether-kinetic-risk-register.schema.json"
ARCH = ROOT / "fixtures/vx4800/kinetics/architecture-v1.json"
HARDENING = ROOT / "fixtures/vx4800/kinetics/hardening-v1.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_risk_register_schema_and_unreleased_state():
    register = load_json(RISK)
    schema = load_json(RISK_SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(register))
    assert not errors, [e.message for e in errors]
    assert register["fixtureId"] == "vx4800-bf-01"
    assert register["finalRiskAssessmentReleased"] is False
    assert register["authority"] == "engineering-development-input"
    assert not any(register["promotionGate"].values())


def test_risk_schema_blocks_fake_release_with_open_gates():
    register = load_json(RISK)
    promoted = deepcopy(register)
    promoted["finalRiskAssessmentReleased"] = True
    errors = list(Draft202012Validator(load_json(RISK_SCHEMA)).iter_errors(promoted))
    assert errors, "Risk register schema must reject final release while required risk gates are false"


def test_no_sil_pl_or_category_is_invented():
    register = load_json(RISK)
    scope = " ".join(register["scopeBoundary"]["notClaims"]).lower()
    assert "no pl, sil, category" in scope
    for candidate in register["safetyRelatedFunctionCandidates"]:
        assert candidate["performanceLevelOrSil"] is None
        assert candidate["allocationStatus"] == "candidate-function-risk-assessment-pending"


def test_current_iso_references_are_inputs_not_compliance_claims():
    register = load_json(RISK)
    refs = {item["reference"]: item for item in register["standardsInputs"]}
    assert "ISO 12100:2010" in refs
    assert "ISO 13850:2015" in refs
    assert "applicability-review" in refs["ISO 12100:2010"]["status"]
    assert "does not by itself define" in refs["ISO 13850:2015"]["scopeNote"]


def test_major_mechanical_hazard_families_are_present():
    register = load_json(RISK)
    hazards = {item["id"]: item for item in register["hazards"]}
    required = {"KR-001", "KR-002", "KR-003", "KR-004", "KR-005", "KR-006", "KR-007", "KR-008", "KR-009", "KR-010", "KR-011", "KR-012", "KR-013", "KR-014", "KR-015", "KR-016"}
    assert required.issubset(hazards)
    assert "fall or major downward displacement" in hazards["KR-001"]["hazard"]
    assert "unexpected start" in hazards["KR-003"]["hazard"]
    assert "uncontrolled or excessive carrier speed" in hazards["KR-004"]["hazard"]
    assert "pinch, shear or trapping" in hazards["KR-005"]["hazard"]
    assert "manual brake/drive release" in hazards["KR-008"]["hazard"]
    assert "fault stop or power-loss stop" in hazards["KR-014"]["hazard"]


def test_risk_register_consumes_other_engineering_tracks_without_stealing_authority():
    register = load_json(RISK)
    interfaces = " ".join(register["scopeBoundary"]["interfaces"]).lower()
    assert "issue #7" in interfaces
    assert "issue #9" in interfaces
    assert "issue #11" in interfaces

    hazards = {item["id"]: item for item in register["hazards"]}
    assert "issue #9" in " ".join(hazards["KR-011"]["existingDesignMeasures"]).lower()
    assert "issue #7" in " ".join(hazards["KR-012"]["existingDesignMeasures"]).lower()
    assert "issue #11" in " ".join(hazards["KR-013"]["furtherAssessmentRequired"]).lower()


def test_final_kinetic_release_requires_separate_risk_release_in_repository_logic():
    architecture = load_json(ARCH)
    hardening = load_json(HARDENING)
    register = load_json(RISK)

    simulated_arch = deepcopy(architecture)
    simulated_arch["finalSystemApproved"] = True
    simulated_arch["promotionGate"] = {key: True for key in simulated_arch["promotionGate"]}
    simulated_hardening = deepcopy(hardening)
    simulated_hardening["finalHardeningApproved"] = True
    simulated_hardening["promotionGate"] = {key: True for key in simulated_hardening["promotionGate"]}

    final_release_allowed = simulated_arch["finalSystemApproved"] and simulated_hardening["finalHardeningApproved"] and register["finalRiskAssessmentReleased"]
    assert final_release_allowed is False


def test_emergency_stop_behavior_stays_open_until_risk_assessment():
    register = load_json(RISK)
    assert register["promotionGate"]["emergencyStopNeedAndBehaviorResolved"] is False
    assert register["promotionGate"]["safetyRelatedControlFunctionsAllocated"] is False
    hazard = next(item for item in register["hazards"] if item["id"] == "KR-014")
    assert "approved stop profiles" in hazard["furtherAssessmentRequired"]
