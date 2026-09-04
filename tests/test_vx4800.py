from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from generate_vx4800_presentation import build, canonical_sha


def test_generated_presentation_regression():
    data = build()
    study = json.loads((ROOT / 'fixtures/vx4800/presentation/v5.2.0/study.json').read_text())
    assert len(data['elements']) == 240
    assert data['counts'] == {'S': 54, 'M': 132, 'L': 54}
    assert canonical_sha(data) == study['expectedViewerDataSha256']


def test_engineering_and_presentation_are_separate():
    import pandas as pd
    df = pd.read_csv(ROOT / 'fixtures/vx4800/composition/engineering-v1.3.0.csv')
    assert df['size'].value_counts().to_dict() == {'M': 144, 'S': 66, 'L': 30}
    assert float(df.lowest_edge_drop_mm.max()) <= 4800


def test_viewer_build():
    subprocess.run([sys.executable, str(ROOT / 'scripts/build_viewer.py')], check=True)
    p = ROOT / 'build/vx4800/VX4800_VORTEX_Viewer_v5.2.0.html'
    s = p.read_text()
    assert p.stat().st_size < 500_000
    assert s.count('"id":"VX-') >= 240
    assert all(token not in s for token in ('__VIEWER_DATA__', '__BACKGROUND_B64__', '__INLINE_CSS__', '__INLINE_JS__'))


def test_product_build_outputs_repository_artifacts_without_archives(built_product):
    viewer = built_product / 'VX4800_VORTEX_Viewer_v5.2.0.html'
    geometry = built_product / 'geometry'
    web = built_product / 'web'
    assert viewer.exists()
    assert (geometry / 'setout-coordination-v1.3.0.dxf').exists()
    assert (web / 'vx4800-coordination-v1.3.0.glb').exists()
    assert (web / 'vx4800-coordination-v1.3.0.optimized.glb').exists()
    assert (web / 'optimization-manifest.json').exists()
    assert not list(built_product.rglob('*.zip'))


def test_photometry_is_not_misrepresented():
    p = json.loads((ROOT / 'fixtures/vx4800/photometry/concept-v5.2.0.json').read_text())
    assert p['status'] == 'conceptual'
    assert p['futureMeasuredData']['iesRequired'] is True


def test_site_catalog_is_valid_json(built_site):
    products = json.loads((built_site / 'products.json').read_text())
    assert len(products) == 1 and products[0]['slug'] == 'vx4800'
    meta = json.loads((built_site / 'products/vx4800/meta.json').read_text())
    assert meta['presentationRevision'] == '5.2.0'
    assert 'downloadPath' not in meta


def test_web_coordination_geometry_is_deterministic_and_complete(built_web_geometry):
    h1 = hashlib.sha256(built_web_geometry.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(ROOT / 'scripts/generate_web_geometry.py')], check=True)
    h2 = hashlib.sha256(built_web_geometry.read_bytes()).hexdigest()
    assert h1 == h2
    import trimesh
    scene = trimesh.load(built_web_geometry, force='scene')
    nodes = set(scene.graph.nodes)
    assert sum(n.startswith('element-VX-') for n in nodes) == 240
    assert sum(n.startswith('cable-VX-') for n in nodes) == 240
    assert sum(n.startswith('led-LED-') for n in nodes) == 14


def test_pages_publish_schemas_fixture_data_and_coordination_glb(built_site):
    schemas = list((ROOT / 'schemas').glob('*.json'))
    assert schemas
    for src in schemas:
        dst = built_site / 'schemas' / src.name
        assert dst.exists()
        assert json.loads(dst.read_text())['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
    fixture = json.loads((built_site / 'products/vx4800/fixture.json').read_text())
    assert fixture['identity']['fixtureId'] == 'vx4800-bf-01'
    meta = json.loads((built_site / 'products/vx4800/meta.json').read_text())
    assert meta['fixtureDataPath'] == 'products/vx4800/fixture.json'
    glb = built_site / meta['coordinationGlbPath']
    assert glb.exists() and glb.stat().st_size > 1000


def test_viewer_source_is_split_and_javascript_parses():
    src = ROOT / 'fixtures/vx4800/presentation/v5.2.0'
    assert (src / 'viewer.template.html').stat().st_size < 20_000
    assert (src / 'viewer.styles.css').stat().st_size > 5_000
    assert (src / 'viewer.app.js').stat().st_size > 20_000
    subprocess.run(['node', '--check', str(src / 'viewer.app.js')], check=True)
