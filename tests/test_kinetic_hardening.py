from copy import deepcopy
from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "fixtures/vx4800/kinetics/architecture-v1.json"
HARDENING = ROOT / "fixtures/vx4800/kinetics/hardening-v1.json"
STATE_MODEL = ROOT / "fixtures/vx4800/kinetics/commissioning-state-model-v1.json"
TEST_PLAN = ROOT / "fixtures/vx4800/kinetics/qualification/dynamic-test-plan-v1.json"
HARDENING_SCHEMA = ROOT / "schemas/aether-kinetic-hardening.schema.json"
STATE_SCHEMA = ROOT / "schemas/aether-kinetic-state-model.schema.json"
TEST_PLAN_SCHEMA = ROOT / "schemas/aether-kinetic-test-plan.schema.json"
TEST_RECORD_SCHEMA = ROOT / "schemas/aether-kinetic-test-record.schema.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def validate(data, schema_path: Path):
    errors = list(Draft202012Validator(load_json(schema_path)).iter_errors(data))
    assert not errors, [e.message for e in errors]


def test_hardening_state_and_test_plan_validate():
    hardening = load_json(HARDENING)
    state = load_json(STATE_MODEL)
    plan = load_json(TEST_PLAN)
    validate(hardening, HARDENING_SCHEMA)
    validate(state, STATE_SCHEMA)
    validate(plan, TEST_PLAN_SCHEMA)
    assert hardening["fixtureId"] == state["fixtureId"] == plan["fixtureId"] == "vx4800-bf-01"


def test_hardening_is_not_approved_and_schema_blocks_fake_promotion():
    hardening = load_json(HARDENING)
    gates = hardening["promotionGate"]
    assert hardening["finalHardeningApproved"] is False
    assert not any(gates.values())

    promoted = deepcopy(hardening)
    promoted["finalHardeningApproved"] = True
    errors = list(Draft202012Validator(load_json(HARDENING_SCHEMA)).iter_errors(promoted))
    assert errors, "Hardening schema must reject final approval while any hardening gate is false"


def test_architecture_final_approval_also_requires_hardening_state_and_physical_plan():
    architecture = load_json(ARCH)
    hardening = load_json(HARDENING)
    state = load_json(STATE_MODEL)
    plan = load_json(TEST_PLAN)

    promoted_architecture = deepcopy(architecture)
    promoted_architecture["finalSystemApproved"] = True
    promoted_architecture["authority"] = "controlled"
    promoted_architecture["status"] = "approved"
    promoted_architecture["promotionGate"] = {key: True for key in architecture["promotionGate"]}

    final_release_allowed = (
        promoted_architecture["finalSystemApproved"]
        and hardening["finalHardeningApproved"]
        and state["finalStateModelApproved"]
        and all(plan["promotionGate"].values())
    )
    assert final_release_allowed is False


def test_drive_transmission_failure_cannot_take_out_the_only_holding_path():
    hardening = load_json(HARDENING)
    findings = {item["id"]: item for item in hardening["designReviewFindings"]}
    faults = {item["faultId"]: item for item in hardening["faultContainmentMatrix"]}
    braking = hardening["architectureCorrections"]["braking"]

    assert findings["KHR-001"]["severity"] == "critical"
    assert "gearbox and belt/gear transmission" in findings["KHR-001"]["finding"]
    assert "directly on a passive carrier brake ring/disc" in braking["preferredStudy"]
    assert "cannot rely only on the failed transmission" in " ".join(faults["FC-004"]["requiredMechanicalContainment"])
    assert hardening["promotionGate"]["directCarrierHoldingPathResolved"] is False
    assert hardening["promotionGate"]["transmissionFailureContainmentValidated"] is False


def test_secondary_retention_common_cause_is_explicit():
    hardening = load_json(HARDENING)
    findings = {item["id"]: item for item in hardening["designReviewFindings"]}
    retention = hardening["architectureCorrections"]["secondaryRetention"]
    faults = {item["faultId"]: item for item in hardening["faultContainmentMatrix"]}

    assert findings["KHR-002"]["severity"] == "critical"
    assert "distributed" in retention["preferredStudy"]
    assert "bearing mounting fastener failure" in retention["requiredCommonCauseReview"]
    assert "hub local fracture" in retention["requiredCommonCauseReview"]
    assert faults["FC-003"]["status"] == "open"


def test_feedback_common_mode_and_brake_failure_modes_are_separate():
    hardening = load_json(HARDENING)
    findings = {item["id"]: item for item in hardening["designReviewFindings"]}
    faults = {item["faultId"]: item for item in hardening["faultContainmentMatrix"]}

    assert findings["KHR-003"]["severity"] == "major"
    assert "independent or sufficiently diverse" in hardening["architectureCorrections"]["feedback"]["overspeedStudy"]
    assert faults["FC-006"]["initiatingFailure"] == "holding/fault brake fails to release"
    assert faults["FC-007"]["initiatingFailure"] == "holding/fault brake fails to apply or loses holding force"
    assert hardening["promotionGate"]["independentOverspeedMonitoringResolved"] is False
    assert hardening["promotionGate"]["brakeStateMonitoringResolved"] is False


def test_manual_recovery_never_creates_freewheel():
    hardening = load_json(HARDENING)
    state = load_json(STATE_MODEL)
    recovery = hardening["architectureCorrections"]["manualRecovery"]
    rules = " ".join(state["manualRecoveryRules"]).lower()

    assert "no manual release creates an uncontrolled freewheel condition" in recovery["rule"]
    assert recovery["sequencePrinciple"][0] == "verify zero speed"
    assert "engage and directly verify positive service lock" in recovery["sequencePrinciple"][1]
    assert "uncontrolled free rotation" in rules


