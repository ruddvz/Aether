from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    project_path = root / "project.json"
    collections_path = root / "site/brand/collections.json"

    if not project_path.is_file():
        return ["missing project.json"]
    if not collections_path.is_file():
        return ["missing site/brand/collections.json"]

    project = load_json(project_path)
    collections = load_json(collections_path)
    if not isinstance(collections, list) or not collections:
        return ["public collection taxonomy must be a non-empty JSON array"]

    by_name: dict[str, dict] = {}
    seen_ids: set[str] = set()
    for index, collection in enumerate(collections):
        label = f"public collection[{index}]"
        if not isinstance(collection, dict):
            errors.append(f"{label} must be an object")
            continue

        collection_id = collection.get("id")
        name = collection.get("name")
        if not isinstance(collection_id, str) or not SLUG_RE.fullmatch(collection_id):
            errors.append(f"{label} id must be a lowercase kebab-case slug")
        elif collection_id in seen_ids:
            errors.append(f"duplicate public collection id {collection_id}")
        else:
            seen_ids.add(collection_id)

        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label} name must be a non-empty string")
        elif name in by_name:
            errors.append(f"duplicate public collection name {name}")
        else:
            by_name[name] = collection

    products = project.get("products")
    if not isinstance(products, dict) or not products:
        errors.append("project.json must register at least one product")
        return errors

    for slug, product in products.items():
        if not isinstance(product, dict):
            errors.append(f"{slug}: project product record must be an object")
            continue
        fixture_ref = product.get("fixtureManifest")
        if not isinstance(fixture_ref, str) or not fixture_ref.strip():
            errors.append(f"{slug}: fixtureManifest must be a non-empty repository path")
            continue

        fixture_path = root / fixture_ref
        if not fixture_path.is_file():
            errors.append(f"{slug}: missing fixture manifest {fixture_ref}")
            continue

        fixture = load_json(fixture_path)
        identity = fixture.get("identity")
        if not isinstance(identity, dict):
            errors.append(f"{slug}: fixture identity must be an object")
            continue

        collection_name = identity.get("collection")
        if not isinstance(collection_name, str) or not collection_name.strip():
            errors.append(f"{slug}: fixture identity.collection must be a non-empty string")
        elif collection_name not in by_name:
            errors.append(
                f"{slug}: controlled fixture collection {collection_name!r} has no matching public collection name"
            )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("COLLECTION TAXONOMY VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    project = load_json(ROOT / "project.json")
    collections = load_json(ROOT / "site/brand/collections.json")
    print(
        "COLLECTION TAXONOMY VALIDATION PASSED "
        f"| public collections {len(collections)} | registered products {len(project['products'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
