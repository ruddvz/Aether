from pathlib import Path
import json,csv,hashlib,re,subprocess,sys
import pandas as pd
from jsonschema import Draft202012Validator
from generate_vx4800_presentation import build, canonical_sha
from materialize_assets import materialize_background
ROOT=Path(__file__).resolve().parents[1]; F=ROOT/'fixtures/vx4800'; errors=[]
materialize_background()
def req(c,m):
    if not c: errors.append(m)
def load(p): return json.loads(Path(p).read_text())
for data_path,schema_path in [(F/'fixture.json',ROOT/'schemas/aether-fixture.schema.json'),(F/'presentation/v5.2.0/study.json',ROOT/'schemas/aether-presentation-study.schema.json'),(F/'photometry/concept-v5.2.0.json',ROOT/'schemas/aether-photometry.schema.json')]:
    data=load(data_path); schema=load(schema_path)
    for e in Draft202012Validator(schema).iter_errors(data): errors.append(f'{data_path.relative_to(ROOT)} schema: {e.message}')
fixture=load(F/'fixture.json'); study=load(F/'presentation/v5.2.0/study.json'); phot=load(F/'photometry/concept-v5.2.0.json')
req(fixture['identity']['designRevision']=='1.3.0','design revision mismatch')
req(fixture['identity']['presentationRevision']=='5.2.0','presentation revision mismatch')
# Asset existence/hash validation.
ids=set()
for a in fixture['assets']:
    req(a['id'] not in ids,f"duplicate asset id {a['id']}"); ids.add(a['id'])
    p=F/a['path']; req(p.exists(),f'missing asset {a["path"]}')
    if p.exists(): req(hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],f'hash mismatch {a["path"]}')

geom=load(F/'geometry/manifest.json')
req(geom['designRevision']=='1.3.0','geometry manifest revision mismatch')
req(len(geom['manufacturingAssets'])==6,'expected six external controlled manufacturing assets')
req(all(len(x['sha256'])==64 for x in geom['manufacturingAssets']),'invalid manufacturing asset hash')
req(fixture['manufacturing']['repositoryGeometryAuthority']=='coordination-only','repository geometry authority must remain coordination-only')

# Engineering schedule invariants.
df=pd.read_csv(F/'composition/engineering-v1.3.0.csv')
req(len(df)==240,'engineering schedule must have 240 rows'); req(df.element_id.nunique()==240,'engineering IDs not unique')
counts=df['size'].value_counts().to_dict(); req(counts=={'M':144,'S':66,'L':30},f'engineering family counts changed: {counts}')
req(float(df.lowest_edge_drop_mm.max())<=4800,'physical lower edge exceeds 4800mm')
req((df.finished_main_cable_mm<=df.yoke_drop_mm+1e-6).all(),'cable/yoke ordering invalid')
req(set(df.design_release.astype(str))=={'1.3.0'},'schedule design_release mismatch')
# Presentation is allowed to diverge only when explicitly declared.
req(study['authority']=='presentation-only','study authority invalid')
req(study['sizeAllocation']=={'S':54,'M':132,'L':54},'V5.2 presentation allocation changed')
req(all(x.get('requiresEngineeringReleaseBeforeManufacture') is True for x in study['declaredDivergences']),'undeclared engineering divergence risk')
# Regenerate V5.2 and compare to stored fingerprint.
gen=build(); req(len(gen['elements'])==240,'generated presentation count not 240'); req(gen['counts']==study['sizeAllocation'],'generated presentation size counts mismatch')
req(canonical_sha(gen)==study['expectedViewerDataSha256'],f'V5.2 regression fingerprint mismatch {canonical_sha(gen)}')
req(phot['status']=='conceptual','photometry must remain conceptual until controlled IES/test data exists'); req(len(phot['heads'])==14,'expected 14 conceptual heads')

# Photometry candidate schema and research contract.
candidate_schema=load(ROOT/'schemas/aether-photometry-candidate.schema.json')
for candidate_path in sorted((F/'photometry/candidates').glob('*.json')):
    candidate=load(candidate_path)
    for e in Draft202012Validator(candidate_schema).iter_errors(candidate):
        errors.append(f'{candidate_path.relative_to(ROOT)} schema: {e.message}')
    if candidate_path.name != '_template.json':
        req(candidate['fixtureId']==fixture['identity']['fixtureId'],f'{candidate_path.name}: fixtureId mismatch')
        for cfg in candidate['configurations']:
            if cfg.get('photometryStatus') in {'downloaded','parsed','verified'}:
                req(bool(cfg.get('iesPath')),f'{candidate_path.name}: {cfg["exactModelCode"]} missing iesPath')
                req(bool(cfg.get('iesSha256')),f'{candidate_path.name}: {cfg["exactModelCode"]} missing iesSha256')

selection=load(F/'photometry/selection-brief.json')
req(selection['fixtureId']==fixture['identity']['fixtureId'],'photometry selection brief fixtureId mismatch')
req(sum(x['quantity'] for x in selection['optics'])==14,'photometry selection brief must allocate 14 heads')
req(selection['lightQuality']['cctK']==3000,'initial controlled photometry CCT target must remain 3000K')

# Template/runtime contract.
t=(F/'presentation/v5.2.0/viewer.template.html').read_text(); css=(F/'presentation/v5.2.0/viewer.styles.css').read_text(); app_js=(F/'presentation/v5.2.0/viewer.app.js').read_text(); req('__VIEWER_DATA__' in t,'viewer data placeholder missing'); req('__BACKGROUND_B64__' in css,'background placeholder missing'); req('__INLINE_CSS__' in t,'inline CSS placeholder missing'); req('__INLINE_JS__' in t,'inline JS placeholder missing'); req('three@0.185.1' in t,'Three.js version is not pinned')
if errors:
    print('VALIDATION FAILED'); [print('-',e) for e in errors]; raise SystemExit(1)
print('VALIDATION PASSED'); print('vx4800: design 1.3.0 | presentation 5.2.0 | engineering 240 | presentation 240')