def test_service_ux_distinguishes_stopped_held_locked_and_accessible():
    state = load_json(STATE_MODEL)
    states = {item["id"]: item for item in state["states"]}

    assert states["SERVICE_LOCKED"]["accessAllowed"] is True
    assert states["ENERGISED_HELD"]["accessAllowed"] is False
    assert states["FAULT_HELD"]["accessAllowed"] is False
    assert states["RETENTION_ENGAGED"]["accessAllowed"] is False

    for item in state["states"]:
        if item["accessAllowed"]:
            conditions = " ".join(item["mechanicalConditions"]).lower()
            assert "service lock" in conditions
            assert "zero speed" in conditions

    ux = " ".join(state["operatorUxRequirements"]).lower()
    assert "stopped/held separately from mechanically locked" in ux
    assert "fault reset" in ux and "never resumes" in ux
    assert "colour-only" in ux


def test_state_model_power_restore_fault_reset_and_retention_are_non_motion_transitions():
    state = load_json(STATE_MODEL)
    transitions = state["transitions"]

    power_restore = next(t for t in transitions if t["from"] == "ISOLATED_UNLOCKED" and t["to"] == "ENERGISED_HELD")
    assert "no automatic motion command" in power_restore["permissives"]

    reset = next(t for t in transitions if t["from"] == "FAULT_HELD" and t["to"] == "ENERGISED_HELD")
    assert "reset itself does not command motion" in reset["permissives"]

    retention = next(t for t in transitions if t["to"] == "RETENTION_ENGAGED")
    assert "ordinary restart is prohibited" in retention["trigger"] or "ordinary restart is prohibited" in " ".join(retention["permissives"])


def test_motion_hardening_requires_jerk_and_physical_dynamic_correlation():
    hardening = load_json(HARDENING)
    motion = hardening["architectureCorrections"]["motionProfile"]
    dynamic = hardening["architectureCorrections"]["dynamicCalculation"]

    assert "jerk-limited" in motion["preferredCommandShape"]
    assert motion["numericAccelerationJerkAndDwell"].startswith("TBD")
    assert dynamic["rigidBodyMassMapUse"] == "screening/inertia input only"
    assert "T1-T4" in dynamic["requiredCorrelation"]


def test_bearing_mounting_and_drive_reactions_are_promoted_to_first_class_inputs():
    hardening = load_json(HARDENING)
    mounting = hardening["architectureCorrections"]["bearingMounting"]
    requirements = " ".join(mounting["requirements"]).lower()

    assert "mounting flatness" in requirements
    assert "fastener grade/count/preload" in requirements
    assert "post-mount running torque and runout" in requirements
    assert "tensioner reactions" in mounting["driveInterfaceRule"]
    assert hardening["promotionGate"]["bearingMountingJointValidated"] is False


def test_dynamic_test_plan_has_all_stages_and_critical_fault_cases():
    plan = load_json(TEST_PLAN)
    tests = {item["id"]: item for item in plan["testCases"]}
    stages = {item["stage"] for item in plan["testCases"]}

    assert stages == {"T1", "T2", "T3", "T4"}
    for test_id in ("KIN-T3-002", "KIN-T3-003", "KIN-T3-004", "KIN-T3-005", "KIN-T3-006", "KIN-T4-003", "KIN-T4-004", "KIN-T4-007", "KIN-T4-008"):
        assert test_id in tests
    assert "transmission failure" in tests["KIN-T3-002"]["purpose"]
    assert "service-lock" in tests["KIN-T3-004"]["purpose"]
    assert "secondary-retention" in tests["KIN-T3-005"]["purpose"]
    assert "manual recovery" in tests["KIN-T3-006"]["purpose"]
    assert all(item["acceptanceCriteriaStatus"] == "tbd-physical-baseline-required" for item in plan["testCases"])
    assert not any(plan["promotionGate"].values())


def test_physical_record_cannot_claim_pass_with_uncontrolled_acceptance_criteria():
    schema = load_json(TEST_RECORD_SCHEMA)
    record = {
        "schemaVersion": "1.0.0",
        "fixtureId": "vx4800-bf-01",
        "testCaseId": "KIN-T3-002",
        "recordId": "example-not-evidence",
        "configuration": {
            "designRevision": "1.3.0",
            "kineticRevision": "1.0.0",
            "articleId": "RIG-EXAMPLE",
            "configurationRefs": ["example-only"]
        },
        "performedAt": "2026-09-04T00:00:00Z",
        "operator": None,
        "equipment": [{"id": "EXAMPLE", "function": "example", "calibrationStatus": "not-applicable", "calibrationRef": None}],
        "acceptanceCriteria": {"controlled": False, "revision": None, "criteria": []},
        "measurements": [{"name": "example", "value": None}],
        "evidence": ["example-only-not-physical-evidence"],
        "result": {"status": "passed", "deviations": [], "disposition": "example"}
    }
    errors = list(Draft202012Validator(schema).iter_errors(record))
    assert errors, "A physical test record must not be able to pass before acceptance criteria are controlled"

    record["result"]["status"] = "planned"
    errors = list(Draft202012Validator(schema).iter_errors(record))
    assert not errors, [e.message for e in errors]


def test_no_rotating_power_or_slip_ring_was_introduced_by_hardening():
    architecture = load_json(ARCH)
    hardening = load_json(HARDENING)
    assert architecture["controlledBaseline"]["slipRingStatus"] == "not-required-by-current-architecture"
    assert hardening["architectureCorrections"]["feedback"]["noSlipRing"] is True
    assert "passive carrier brake ring/disc" in hardening["architectureCorrections"]["braking"]["preferredStudy"]
