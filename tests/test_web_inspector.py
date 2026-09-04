from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_inspector_source_pins_bvh_and_parses():
    src = ROOT / "site/inspectors/vx4800"
    html = (src / "index.html").read_text()
    js = src / "inspector.app.js"
    text = js.read_text()
    assert "three@0.185.1" in html
    assert "three-mesh-bvh@0.9.14" in html
    assert "computeBoundsTree" in text
    assert "closestPointToGeometry" in text
    assert "MeshoptDecoder" in text
    assert "localStorage" in text
    subprocess.run(["node", "--check", str(js)], check=True)


def test_nearest_clearance_uses_lower_bound_not_candidate_cap():
    text = (ROOT / "site/inspectors/vx4800/inspector.app.js").read_text()
    assert ".slice(0, 18)" not in text
    assert "candidate.lowerBound >= best.distance" in text
    assert "sourceSphere.center.distanceTo(s.center) - sourceSphere.radius - s.radius" in text


def test_pages_publish_inspector_and_optimized_coordination_asset(built_site):
    meta = json.loads((built_site / "products/vx4800/meta.json").read_text())
    assert meta["inspectorPath"] == "products/vx4800/inspect/"
    assert meta["optimizedCoordinationGlbPath"]
    assert meta["optimizationManifestPath"]

    inspector = built_site / meta["inspectorPath"] / "index.html"
    inspector_js = built_site / meta["inspectorPath"] / "inspector.app.js"
    optimized = built_site / meta["optimizedCoordinationGlbPath"]
    source = built_site / meta["coordinationGlbPath"]
    manifest_path = built_site / meta["optimizationManifestPath"]

    assert inspector.exists()
    assert inspector_js.exists()
    assert optimized.exists() and optimized.stat().st_size > 1000
    assert source.exists() and source.stat().st_size > 1000
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text())
    assert manifest["authority"] == "coordination-only-derived-web-asset"
    assert manifest["optimizer"]["package"] == "@gltf-transform/cli@4.5.0"
    assert manifest["optimized"]["extensionsExpected"] == ["EXT_meshopt_compression"]
    assert manifest["constraints"]["mayReplaceControlledCoordinationGlb"] is False
    assert manifest["constraints"]["mayBecomeManufacturingAuthority"] is False
    assert manifest["constraints"]["rawFileSizeReductionRequired"] is False
    assert optimized.stat().st_size - source.stat().st_size == manifest["optimized"]["rawByteDelta"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest["source"]["sha256"]
    assert hashlib.sha256(optimized.read_bytes()).hexdigest() == manifest["optimized"]["sha256"]


def test_inspector_keeps_authority_boundary_visible():
    src = ROOT / "site/inspectors/vx4800"
    html = (src / "index.html").read_text()
    js = (src / "inspector.app.js").read_text()
    assert "does not replace controlled engineering" in html
    assert "coordination geometry" in js.lower()
    assert "manufacturing" in html.lower()
