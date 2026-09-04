from copy import deepcopy
from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RESPONSE_SCHEMA = ROOT / "schemas/aether-kinetic-rfq-response.schema.json"
DISPATCH_SCHEMA = ROOT / "schemas/aether-kinetic-rfq-dispatch.schema.json"
CONTACT_SCHEMA = ROOT / "schemas/aether-kinetic-rfq-contact-evidence.schema.json"
TEMPLATE = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-response-template-v1.json"
DISPATCH = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-dispatch-register-v1.json"
CONTACTS = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-contact-evidence-v1.json"
RFQ = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-requirements-v1.json"


def load(path: Path):
    return json.loads(path.read_text())


def errors(instance, schema):
    return list(Draft202012Validator(schema).iter_errors(instance))


def identified_variant(fake):
    fake["exactVariant"] = {
        "family": "example-family",
        "modelCode": "example-model",
        "variantCode": "example-variant",
        "configurationNotes": "schema test only; not a product candidate",
        "fullyIdentified": True,
    }
    fake["releaseGates"]["exactVariantIdentified"] = True
    fake["releaseGates"]["assumptionsDisclosed"] = True
    return fake


def test_rfq_execution_artifacts_validate():
    response_schema = load(RESPONSE_SCHEMA)
    dispatch_schema = load(DISPATCH_SCHEMA)
    contact_schema = load(CONTACT_SCHEMA)
    assert not errors(load(TEMPLATE), response_schema)
    assert not errors(load(DISPATCH), dispatch_schema)
    assert not errors(load(CONTACTS), contact_schema)


def test_dispatch_register_covers_exactly_the_six_controlled_rfq_packages():
    rfq = load(RFQ)
    dispatch = load(DISPATCH)
    requirement_ids = {item["id"] for item in rfq["supplierPackages"]}
    dispatch_ids = {item["rfqPackageId"] for item in dispatch["packages"]}
    assert requirement_ids == dispatch_ids
    assert len(dispatch_ids) == 6


def test_ready_to_issue_is_not_misrepresented_as_external_dispatch():
    dispatch = load(DISPATCH)
    assert dispatch["status"] == "dispatch-planning"
    statuses = {item["rfqPackageId"]: item["dispatchStatus"] for item in dispatch["packages"]}
    assert statuses == {
        "RFQ-KIN-BRG-01": "ready-to-issue",
        "RFQ-KIN-DRV-01": "ready-to-issue",
        "RFQ-KIN-BELT-01": "ready-to-issue",
        "RFQ-KIN-BRK-01": "ready-to-issue",
        "RFQ-KIN-FBK-01": "ready-to-issue",
        "RFQ-KIN-FAB-01": "not-issued",
    }
    assert all(item["issuedDate"] is None for item in dispatch["packages"])
    assert all(item["dispatchChannelReference"] is None for item in dispatch["packages"])
    assert all(item["responseRecord"] is None for item in dispatch["packages"])


def test_contact_qualified_targets_are_bound_to_current_contact_evidence():
    dispatch = load(DISPATCH)
    contacts = load(CONTACTS)
    contact_ids = {record["id"] for record in contacts["records"]}
    qualified = [
        target
        for package in dispatch["packages"]
        for target in package["candidateTargets"]
        if target["targetStatus"] == "contact-qualified"
    ]
    assert len(qualified) == 5
    assert all(target["contactEvidenceRef"] in contact_ids for target in qualified)

    unresolved = [
        target
        for package in dispatch["packages"]
        for target in package["candidateTargets"]
        if target["targetStatus"] != "contact-qualified"
    ]
    assert unresolved
    assert all(target["contactEvidenceRef"] is None for target in unresolved)


def test_ready_to_issue_requires_at_least_one_contact_qualified_target():
    schema = load(DISPATCH_SCHEMA)
    fake = deepcopy(load(DISPATCH))
    bearing = next(item for item in fake["packages"] if item["rfqPackageId"] == "RFQ-KIN-BRG-01")
    for target in bearing["candidateTargets"]:
        target["targetStatus"] = "research-required"
        target["contactEvidenceRef"] = None
    assert errors(fake, schema)


