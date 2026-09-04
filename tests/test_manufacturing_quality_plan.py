from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "fixtures/vx4800/manufacturing/quality-plan-v1.json"
SCHEMA = ROOT / "schemas/aether-manufacturing-quality-plan.schema.json"
FIXTURE = ROOT / "fixtures/vx4800/fixture.json"
RELEASE_GATE = ROOT / "fixtures/vx4800/compliance/release-gate-v1.json"
EVIDENCE_INDEX = ROOT / "fixtures/vx4800/compliance/evidence-index-v1.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_quality_plan_schema_and_identity():
    plan = load_json(PLAN)
    schema = load_json(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(plan))
    assert not errors, [e.message for e in errors]
    assert plan["fixtureId"] == "vx4800-bf-01"
    assert plan["designRevision"] == "1.3.0"
    assert plan["authority"] == "qualification-plan"
    assert plan["status"] == "open"


def test_configuration_control_blocks_unreviewed_substitution():
    plan = load_json(PLAN)
    control = plan["configurationControl"]
    assert control["releasedBomStatus"] == "not-released"
    assert control["releasedManufacturingPackageStatus"] == "not-released"
    assert control["buildConfigurationIdRequired"] is True
    assert control["serializedFixtureRequired"] is True
    assert control["revisionTraceabilityRequired"] is True
    assert control["approvedSupplierPartIdentityRequiredForSafetyCriticalItems"] is True
    assert control["purchasingSubstitutionPermittedWithoutEngineeringReview"] is False
    assert control["commercialEquivalentIsEngineeringEquivalent"] is False
    assert control["safetyCriticalChangeRequiresEvidenceImpactReview"] is True


def test_safety_critical_traceability_groups_are_present():
    plan = load_json(PLAN)
    groups = {entry["id"]: entry for entry in plan["traceabilityGroups"]}
    for group_id in ["SUSPENSION-SYSTEM", "KINETIC-SYSTEM", "STRUCTURAL-CANOPY"]:
        assert groups[group_id]["criticality"] == "safety-critical"
    assert "BUTTERFLY-ASSEMBLIES" in groups
    assert "LIGHTING-ELECTRICAL" in groups
    assert "FINISHES" in groups


def test_controlled_composition_is_preserved_as_ctq():
    plan = load_json(PLAN)
    fixture = load_json(FIXTURE)
    ctqs = {entry["id"]: entry for entry in plan["criticalToQuality"]}
    composition = ctqs["CTQ-COMPOSITION"]
    assert composition["currentAcceptanceStatus"] == "defined"
    assert "240-element" in composition["characteristic"]
    assert "S66/M144/L30" in composition["characteristic"]
    assert fixture["composition"]["elementCount"] == 240
    assert {f["id"]: f["count"] for f in fixture["composition"]["families"]} == {"S": 66, "M": 144, "L": 30}


def test_unreleased_manufacturing_stages_and_fat_domains_do_not_claim_pass():
    plan = load_json(PLAN)
    assert all(stage["releaseStatus"] == "not-released" for stage in plan["manufacturingStages"])
    assert all(domain["status"] == "not-released" for domain in plan["factoryAcceptanceDomains"])
    assert all(domain["required"] is True for domain in plan["factoryAcceptanceDomains"])


def test_inspection_requires_controlled_criteria_and_traceability():
    plan = load_json(PLAN)
    inspection = plan["inspectionControl"]
    assert inspection["inspectionPlanRequired"] is True
    assert inspection["measurementEquipmentIdentificationRequired"] is True
    assert inspection["calibrationOrVerificationStatusRequiredWhereMeasurementAffectsAcceptance"] is True
    assert inspection["acceptanceCriteriaMustReferenceControlledRequirement"] is True
    assert inspection["inspectionResultTraceableToBuildRequired"] is True
    assert inspection["uncontrolledPassFailJudgmentPermitted"] is False


