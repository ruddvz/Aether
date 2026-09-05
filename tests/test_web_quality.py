from pathlib import Path
import json
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.enforce_lighthouse import enforce
from scripts.qa_site import validate_site

CONFIG = ROOT / "fixtures/platform/web-quality-v1.json"
SCHEMA = ROOT / "schemas/aether-web-quality-budget.schema.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_web_quality_budget_schema_and_pinned_toolchain():
    config = load_json(CONFIG)
    schema = load_json(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(config))
    assert not errors, [error.message for error in errors]
    assert config["authority"] == "repository-quality-gate"
    assert config["toolchain"] == {
        "nodeMajor": 24,
        "playwright": "1.62.1",
        "lighthouse": "13.4.1",
    }
    assert config["global"]["zipFilesPermitted"] is False


def test_browser_and_route_matrix_cover_required_review_surfaces():
    config = load_json(CONFIG)
    assert set(config["browserMatrix"]) == {
        "chromium-desktop",
        "firefox-desktop",
        "webkit-desktop",
        "iphone-webkit-emulation",
        "android-chromium-emulation",
    }
    routes = {route["id"]: route for route in config["routes"]}
    assert set(routes) == {"catalog", "vx4800-viewer", "vx4800-inspector"}
    assert routes["catalog"]["path"] == "/"
    assert routes["vx4800-viewer"]["path"] == "/products/vx4800/"
    assert routes["vx4800-inspector"]["path"] == "/products/vx4800/inspect/"
    for route in routes.values():
        assert route["lighthouseMinimum"]["performance"] >= 0.5
        assert route["lighthouseMinimum"]["accessibility"] >= 0.7
        assert route["lighthouseMinimum"]["best-practices"] >= 0.7
        assert route["lighthouseMinimum"]["seo"] >= 0.7


def write_minimal_site(site: Path) -> None:
    documents = {
        "index.html": "<!doctype html><html lang='en'><head><meta name='viewport' content='width=device-width'><title>Catalog</title></head><body><main>Catalog</main></body></html>",
        "products/vx4800/index.html": "<!doctype html><html lang='en'><head><meta name='viewport' content='width=device-width'><title>VORTEX</title></head><body><nav id='dock'>Viewer</nav></body></html>",
        "products/vx4800/inspect/index.html": "<!doctype html><html lang='en'><head><meta name='viewport' content='width=device-width'><title>Inspector</title></head><body><nav class='toolbar'>Inspect</nav></body></html>",
    }
    for relative, content in documents.items():
        target = site / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


def test_static_site_gate_rejects_zip_and_broken_local_reference(tmp_path):
    write_minimal_site(tmp_path)
    passing = validate_site(tmp_path, CONFIG, SCHEMA)
    assert passing["status"] == "pass", passing["errors"]

    (tmp_path / "handoff.zip").write_bytes(b"not a product artifact")
    viewer = tmp_path / "products/vx4800/index.html"
    viewer.write_text(viewer.read_text().replace("</body>", "<script src='missing.js'></script></body>"))
    failing = validate_site(tmp_path, CONFIG, SCHEMA)
    assert failing["status"] == "fail"
    text = " ".join(failing["errors"])
    assert "ZIP files are not permitted" in text
    assert "missing.js" in text


def make_lighthouse_report(version: str, score: float) -> dict:
    return {
        "lighthouseVersion": version,
        "finalDisplayedUrl": "http://127.0.0.1:4173/",
        "categories": {
            "performance": {"score": score},
            "accessibility": {"score": score},
            "best-practices": {"score": score},
            "seo": {"score": score},
        },
    }


def test_lighthouse_enforcer_requires_every_pinned_report_and_floor(tmp_path):
    config = load_json(CONFIG)
    for route in config["routes"]:
        for mode in ("mobile", "desktop"):
            path = tmp_path / f"{route['id']}-{mode}.report.json"
            path.write_text(json.dumps(make_lighthouse_report("13.4.1", 1.0)))
    passing = enforce(tmp_path, CONFIG)
    assert passing["status"] == "pass", passing["errors"]

    bad = tmp_path / "catalog-mobile.report.json"
    bad.write_text(json.dumps(make_lighthouse_report("13.4.1", 0.2)))
    failing = enforce(tmp_path, CONFIG)
    assert failing["status"] == "fail"
    assert any("below" in error for error in failing["errors"])
