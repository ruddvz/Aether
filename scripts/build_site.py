from pathlib import Path
import base64
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

tools_src = ROOT / 'site' / 'tools'
if tools_src.exists():
    shutil.copytree(tools_src, OUT / 'tools', dirs_exist_ok=True)

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

# Public brand site. This layer is intentionally separate from fixture authority:
# concept imagery and marketing copy do not modify controlled fixture data.
brand_src = ROOT / 'site' / 'brand'
if brand_src.exists():
    shutil.copytree(brand_src, OUT, dirs_exist_ok=True)

# Binary brand imagery is stored as text-safe base64 sources so the repository
# remains compatible with the existing text-oriented content workflow.
brand_assets_src = ROOT / 'site' / 'brand-assets'
if brand_assets_src.exists():
    brand_assets_out = OUT / 'assets'
    brand_assets_out.mkdir(parents=True, exist_ok=True)
    for src in sorted(brand_assets_src.glob('*.b64')):
        target_name = src.name[:-4]
        encoded = ''.join(src.read_text().split())
        (brand_assets_out / target_name).write_bytes(base64.b64decode(encoded))
    for pack in sorted(brand_assets_src.glob('*.b64pack')):
        for line_number, line in enumerate(pack.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            if '|' not in line:
                raise ValueError(f'Invalid brand asset pack line {pack}:{line_number}')
            target_name, encoded = line.split('|', 1)
            if '/' in target_name or '\\' in target_name or target_name.startswith('.'):
                raise ValueError(f'Invalid brand asset filename {target_name!r}')
            (brand_assets_out / target_name).write_bytes(base64.b64decode(encoded))

print(OUT)