def test_nonconformance_cannot_erase_failure_or_skip_retest():
    plan = load_json(PLAN)
    ncr = plan["nonconformanceControl"]
    assert ncr["ncrRequiredForAcceptanceFailure"] is True
    assert ncr["useAsIsRequiresEngineeringApprovalWhenRequirementIsEngineeringControlled"] is True
    assert ncr["affectedQualificationEvidenceMustBeReviewed"] is True
    assert ncr["retestRequiredWhenDispositionCanAffectVerifiedRequirement"] is True
    assert ncr["ncrClosureMustNotRewriteOriginalFailure"] is True


def test_packaging_preserves_identity_and_protects_suspension_and_butterflies():
    plan = load_json(PLAN)
    pack = plan["packagingAndTransport"]
    assert pack["packPlanRequired"] is True
    assert pack["componentAndElementIdentityPreservedThroughPackaging"] is True
    assert pack["installationSequencePreservedWhereRequired"] is True
    assert pack["suspensionLinesProtectedAgainstKinkAbrasionAndUncontrolledTangling"] is True
    assert pack["butterfliesProtectedAgainstContactDamage"] is True
    assert pack["siteReceiptInspectionRequired"] is True
    assert pack["transportValidationRequirementStatus"] == "not-defined"


def test_manufacturing_plan_is_repository_evidence_not_production_validation():
    index = load_json(EVIDENCE_INDEX)
    records = {entry["id"]: entry for entry in index["records"]}
    evidence = records["EVID-REPO-MFG-QUALITY-V1"]
    assert evidence["evidenceClass"] == "REPOSITORY"
    assert evidence["sourceType"] == "repository-file"
    assert evidence["canClosePhysicalTest"] is False
    assert evidence["reference"] == "fixtures/vx4800/manufacturing/quality-plan-v1.json"
    assert "does not prove" in evidence["claim"]


def test_production_release_requires_all_manufacturing_gates():
    plan = load_json(PLAN)
    gates = plan["promotionGate"]
    prerequisites = [name for name in gates if name != "productionReleaseApproved"]
    if gates["productionReleaseApproved"]:
        assert all(gates[name] for name in prerequisites)
        assert plan["authority"] == "controlled"
        assert plan["status"] == "approved"
        assert plan["configurationControl"]["releasedBomStatus"] == "released"
        assert plan["configurationControl"]["releasedManufacturingPackageStatus"] == "released"
        assert all(stage["releaseStatus"] == "released" for stage in plan["manufacturingStages"])
    else:
        assert gates["productionReleaseApproved"] is False


def test_approved_metadata_cannot_exist_with_open_manufacturing_gates():
    plan = load_json(PLAN)
    gates = plan["promotionGate"]
    if plan["status"] == "approved" or plan["authority"] == "controlled":
        assert plan["status"] == "approved"
        assert plan["authority"] == "controlled"
        assert all(gates.values())
        assert plan["configurationControl"]["releasedBomStatus"] == "released"
        assert plan["configurationControl"]["releasedManufacturingPackageStatus"] == "released"


def test_current_manufacturing_and_global_production_release_remain_false():
    plan = load_json(PLAN)
    release = load_json(RELEASE_GATE)
    assert all(value is False for value in plan["promotionGate"].values())
    assert release["promotionGate"]["productionReleaseApproved"] is False
    assert release["promotionGate"]["firstArticleInspectionPassed"] is False
    assert release["promotionGate"]["fullFactoryPreHangPassed"] is False


def test_manufacturing_plan_preserves_external_geometry_and_physical_evidence_boundaries():
    fixture = load_json(FIXTURE)
    assert fixture["manufacturing"]["repositoryGeometryAuthority"] == "coordination-only"
    assert fixture["manufacturing"]["firstArticleRequired"] is True
    assert fixture["manufacturing"]["fullFactoryPreHangRequired"] is True
    assert fixture["manufacturing"]["actualInstalledMassRequiredBeforeConstructionRelease"] is True
