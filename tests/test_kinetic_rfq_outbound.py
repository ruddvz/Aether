from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-outbound-manifest-v1.json"
SCHEMA = ROOT / "schemas/aether-kinetic-rfq-outbound.schema.json"
DISPATCH = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-dispatch-register-v1.json"
CONTACTS = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-contact-evidence-v1.json"


def load(path: Path):
    return json.loads(path.read_text())


def test_outbound_manifest_validates_and_covers_all_six_rfq_packages():
    manifest = load(MANIFEST)
    schema = load(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(manifest))
    assert not errors, [error.message for error in errors]
    assert manifest["status"] == "prepared-not-sent"
    assert {item["rfqPackageId"] for item in manifest["documents"]} == {
        "RFQ-KIN-BRG-01",
        "RFQ-KIN-DRV-01",
        "RFQ-KIN-BELT-01",
        "RFQ-KIN-BRK-01",
        "RFQ-KIN-FBK-01",
        "RFQ-KIN-FAB-01",
    }


def test_every_outbound_document_exists_and_is_explicitly_not_sent():
    manifest = load(MANIFEST)
    for item in manifest["documents"]:
        path = ROOT / item["documentPath"]
        assert path.exists(), item["documentPath"]
        text = path.read_text()
        assert item["rfqPackageId"] in text
        assert "Status: **prepared-not-sent**" in text
        assert "Engineering boundary" in text
        assert item["outboundStatus"] == "prepared-not-sent"
        assert item["unknownsNotToInvent"]


def test_outbound_targets_and_contact_references_match_controlled_dispatch_state():
    manifest = load(MANIFEST)
    dispatch = load(DISPATCH)
    contacts = load(CONTACTS)
    contact_ids = {item["id"] for item in contacts["records"]}
    dispatch_by_id = {item["rfqPackageId"]: item for item in dispatch["packages"]}

    for outbound in manifest["documents"]:
        package = dispatch_by_id[outbound["rfqPackageId"]]
        assert package["dispatchStatus"] == "ready-to-issue"
        assert package["issuedDate"] is None
        assert package["dispatchChannelReference"] is None
        controlled_names = {target["name"] for target in package["candidateTargets"]}
        assert outbound["primaryTarget"] in controlled_names
        assert set(outbound["alternateTargets"]).issubset(controlled_names)
        assert set(outbound["contactEvidenceRefs"]).issubset(contact_ids)


def test_outbound_preparation_does_not_mutate_dispatch_into_issued_state():
    dispatch = load(DISPATCH)
    assert all(item["dispatchStatus"] == "ready-to-issue" for item in dispatch["packages"])
    assert all(item["issuedDate"] is None for item in dispatch["packages"])
    assert all(item["dispatchChannelReference"] is None for item in dispatch["packages"])
    assert all(item["responseRecord"] is None for item in dispatch["packages"])


def test_outbound_drafts_preserve_known_unknowns_instead_of_claiming_final_sizing():
    manifest = load(MANIFEST)
    joined = "\n".join((ROOT / item["documentPath"]).read_text().lower() for item in manifest["documents"])
    required_open_concepts = [
        "total installed rotating mass",
        "drive torque",
        "stopping energy",
        "final position resolution",
        "proof load",
    ]
    for phrase in required_open_concepts:
        assert phrase in joined
    assert "prepared-not-sent" in joined
    assert "no brake model" in joined
    assert "no drive variant" in joined
    assert "no encoder family" in joined
    assert "no manufacturing geometry or proof load is released" in joined