def test_issued_status_requires_a_real_external_reference_and_date():
    schema = load(DISPATCH_SCHEMA)
    fake = deepcopy(load(DISPATCH))
    package = fake["packages"][0]
    package["dispatchStatus"] = "issued"
    assert errors(fake, schema), "An RFQ must not be marked issued without issue date and external channel reference"


def test_response_template_starts_with_no_variant_and_no_release_gates():
    template = load(TEMPLATE)
    assert template["responseStatus"] == "template-not-issued"
    assert template["selectionState"] == "not-selected"
    assert template["exactVariant"]["fullyIdentified"] is False
    assert template["exactVariant"]["family"] is None
    assert template["exactVariant"]["modelCode"] is None
    assert template["exactVariant"]["variantCode"] is None
    assert not any(template["releaseGates"].values())


def test_response_schema_has_no_selected_state():
    schema_text = RESPONSE_SCHEMA.read_text()
    assert '"selected"' not in schema_text
    assert '"shortlisted-not-selected"' in schema_text


def test_shortlist_candidate_requires_exact_variant_and_assumption_disclosure():
    schema = load(RESPONSE_SCHEMA)
    fake = deepcopy(load(TEMPLATE))
    fake["selectionState"] = "candidate-for-shortlist"
    assert errors(fake, schema), "Shortlist candidacy must fail without exact variant identity and assumption disclosure"

    identified_variant(fake)
    assert not errors(fake, schema)


def test_supplier_estimate_requires_a_value_unit_and_condition():
    schema = load(RESPONSE_SCHEMA)
    fake = deepcopy(load(TEMPLATE))
    fake["technicalResponse"]["numericRatings"] = [
        {
            "name": "example-rating",
            "value": 1.0,
            "unit": "example",
            "condition": None,
            "evidenceRef": None,
            "status": "supplier-estimate",
        }
    ]
    assert errors(fake, schema)

    fake["technicalResponse"]["numericRatings"][0]["condition"] = "schema-test operating condition"
    assert not errors(fake, schema)


def test_published_or_calculated_rating_requires_bound_evidence():
    schema = load(RESPONSE_SCHEMA)
    for status in ["supplier-published", "supplier-calculated"]:
        fake = deepcopy(load(TEMPLATE))
        fake["technicalResponse"]["numericRatings"] = [
            {
                "name": "example-rating",
                "value": 1.0,
                "unit": "example",
                "condition": "schema-test operating condition",
                "evidenceRef": None,
                "status": status,
            }
        ]
        assert errors(fake, schema)
        fake["technicalResponse"]["numericRatings"][0]["evidenceRef"] = "EVIDENCE-TEST-01"
        assert not errors(fake, schema)


def test_technically_comparable_state_requires_completed_review_gates():
    schema = load(RESPONSE_SCHEMA)
    fake = identified_variant(deepcopy(load(TEMPLATE)))
    fake["responseStatus"] = "technically-comparable"
    assert errors(fake, schema)

    for gate in [
        "requiredSubmittalsPresent",
        "numericRatingsVariantBound",
        "technicalReviewComplete",
        "comparisonReady",
    ]:
        fake["releaseGates"][gate] = True
    assert not errors(fake, schema)


def test_shortlisted_state_requires_technically_comparable_response():
    schema = load(RESPONSE_SCHEMA)
    fake = identified_variant(deepcopy(load(TEMPLATE)))
    fake["selectionState"] = "shortlisted-not-selected"
    for gate in [
        "requiredSubmittalsPresent",
        "numericRatingsVariantBound",
        "technicalReviewComplete",
        "comparisonReady",
    ]:
        fake["releaseGates"][gate] = True
    assert errors(fake, schema)

    fake["responseStatus"] = "technically-comparable"
    assert not errors(fake, schema)


def test_dispatch_candidates_do_not_close_engineering_selection():
    dispatch_text = DISPATCH.read_text().lower()
    assert "candidate target is not an issued rfq" in dispatch_text
    assert "no dispatch state selects a component" in dispatch_text
    assert "contact qualification proves only that a current public route exists" in dispatch_text
    assert "prototype precision fabricator target tbd" in dispatch_text
