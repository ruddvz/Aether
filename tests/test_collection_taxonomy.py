import json
from pathlib import Path

from scripts.validate_collection_taxonomy import validate


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def make_minimal_repo(root: Path, fixture_collection: str = "FLIGHT") -> None:
    write_json(
        root / "project.json",
        {
            "products": {
                "vx4800": {
                    "fixtureManifest": "fixtures/vx4800/fixture.json",
                }
            }
        },
    )
    write_json(
        root / "fixtures/vx4800/fixture.json",
        {"identity": {"collection": fixture_collection}},
    )
    write_json(
        root / "site/brand/collections.json",
        [
            {"id": "flight", "name": "FLIGHT"},
            {"id": "ocean", "name": "OCEAN"},
        ],
    )


def test_current_repository_collection_taxonomy_is_consistent():
    assert validate() == []


def test_collection_taxonomy_rejects_fixture_collection_drift(tmp_path):
    make_minimal_repo(tmp_path, fixture_collection="UNKNOWN")
    errors = validate(tmp_path)
    assert errors == [
        "vx4800: controlled fixture collection 'UNKNOWN' has no matching public collection name"
    ]


def test_collection_taxonomy_rejects_duplicate_public_identity(tmp_path):
    make_minimal_repo(tmp_path)
    write_json(
        tmp_path / "site/brand/collections.json",
        [
            {"id": "flight", "name": "FLIGHT"},
            {"id": "flight", "name": "FLIGHT"},
        ],
    )
    errors = validate(tmp_path)
    assert "duplicate public collection id flight" in errors
    assert "duplicate public collection name FLIGHT" in errors
