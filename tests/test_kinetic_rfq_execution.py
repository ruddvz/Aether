from copy import deepcopy
from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RESPONSE_SCHEMA = ROOT / "schemas/aether-kinetic-rfq-response.schema.json"
DISPATCH_SCHEMA = ROOT / "schemas/aether-kinetic-rfq-dispatch.schema.json"
TEMPLATE = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-response-template-v1.json"
DISPATCH = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-dispatch-register-v1.json"
RFQ = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-requirements-v1.json"


def load(path: Path):
    return json.loads(path.read_text())


def errors(instance, schema):
    return list(Draft202012Validator(schema).iter_errors(instance))


def test_rfq_execution_artifacts_validate():
    response_schema = load(RESPONSE_SCHEMA)
    dispatch_schema = load(DISPATCH_SCHEMA)
    assert not errors(load(TEMPLATE), response_schema)
    assert not errors(load(DISPATCH), dispatch_schema)


def test_dispatch_register_covers_exactly_the_six_controlled_rfq_packages():
    rfq = load(RFQ)
    dispatch = load(DISPATCH)
    requirement_ids = {item["id"] for item in rfq["supplierPackages"]}
    dispatch_ids = {item["rfqPackageId"] for item in dispatch["packages"]}
    assert requirement_ids == dispatch_ids
    assert len(dispatch_ids) == 6


def test_repository_research_is_not_misrepresented_as_external_dispatch():
    dispatch = load(DISPATCH)
    assert dispatch["status"] == "dispatch-planning"
    assert all(item["dispatchStatus"] == "not-issued" for item in dispatch["packages"])
    assert all(item["issuedDate"] is None for item in dispatch["packages"])
    assert all(item["dispatchChannelReference"] is None for item in dispatch["packages"])
    assert all(item["responseRecord"] is None for item in dispatch["packages"])


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

    fake["exactVariant"] = {
        "family": "example-family",
        "modelCode": "example-model",
        "variantCode": "example-variant",
        "configurationNotes": "schema test only; not a product candidate",
        "fullyIdentified": True,
    }
    fake["releaseGates"]["exactVariantIdentified"] = True
    fake["releaseGates"]["assumptionsDisclosed"] = True
    assert not errors(fake, schema)


def test_numeric_ratings_are_required_to_carry_condition_evidence_and_provenance_status():
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
    assert not errors(fake, schema)
    rating = fake["technicalResponse"]["numericRatings"][0]
    assert set(rating) == {"name", "value", "unit", "condition", "evidenceRef", "status"}
    assert rating["status"] != "supplier-published"


def test_dispatch_candidates_do_not_close_engineering_selection():
    dispatch_text = DISPATCH.read_text().lower()
    assert "candidate target is not an issued rfq" in dispatch_text
    assert "no dispatch state selects a component" in dispatch_text
    assert "drive application-engineering supplier target tbd" in dispatch_text
    assert "prototype precision fabricator target tbd" in dispatch_text
