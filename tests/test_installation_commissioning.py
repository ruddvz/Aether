from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "fixtures/vx4800/installation/commissioning-plan-v1.json"
SCHEMA = ROOT / "schemas/aether-installation-commissioning-plan.schema.json"
FIXTURE = ROOT / "fixtures/vx4800/fixture.json"
RELEASE_GATE = ROOT / "fixtures/vx4800/compliance/release-gate-v1.json"
EVIDENCE_INDEX = ROOT / "fixtures/vx4800/compliance/evidence-index-v1.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_installation_plan_schema_and_identity():
    plan = load_json(PLAN)
    schema = load_json(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(plan))
    assert not errors, [e.message for e in errors]
    assert plan["fixtureId"] == "vx4800-bf-01"
    assert plan["designRevision"] == "1.3.0"
    assert plan["authority"] == "qualification-plan"
    assert plan["status"] == "open"


def test_factory_acceptance_and_visual_assets_are_not_site_acceptance():
    plan = load_json(PLAN)
    b = plan["boundaries"]
    assert b["factoryAcceptanceIsSiteAcceptance"] is False
    assert b["coordinationCadIsInstallationAuthority"] is False
    assert b["blenderIsInstallationAuthority"] is False
    assert b["falseCeilingCanSupportFixture"] is False
    assert b["siteStructuralApprovalRequiredBeforePermanentLoadTransfer"] is True


def test_controlled_product_baseline_is_preserved():
    plan = load_json(PLAN)
    fixture = load_json(FIXTURE)
    baseline = plan["controlledBaseline"]
    assert baseline["elementCount"] == fixture["composition"]["elementCount"] == 240
    assert baseline["sizeAllocation"] == {"S": 66, "M": 144, "L": 30}
    assert baseline["fixedAccentHeadCount"] == 14
    assert baseline["interfaceZoneCount"] == fixture["physical"]["mounting"]["interfaceZoneCount"] == 8
    assert baseline["lightingLocation"] == "fixed-canopy"
    assert baseline["rotatingFieldPlannedElectricalLoads"] is False


def test_all_site_stages_and_preconditions_are_unreleased():
    plan = load_json(PLAN)
    assert all(stage["releaseStatus"] == "not-released" for stage in plan["siteStages"])
    assert all(entry["status"] == "open" for entry in plan["preconditions"])


def test_physical_site_domains_require_physical_evidence():
    plan = load_json(PLAN)
    evidence = {entry["id"]: entry for entry in plan["installationEvidence"]}
    for evidence_id in [
        "INST-RECEIPT",
        "INST-STRUCTURE",
        "INST-CONFIGURATION",
        "INST-ELECTRICAL",
        "INST-LIGHTING",
        "INST-KINETIC",
        "INST-CLEARANCE",
        "INST-HANDOVER",
    ]:
        assert "PHYSICAL" in evidence[evidence_id]["requiredEvidence"], evidence_id
        assert evidence[evidence_id]["status"] == "open"


def test_site_change_control_blocks_unsafe_workarounds():
    plan = load_json(PLAN)
    c = plan["siteChangeControl"]
    assert c["siteDeviationRegisterRequired"] is True
    assert c["engineeringApprovalRequiredForControlledRequirementDeviation"] is True
    assert c["substitutionWithoutEvidenceImpactReviewPermitted"] is False
    assert c["fieldDrillingCuttingOrReworkingSafetyCriticalPartsWithoutApprovalPermitted"] is False
    assert c["softwareLimitExpansionWithoutEngineeringApprovalPermitted"] is False
    assert c["structuralSupportChangeRequiresReanalysis"] is True
    assert c["kineticGeometryOrMassChangeRequiresDynamicImpactReview"] is True
    assert c["headDriverOrControlGearChangeRequiresElectricalPhotometricImpactReview"] is True
    assert c["failedCommissioningTestRequiresDispositionAndRetest"] is True


def test_handover_requires_as_installed_service_baseline():
    plan = load_json(PLAN)
    records = plan["baselineRecords"]
    for key in [
        "fixtureSerialRequired",
        "buildConfigurationIdRequired",
        "projectSiteIdRequired",
        "structuralApprovalReferenceRequired",
        "siteDeviationRegisterRequired",
        "installedComponentTraceabilityRequired",
        "lightingCommissioningRecordRequired",
        "kineticCommissioningRecordRequired",
        "finalInspectionRecordRequired",
        "photographicConditionRecordRequired",
        "operatorServiceHandoverRecordRequired",
        "firstInspectionDueDateRequired",
    ]:
        assert records[key] is True


def test_installation_release_cannot_skip_prerequisites():
    plan = load_json(PLAN)
    gates = plan["promotionGate"]
    prerequisites = [name for name in gates if name != "installationCommissioningReleaseApproved"]
    if gates["installationCommissioningReleaseApproved"]:
        assert all(gates[name] for name in prerequisites)
        assert plan["authority"] == "controlled"
        assert plan["status"] == "approved"
        assert all(stage["releaseStatus"] == "released" for stage in plan["siteStages"])
    else:
        assert gates["installationCommissioningReleaseApproved"] is False


def test_current_site_release_is_open_and_global_product_release_stays_open():
    plan = load_json(PLAN)
    release = load_json(RELEASE_GATE)
    assert all(value is False for value in plan["promotionGate"].values())
    assert release["promotionGate"]["constructionReleaseApproved"] is False
    assert release["promotionGate"]["productionReleaseApproved"] is False


def test_installation_plan_is_registered_only_as_repository_evidence():
    index = load_json(EVIDENCE_INDEX)
    record = next((r for r in index["records"] if r["id"] == "EVID-REPO-INSTALL-COMMISSION-V1"), None)
    assert record is not None
    assert record["evidenceClass"] == "REPOSITORY"
    assert record["canClosePhysicalTest"] is False
    assert record["reference"] == "fixtures/vx4800/installation/commissioning-plan-v1.json"


def test_any_future_passed_evidence_ref_resolves_through_controlled_index():
    plan = load_json(PLAN)
    index = load_json(EVIDENCE_INDEX)
    known = {record["id"]: record for record in index["records"]}
    for entry in plan["installationEvidence"]:
        if entry["status"] == "passed":
            assert entry.get("evidenceRefs")
            for ref in entry["evidenceRefs"]:
                assert ref in known, f"Dangling installation evidence reference: {ref}"
            if "PHYSICAL" in entry["requiredEvidence"]:
                assert any(known[ref]["evidenceClass"] in {"PHYSICAL", "THIRD_PARTY"} for ref in entry["evidenceRefs"])
