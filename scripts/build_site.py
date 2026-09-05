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

tools_src = ROOT / 'site' / 'tools'
if tools_src.exists():
    shutil.copytree(tools_src, OUT / 'tools', dirs_exist_ok=True)

subprocess.run([sys.executable, str(ROOT / 'scripts/build_product.py')], check=True)

collections_by_id = {collection['id']: (slug, collection) for slug, collection in P['collections'].items()}
registry = []
for slug, product in P['products'].items():
    version = product['currentPresentation']
    design_revision = product['designRevision']
    build_dir = ROOT / 'build' / slug
    viewer_candidates = sorted(build_dir.glob(f'*_Viewer_v{version}.html'))
    if len(viewer_candidates) != 1:
        raise RuntimeError(f'{slug}: expected exactly one viewer for presentation {version}, found {len(viewer_candidates)}')
    viewer = viewer_candidates[0]
    stable = OUT / 'products' / slug
    version_dir = stable / 'versions' / version
    stable.mkdir(parents=True, exist_ok=True)
    version_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(viewer, stable / 'index.html')
    shutil.copy2(viewer, version_dir / 'index.html')

    fixture_src = ROOT / product['fixtureManifest']
    fixture = json.loads(fixture_src.read_text())
    shutil.copy2(fixture_src, stable / 'fixture.json')
    collection_id = fixture['identity']['collection']
    if collection_id not in collections_by_id:
        raise RuntimeError(f'{slug}: unregistered collection {collection_id}')
    collection_slug, collection = collections_by_id[collection_id]

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
        'collectionId': collection_id,
        'collectionSlug': collection_slug,
        'collectionDisplayName': collection['displayName'],
        'collectionPath': f'collections/{collection_slug}/',
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

products_by_collection = {collection_id: [] for collection_id in collections_by_id}
for product in registry:
    products_by_collection[product['collectionId']].append(product)

collection_registry = []
for collection_slug, collection in sorted(P['collections'].items(), key=lambda item: (item[1]['sortOrder'], item[0])):
    products = sorted(products_by_collection[collection['id']], key=lambda item: item['displayName'])
    collection_meta = {
        'slug': collection_slug,
        'id': collection['id'],
        'displayName': collection['displayName'],
        'status': collection['status'],
        'sortOrder': collection['sortOrder'],
        'path': f'collections/{collection_slug}/',
        'productCount': len(products),
        'products': [item['slug'] for item in products],
    }
    collection_registry.append(collection_meta)
    collection_dir = OUT / 'collections' / collection_slug
    collection_dir.mkdir(parents=True, exist_ok=True)
    product_cards = []
    for item in products:
        inspector_link = f'<a href="../../{item["inspectorPath"]}">Technical inspector →</a>' if item['inspectorPath'] else ''
        product_cards.append(
            f'''<article class="product-card"><div class="ey">{html.escape(item['model'])}</div><h2>{html.escape(item['displayName'])}</h2><p>Design {html.escape(item['designRevision'])} · presentation {html.escape(item['presentationRevision'])}</p><div class="actions"><a href="../../{item['stablePath']}">Open viewer →</a>{inspector_link}</div></article>'''
        )
    if product_cards:
        content = '<div class="grid">' + ''.join(product_cards) + '</div>'
    else:
        content = '<div class="empty">No registered products are currently published in this collection.</div>'
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="AETHERIA {html.escape(collection['displayName'])} collection registry."><title>AETHERIA · {html.escape(collection['displayName'])}</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#0a0a0b;color:#f3efe8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{max-width:1100px;margin:auto;padding:8vh 24px}}a{{color:#d7ad75}}.brand{{font-family:Georgia,serif;letter-spacing:.24em;color:#d7ad75}}.back{{display:inline-block;margin-top:34px;text-decoration:none;font-size:13px}}h1{{font-family:Georgia,serif;font-size:clamp(48px,8vw,96px);font-weight:400;letter-spacing:-.055em;margin:70px 0 12px}}.meta{{color:#8c8985;text-transform:uppercase;letter-spacing:.12em;font-size:11px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-top:60px}}.product-card{{border:1px solid #252326;border-radius:28px;padding:28px;background:linear-gradient(145deg,#151416,#0e0e0f);min-height:230px}}.ey{{font-size:11px;letter-spacing:.15em;color:#8d7559}}h2{{font-family:Georgia,serif;font-size:42px;font-weight:400;margin:25px 0 8px}}.product-card p{{color:#777}}.actions{{display:flex;gap:18px;flex-wrap:wrap;margin-top:45px}}.actions a{{text-decoration:none;font-size:14px}}.empty{{margin-top:60px;border:1px solid #252326;border-radius:24px;padding:28px;color:#777}}</style></head><body><main><div class="brand">AETHERIA</div><a class="back" href="../../">← All collections</a><h1>{html.escape(collection['displayName'])}</h1><div class="meta">{html.escape(collection['status'])} · {len(products)} registered product{'s' if len(products) != 1 else ''}</div>{content}</main></body></html>'''
    (collection_dir / 'index.html').write_text(page)

