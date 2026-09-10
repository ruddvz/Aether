from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COLLECTIONS = {
    "flight": "FLIGHT",
    "ocean": "OCEAN",
    "botanica": "BOTANICA",
    "celestial": "CELESTIAL",
    "abstract-motion": "ABSTRACT MOTION",
}


def load(path: Path):
    return json.loads(path.read_text())


def test_project_registry_schema_and_collection_contract():
    project = load(ROOT / "project.json")
    schema = load(ROOT / "schemas/aether-project.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(project), key=lambda error: list(error.path))
    assert not errors, [error.message for error in errors]
    assert project["repositorySchema"] == 3
    assert project["$schema"] == "schemas/aether-project.schema.json"
    assert project["defaultProduct"] in project["products"]

    collections = project["collections"]
    assert {slug: value["id"] for slug, value in collections.items()} == EXPECTED_COLLECTIONS
    assert collections["flight"]["status"] == "active"
    assert all(
        collections[slug]["status"] == "planned"
        for slug in ("ocean", "botanica", "celestial", "abstract-motion")
    )
    sort_orders = [collection["sortOrder"] for collection in collections.values()]
    assert len(sort_orders) == len(set(sort_orders))


def test_registered_products_bind_to_canonical_fixture_identity():
    project = load(ROOT / "project.json")
    collection_ids = {collection["id"] for collection in project["collections"].values()}
    counts = {collection_id: 0 for collection_id in collection_ids}

    for slug, product in project["products"].items():
        for path_field in ("fixtureManifest", "viewerTemplate", "presentationStudy", "photometry"):
            assert (ROOT / product[path_field]).is_file(), f"{slug}: missing {path_field}"

        fixture = load(ROOT / product["fixtureManifest"])
        identity = fixture["identity"]
        assert identity["brand"] == project["brand"]
        assert identity["name"] == product["displayName"]
        assert identity["productCode"] == product["model"]
        assert identity["designRevision"] == product["designRevision"]
        assert identity["presentationRevision"] == product["currentPresentation"]
        assert identity["collection"] in collection_ids
        assert product["publicPath"] == f"products/{slug}/"
        counts[identity["collection"]] += 1

    assert counts["FLIGHT"] == 1
    assert all(counts[collection_id] == 0 for collection_id in collection_ids - {"FLIGHT"})

    for collection in project["collections"].values():
        if collection["status"] == "active":
            assert counts[collection["id"]] > 0
        elif collection["status"] == "planned":
            assert counts[collection["id"]] == 0


def test_public_collection_catalog_matches_controlled_registry_identity():
    project = load(ROOT / "project.json")
    public_collections = load(ROOT / "site/brand/collections.json")
    public_by_slug = {collection["id"]: collection for collection in public_collections}

    assert set(public_by_slug) == set(project["collections"])
    for slug, controlled in project["collections"].items():
        assert public_by_slug[slug]["name"] == controlled["displayName"]
