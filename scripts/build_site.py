from pathlib import Path
import html
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
P = json.loads((ROOT / 'project.json').read_text())

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()

for src in (ROOT / 'site/static').iterdir():
    if src.is_file():
        shutil.copy2(src, OUT / src.name)

schemas_out = OUT / 'schemas'
schemas_out.mkdir(parents=True, exist_ok=True)
for src in sorted((ROOT / 'schemas').glob('*.json')):
    shutil.copy2(src, schemas_out / src.name)

subprocess.run([sys.executable, str(ROOT / 'scripts/build_product.py')], check=True)

registry = []
for slug, product in P['products'].items():
    version = product['currentPresentation']
    design_revision = product['designRevision']
    build_dir = ROOT / 'build' / slug
    viewer = build_dir / f'VX4800_VORTEX_Viewer_v{version}.html'
    stable = OUT / 'products' / slug
    version_dir = stable / 'versions' / version
    stable.mkdir(parents=True, exist_ok=True)
    version_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(viewer, stable / 'index.html')
    shutil.copy2(viewer, version_dir / 'index.html')

    fixture_src = ROOT / 'fixtures' / slug / 'fixture.json'
    shutil.copy2(fixture_src, stable / 'fixture.json')

    inspector_src = ROOT / 'site' / 'inspectors' / slug
    inspector_out = stable / 'inspect'
    if inspector_src.exists():
        shutil.copytree(inspector_src, inspector_out, dirs_exist_ok=True)

    design_dl = OUT / 'downloads' / slug / design_revision
    design_dl.mkdir(parents=True, exist_ok=True)
    glb = build_dir / 'web' / f'{slug}-coordination-v{design_revision}.glb'
    optimized_glb = build_dir / 'web' / f'{slug}-coordination-v{design_revision}.optimized.glb'
    optimization_manifest = build_dir / 'web' / 'optimization-manifest.json'
    if glb.exists():
        shutil.copy2(glb, design_dl / glb.name)
    if optimized_glb.exists():
        shutil.copy2(optimized_glb, design_dl / optimized_glb.name)
    if optimization_manifest.exists():
        shutil.copy2(optimization_manifest, design_dl / optimization_manifest.name)

    meta = {
        'slug': slug,
        'brand': P['brand'],
        'displayName': product['displayName'],
        'model': product['model'],
        'designRevision': design_revision,
        'presentationRevision': version,
        'stablePath': f'products/{slug}/',
        'versionPath': f'products/{slug}/versions/{version}/',
        'inspectorPath': f'products/{slug}/inspect/' if inspector_src.exists() else None,
        'fixtureDataPath': f'products/{slug}/fixture.json',
        'coordinationGlbPath': f'downloads/{slug}/{design_revision}/{glb.name}' if glb.exists() else None,
        'optimizedCoordinationGlbPath': f'downloads/{slug}/{design_revision}/{optimized_glb.name}' if optimized_glb.exists() else None,
        'optimizationManifestPath': f'downloads/{slug}/{design_revision}/{optimization_manifest.name}' if optimization_manifest.exists() else None,
    }
    (stable / 'meta.json').write_text(json.dumps(meta, indent=2) + '\n')
    registry.append(meta)

(OUT / 'products.json').write_text(json.dumps(registry, indent=2) + '\n')

cards_parts = []
for x in registry:
    inspector_link = f'<a href="{x["inspectorPath"]}">Technical inspector →</a>' if x['inspectorPath'] else ''
    cards_parts.append(
        f'''<article class="card"><div class="ey">{html.escape(x['model'])}</div><h2>{html.escape(x['displayName'])}</h2><p>Design {x['designRevision']} · presentation {x['presentationRevision']}</p><div class="actions"><a href="{x['stablePath']}">Open viewer →</a>{inspector_link}</div></article>'''
    )

cards = ''.join(cards_parts)
index = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AETHERIA</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#0a0a0b;color:#f3efe8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{max-width:1100px;margin:auto;padding:8vh 24px}}.brand{{font-family:Georgia,serif;letter-spacing:.24em;color:#d7ad75}}h1{{font-size:clamp(44px,8vw,94px);font-weight:400;letter-spacing:-.06em;margin:80px 0 12px}}.sub{{color:#8c8985;max-width:620px;line-height:1.6}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-top:70px}}.card{{display:block;color:inherit;border:1px solid #252326;border-radius:28px;padding:28px;background:linear-gradient(145deg,#151416,#0e0e0f);min-height:230px;transition:.25s}}.card:hover{{transform:translateY(-3px);border-color:#4a3b2c}}.ey{{font-size:11px;letter-spacing:.15em;color:#8d7559}}h2{{font-family:Georgia,serif;font-size:42px;font-weight:400;margin:25px 0 8px}}.card p{{color:#777}}.actions{{display:flex;gap:18px;flex-wrap:wrap;margin-top:45px}}.actions a{{color:#d7ad75;text-decoration:none;font-size:14px}}.actions a:hover{{text-decoration:underline}}</style></head><body><main><div class="brand">AETHERIA</div><h1>Sculptural light,<br>engineered as a product.</h1><p class="sub">A controlled platform for architectural lighting design, geometry, photometry, installation data and interactive presentation.</p><div class="grid">{cards}</div></main></body></html>'''
(OUT / 'index.html').write_text(index)
print(OUT)