(OUT / 'collections.json').write_text(json.dumps(collection_registry, indent=2) + '\n')

cards_parts = []
for x in registry:
    inspector_link = f'<a href="{x["inspectorPath"]}">Technical inspector →</a>' if x['inspectorPath'] else ''
    cards_parts.append(
        f'''<article class="card"><div class="ey"><a href="{x['collectionPath']}">{html.escape(x['collectionDisplayName'])}</a> · {html.escape(x['model'])}</div><h2>{html.escape(x['displayName'])}</h2><p>Design {html.escape(x['designRevision'])} · presentation {html.escape(x['presentationRevision'])}</p><div class="actions"><a href="{x['stablePath']}">Open viewer →</a>{inspector_link}</div></article>'''
    )

collection_links = ''.join(
    f'''<a class="collection-link" href="{item['path']}"><span>{html.escape(item['displayName'])}</span><small>{html.escape(item['status'])} · {item['productCount']}</small></a>'''
    for item in collection_registry
)
cards = ''.join(cards_parts)
index = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="AETHERIA controlled architectural lighting product and collection catalog."><title>AETHERIA</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#0a0a0b;color:#f3efe8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{max-width:1100px;margin:auto;padding:8vh 24px}}.brand{{font-family:Georgia,serif;letter-spacing:.24em;color:#d7ad75}}h1{{font-size:clamp(44px,8vw,94px);font-weight:400;letter-spacing:-.06em;margin:80px 0 12px}}.sub{{color:#8c8985;max-width:620px;line-height:1.6}}.tools{{margin-top:28px}}.tools a,.collection-link,.ey a{{color:#d7ad75;text-decoration:none}}.tools a:hover,.collection-link:hover,.ey a:hover{{text-decoration:underline}}.section-title{{margin:70px 0 18px;font-size:11px;text-transform:uppercase;letter-spacing:.16em;color:#777}}.collections{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}}.collection-link{{display:flex;flex-direction:column;gap:8px;border:1px solid #252326;border-radius:16px;padding:16px;background:#101011}}.collection-link span{{font-family:Georgia,serif;font-size:20px;color:#eee8df}}.collection-link small{{color:#777;text-transform:uppercase;letter-spacing:.08em;font-size:9px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}}.card{{display:block;color:inherit;border:1px solid #252326;border-radius:28px;padding:28px;background:linear-gradient(145deg,#151416,#0e0e0f);min-height:230px;transition:.25s}}.card:hover{{transform:translateY(-3px);border-color:#4a3b2c}}.ey{{font-size:11px;letter-spacing:.12em;color:#8d7559}}h2{{font-family:Georgia,serif;font-size:42px;font-weight:400;margin:25px 0 8px}}.card p{{color:#777}}.actions{{display:flex;gap:18px;flex-wrap:wrap;margin-top:45px}}.actions a{{color:#d7ad75;text-decoration:none;font-size:14px}}.actions a:hover{{text-decoration:underline}}</style></head><body><main><div class="brand">AETHERIA</div><h1>Sculptural light,<br>engineered as a product.</h1><p class="sub">A controlled platform for architectural lighting design, geometry, photometry, installation data and interactive presentation.</p><div class="tools"><a href="tools/fixture-editor/">Open fixture proposal editor →</a></div><div class="section-title">Collections</div><nav class="collections" aria-label="AETHERIA collections">{collection_links}</nav><div class="section-title">Registered products</div><div class="grid">{cards}</div></main></body></html>'''
(OUT / 'index.html').write_text(index)
print(OUT)
