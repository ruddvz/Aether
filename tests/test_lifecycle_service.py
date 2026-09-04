from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "fixtures/vx4800/service/lifecycle-plan-v1.json"
SCHEMA = ROOT / "schemas/aether-lifecycle-service-plan.schema.json"
EVIDENCE_INDEX = ROOT / "fixtures/vx4800/compliance/evidence-index-v1.json"
INSTALL = ROOT / "fixtures/vx4800/installation/commissioning-plan-v1.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_lifecycle_plan_schema_and_identity():
    plan = load_json(PLAN)
    schema = load_json(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(plan))
    assert not errors, [e.message for e in errors]
    assert plan["fixtureId"] == "vx4800-bf-01"
    assert plan["designRevision"] == "1.3.0"
    assert plan["authority"] == "qualification-plan"
    assert plan["status"] == "open"


def test_service_intervals_and_lives_are_not_invented():
    plan = load_json(PLAN)
    b = plan["boundaries"]
    assert b["genericFixedMaintenanceIntervalsApproved"] is False
    assert b["genericLubricationIntervalApproved"] is False
    assert b["genericSafetyCriticalReplacementLifeApproved"] is False
    assert plan["intervalRelease"]["currentIntervalStatus"] == "not-released"
    assert all(domain["intervalStatus"] == "not-defined" for domain in plan["inspectionDomains"])


def test_service_requires_commissioned_baseline_and_controlled_return_to_service():
    plan = load_json(PLAN)
    assert plan["boundaries"]["commissionedAsInstalledBaselineRequired"] is True
    assert plan["serviceBaseline"]["status"] == "not-established"
    assert plan["boundaries"]["returnToServiceRequiresAffectedVerification"] is True
    assert plan["boundaries"]["serviceWorkMayBypassMechanicalServiceLock"] is False


def test_safety_critical_domains_and_event_inspections_exist():
    plan = load_json(PLAN)
    domains = {d["id"]: d for d in plan["inspectionDomains"]}
    for domain_id in ["STRUCTURE-INTERFACE", "SUSPENSION", "KINETIC-SYSTEM", "ELECTRICAL-LIGHTING"]:
        assert domains[domain_id]["criticality"] == "safety-critical"
    events = {e["id"]: e for e in plan["eventTriggeredInspection"]}
    for event_id in ["ABNORMAL-STOP", "PHYSICAL-CONTACT", "STRUCTURAL-EVENT", "WATER-CONTAMINATION", "UNAUTHORIZED-CHANGE", "MAJOR-SERVICE"]:
        assert events[event_id]["required"] is True


def test_maintenance_and_spares_block_uncontrolled_substitution():
    plan = load_json(PLAN)
    m = plan["maintenanceControl"]
    s = plan["sparesControl"]
    assert m["releasedProcedureRequiredForSafetyCriticalWork"] is True
    assert m["authorizedPersonnelRequired"] is True
    assert m["replacementPartIdentityRecorded"] is True
    assert m["serviceDeviationRegisterRequired"] is True
    assert m["originalFailureHistoryMustBePreserved"] is True
    assert s["exactQualifiedIdentityRequiredForSafetyCriticalSpares"] is True
    assert s["obsoletePartSubstitutionRequiresEngineeringReview"] is True
    assert s["uncontrolledCannibalizationPermitted"] is False
    assert s["replacementButterflyMassBalanceImpactReviewRequired"] is True
    assert s["lightingReplacementPhotometricElectricalEquivalenceReviewRequired"] is True
    assert s["kineticReplacementQualificationImpactReviewRequired"] is True


def test_post_service_verification_covers_all_affected_domains():
    plan = load_json(PLAN)
    verification = {v["id"]: v for v in plan["postServiceVerification"]}
    assert set(verification) >= {"CONFIGURATION", "MECHANICAL", "ELECTRICAL", "KINETIC", "CLEARANCE", "LIGHTING", "BASELINE"}
    assert all(v["required"] is True for v in verification.values())


def test_fault_and_service_history_is_preserved():
    plan = load_json(PLAN)
    history = plan["faultAndHistory"]
    assert all(history.values())
    assert plan["maintenanceControl"]["originalFailureHistoryMustBePreserved"] is True


def test_interval_release_requires_supplier_test_and_duty_cycle_inputs():
    plan = load_json(PLAN)
    i = plan["intervalRelease"]
    assert i["initialIntervalsRequireSelectedComponentManufacturerInputs"] is True
    assert i["initialIntervalsRequireQualificationTestInputs"] is True
    assert i["initialIntervalsRequireCommissionedDutyCycle"] is True
    assert i["fieldHistoryMayShortenInterval"] is True
    assert i["intervalMayBeExtendedWithoutEngineeringReview"] is False


def test_lifecycle_approval_cannot_skip_prerequisites():
    plan = load_json(PLAN)
    gates = plan["promotionGate"]
    prerequisites = [name for name in gates if name != "lifecycleServicePlanApproved"]
    if gates["lifecycleServicePlanApproved"]:
        assert all(gates[name] for name in prerequisites)
        assert plan["authority"] == "controlled"
        assert plan["status"] == "approved"
        assert plan["serviceBaseline"]["status"] == "controlled"
        assert plan["intervalRelease"]["currentIntervalStatus"] == "released"
    else:
        assert gates["lifecycleServicePlanApproved"] is False
        assert not all(gates[name] for name in prerequisites)


def test_current_lifecycle_and_installation_baselines_remain_open():
    plan = load_json(PLAN)
    install = load_json(INSTALL)
    assert all(value is False for value in plan["promotionGate"].values())
    assert install["promotionGate"]["installationCommissioningReleaseApproved"] is False


def test_lifecycle_plan_is_repository_evidence_only():
    index = load_json(EVIDENCE_INDEX)
    record = next((r for r in index["records"] if r["id"] == "EVID-REPO-LIFECYCLE-SERVICE-V1"), None)
    assert record is not None
    assert record["evidenceClass"] == "REPOSITORY"
    assert record["canClosePhysicalTest"] is False
    assert record["reference"] == "fixtures/vx4800/service/lifecycle-plan-v1.json"
