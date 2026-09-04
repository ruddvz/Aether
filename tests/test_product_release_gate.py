from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "fixtures/vx4800/compliance/release-gate-v1.json"
SCHEMA = ROOT / "schemas/aether-product-release-gate.schema.json"
FIXTURE = ROOT / "fixtures/vx4800/fixture.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_release_gate_schema_and_identity():
    gate = load_json(GATE)
    schema = load_json(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(gate))
    assert not errors, [e.message for e in errors]
    assert gate["fixtureId"] == "vx4800-bf-01"
    assert gate["designRevision"] == "1.3.0"
    assert gate["authority"] == "qualification-plan"
    assert gate["status"] == "open"


def test_repository_validation_is_not_physical_or_certification_evidence():
    gate = load_json(GATE)
    boundary = gate["validationBoundary"]
    assert boundary["existingPackageValidationIsCertification"] is False
    assert boundary["githubCiIsPhysicalTestEvidence"] is False
    assert boundary["githubCiIsCertificationEvidence"] is False
    assert boundary["physicalQualificationRequired"] is True

    classes = {entry["id"]: entry for entry in gate["evidenceClasses"]}
    assert classes["REPOSITORY"]["canClosePhysicalTest"] is False
    assert classes["SUPPLIER"]["canClosePhysicalTest"] is False
    assert classes["ENGINEERING"]["canClosePhysicalTest"] is False
    assert classes["PHYSICAL"]["canClosePhysicalTest"] is True
    assert classes["THIRD_PARTY"]["canClosePhysicalTest"] is True


def test_standards_are_targets_not_certification_claims():
    gate = load_json(GATE)
    targets = {entry["id"]: entry for entry in gate["standardsTargets"]}
    assert all(entry["status"] == "target-applicability-review" for entry in targets.values())

    iec = {doc["standard"] for doc in targets["IEC-LUMINAIRE"]["documents"]}
    assert "IEC 60598-1:2024" in iec
    assert "IEC 60598-2-1:2025" in iec
    assert "IECEE TRF 60598-2-1L:2026" in targets["IEC-LUMINAIRE"]["testReportFramework"]

    india = {doc["standard"] for doc in targets["INDIA-FGPL"]["documents"]}
    assert "IS 10322 (Part 1):2026" in india
    assert "IS 10322 (Part 5/Sec 1):2026" in india

    north_america = {doc["standard"] for doc in targets["NORTH-AMERICA-LUMINAIRE"]["documents"]}
    assert "UL 1598" in north_america
    assert "CSA C22.2 No. 250.0-21" in north_america


def test_physical_domains_require_physical_evidence():
    gate = load_json(GATE)
    matrix = {entry["id"]: entry for entry in gate["evidenceMatrix"]}
    for requirement_id in [
        "MASS-001",
        "SUS-001",
        "MAT-001",
        "KIN-001",
        "CLR-001",
        "ELEC-TEST-001",
        "THERM-001",
        "SERVICE-001",
        "PREHANG-001",
        "FAI-001",
    ]:
        required = matrix[requirement_id]["requiredEvidence"]
        assert "PHYSICAL" in required or "THIRD_PARTY" in required, requirement_id


def test_passed_or_not_applicable_rows_require_traceable_references():
    gate = load_json(GATE)
    for entry in gate["evidenceMatrix"]:
        if entry["status"] == "passed":
            assert entry.get("evidenceRefs"), f"Passed requirement lacks evidence refs: {entry['id']}"
        if entry["status"] == "not-applicable":
            assert entry.get("deviationRefs"), f"N/A requirement lacks disposition refs: {entry['id']}"


def test_first_article_and_release_stages_are_not_released():
    gate = load_json(GATE)
    stages = {entry["id"]: entry for entry in gate["releaseStages"]}
    assert stages["FIRST_ARTICLE"]["currentStatus"] == "not-released"
    assert stages["CONSTRUCTION_RELEASE"]["currentStatus"] == "not-released"
    assert stages["PRODUCTION_RELEASE"]["currentStatus"] == "not-released"


def test_construction_release_cannot_skip_prerequisite_gates():
    gate = load_json(GATE)
    gates = gate["promotionGate"]
    construction_prerequisites = [
        "standardsApplicabilityConfirmed",
        "exactReleasedConfigurationControlled",
        "actualInstalledMassControlled",
        "rotatingMassAndCenterOfGravityControlled",
        "structuralCalculationApproved",
        "suspensionSystemQualified",
        "butterflyMaterialAttachmentQualified",
        "kineticMechanismQualified",
        "dynamicClearanceValidated",
        "electricalArchitectureControlled",
        "electricalSafetyTestsPassed",
        "thermalEnduranceTestsPassed",
        "exactPhotometryControlled",
        "fullFactoryPreHangPassed",
        "serviceabilityValidated",
        "firstArticleInspectionPassed",
        "technicalConstructionFileComplete",
    ]
    if gates["constructionReleaseApproved"]:
        assert all(gates[name] for name in construction_prerequisites)


def test_production_release_requires_construction_release_and_all_gates():
    gate = load_json(GATE)
    gates = gate["promotionGate"]
    if gates["productionReleaseApproved"]:
        assert gates["constructionReleaseApproved"] is True
        assert all(value is True for value in gates.values())


def test_current_release_approval_is_impossible_with_open_gates():
    gate = load_json(GATE)
    gates = gate["promotionGate"]
    assert gates["constructionReleaseApproved"] is False
    assert gates["productionReleaseApproved"] is False
    assert not all(gates.values())
    assert any(entry["status"] == "open" for entry in gate["evidenceMatrix"])


def test_fixture_still_does_not_claim_product_certification():
    fixture = load_json(FIXTURE)
    assert fixture["identity"]["lifecycle"] == "prototype"
    assert fixture["compliance"]["status"] == "target-defined"
    assert fixture["manufacturing"]["actualInstalledMassRequiredBeforeConstructionRelease"] is True
    assert "RFQ/prototype design, not construction release." in fixture["limitations"]
