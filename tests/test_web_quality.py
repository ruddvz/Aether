from pathlib import Path
import json
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.enforce_lighthouse import enforce as enforce_lighthouse
from scripts.qa_site import validate_site
from scripts.run_lighthouse import build_audit_jobs

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
    assert set(config["global"]["allowedExternalHosts"]) == {
        "cdn.jsdelivr.net",
        "fonts.googleapis.com",
        "fonts.gstatic.com",
    }


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
    assert all(route["maxHtmlBytes"] >= 1024 for route in routes.values())


def test_lighthouse_floors_are_preserved_and_audit_matrix_has_six_runs():
    config = load_json(CONFIG)
    routes = {route["id"]: route for route in config["routes"]}
    assert routes["catalog"]["lighthouseMinimum"] == {
        "performance": 0.9,
        "accessibility": 0.9,
        "best-practices": 0.9,
        "seo": 0.9,
    }
    assert routes["vx4800-viewer"]["lighthouseMinimum"] == {
        "performance": 0.55,
        "accessibility": 0.75,
        "best-practices": 0.75,
        "seo": 0.7,
    }
    assert routes["vx4800-inspector"]["lighthouseMinimum"] == {
        "performance": 0.55,
        "accessibility": 0.8,
        "best-practices": 0.75,
        "seo": 0.7,
    }
    jobs = build_audit_jobs(config, "http://127.0.0.1:4173")
    assert len(jobs) == 6
    assert {(job["routeId"], job["mode"]) for job in jobs} == {
        ("catalog", "mobile"),
        ("catalog", "desktop"),
        ("vx4800-viewer", "mobile"),
        ("vx4800-viewer", "desktop"),
        ("vx4800-inspector", "mobile"),
        ("vx4800-inspector", "desktop"),
    }


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


def test_external_navigation_is_not_treated_as_runtime_dependency(tmp_path):
    write_minimal_site(tmp_path)
    catalog = tmp_path / "index.html"
    catalog.write_text(
        catalog.read_text().replace(
            "</body>",
            "<a href='https://github.com/ruddvz/Aether'>Source</a></body>",
        )
    )

    report = validate_site(tmp_path, CONFIG, SCHEMA)
    assert report["status"] == "pass", report["errors"]
    assert report["measurements"]["routes"]["catalog"]["externalHosts"] == []


def test_external_runtime_resource_must_be_allowlisted(tmp_path):
    write_minimal_site(tmp_path)
    catalog = tmp_path / "index.html"
    catalog.write_text(
        catalog.read_text().replace(
            "</body>",
            "<script src='https://example.invalid/runtime.js'></script></body>",
        )
    )

    report = validate_site(tmp_path, CONFIG, SCHEMA)
    assert report["status"] == "fail"
    assert report["measurements"]["routes"]["catalog"]["externalHosts"] == ["example.invalid"]
    assert any("external runtime hosts not allowlisted: example.invalid" in error for error in report["errors"])


def write_lighthouse_reports(report_dir: Path, *, score: float = 1.0, version: str = "13.4.1") -> None:
    config = load_json(CONFIG)
    for route in config["routes"]:
        for mode in ("mobile", "desktop"):
            report = {
                "lighthouseVersion": version,
                "finalDisplayedUrl": f"http://127.0.0.1:4173{route['path']}",
                "categories": {
                    "performance": {"score": score},
                    "accessibility": {"score": score},
                    "best-practices": {"score": score},
                    "seo": {"score": score},
                },
            }
            (report_dir / f"{route['id']}-{mode}.report.json").write_text(json.dumps(report))


def test_lighthouse_score_enforcer_passes_complete_reports(tmp_path):
    write_lighthouse_reports(tmp_path)
    summary = enforce_lighthouse(tmp_path, CONFIG)
    assert summary["status"] == "pass"
    assert len(summary["runs"]) == 6
    assert summary["errors"] == []


def test_lighthouse_score_enforcer_reports_score_failure_separately(tmp_path):
    write_lighthouse_reports(tmp_path)
    viewer = tmp_path / "vx4800-viewer-mobile.report.json"
    report = json.loads(viewer.read_text())
    report["categories"]["performance"]["score"] = 0.54
    viewer.write_text(json.dumps(report))

    summary = enforce_lighthouse(tmp_path, CONFIG)
    assert summary["status"] == "fail"
    assert any(
        "vx4800-viewer mobile: performance score 0.540 below 0.550" in error
        for error in summary["errors"]
    )


def test_lighthouse_score_enforcer_fails_closed_on_missing_or_wrong_version_report(tmp_path):
    write_lighthouse_reports(tmp_path)
    missing = tmp_path / "catalog-mobile.report.json"
    missing.unlink()
    wrong = tmp_path / "vx4800-inspector-desktop.report.json"
    report = json.loads(wrong.read_text())
    report["lighthouseVersion"] = "0.0.0"
    wrong.write_text(json.dumps(report))

    summary = enforce_lighthouse(tmp_path, CONFIG)
    assert summary["status"] == "fail"
    assert any("missing Lighthouse report: catalog-mobile.report.json" in error for error in summary["errors"])
    assert any("Lighthouse 0.0.0 != pinned 13.4.1" in error for error in summary["errors"])
