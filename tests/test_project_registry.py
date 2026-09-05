from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COLLECTION_IDS = {"FLIGHT", "OCEAN", "BOTANICA", "CELESTIAL", "ABSTRACT MOTION"}


def load(path: Path):
    return json.loads(path.read_text())


def test_project_registry_schema_and_collection_contract():
    project = load(ROOT / "project.json")
    schema = load(ROOT / "schemas/aether-project.schema.json")
    errors = list(Draft202012Validator(schema).iter_errors(project))
    assert not errors, [error.message for error in errors]
    assert project["repositorySchema"] == 3
    assert project["$schema"] == project["schemas"]["project"]
    assert project["defaultProduct"] in project["products"]

    collections = project["collections"]
    collection_ids = [collection["id"] for collection in collections.values()]
    assert set(collection_ids) == EXPECTED_COLLECTION_IDS
    assert len(collection_ids) == len(set(collection_ids))
    assert collections["flight"]["status"] == "active"
    assert all(collections[slug]["status"] == "planned" for slug in ("ocean", "botanica", "celestial", "abstract-motion"))


def test_registered_products_bind_to_canonical_fixture_identity():
    project = load(ROOT / "project.json")
    by_id = {collection["id"]: (slug, collection) for slug, collection in project["collections"].items()}
    counts = {collection_id: 0 for collection_id in by_id}

    for slug, product in project["products"].items():
        fixture_path = ROOT / product["fixtureManifest"]
        assert fixture_path.is_file()
        fixture = load(fixture_path)
        identity = fixture["identity"]
        assert identity["brand"] == project["brand"]
        assert identity["name"] == product["displayName"]
        assert identity["productCode"] == product["model"]
        assert identity["designRevision"] == product["designRevision"]
        assert identity["presentationRevision"] == product["currentPresentation"]
        assert identity["collection"] in by_id
        assert product["publicPath"] == f"products/{slug}/"
        counts[identity["collection"]] += 1

    assert counts["FLIGHT"] == 1
    assert all(counts[collection_id] == 0 for collection_id in EXPECTED_COLLECTION_IDS - {"FLIGHT"})

    for collection_id, (slug, collection) in by_id.items():
        if collection["status"] == "active":
            assert counts[collection_id] > 0, f"{slug} is active without a registered product"
        elif collection["status"] == "planned":
            assert counts[collection_id] == 0, f"{slug} is planned but already has a registered product"
