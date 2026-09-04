from pathlib import Path
import hashlib,json,zipfile,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]; F=ROOT/'fixtures/vx4800'; B=ROOT/'build/vx4800'; B.mkdir(parents=True,exist_ok=True)
subprocess.run([sys.executable,str(ROOT/'scripts/build_viewer.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/generate_geometry.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/generate_web_geometry.py')],check=True)
viewer=B/'VX4800_VORTEX_Viewer_v5.2.0.html'
files=[
 ('viewer/index.html',viewer),('product/fixture.json',F/'fixture.json'),('product/engineering-v1.3.0.csv',F/'composition/engineering-v1.3.0.csv'),('product/presentation-study-v5.2.0.json',F/'presentation/v5.2.0/study.json'),('product/photometry-concept-v5.2.0.json',F/'photometry/concept-v5.2.0.json'),
 ('engineering/geometry-manifest-v1.3.0.json',F/'geometry/manifest.json'),
 ('coordination/canopy-coordination-v1.3.0.step',B/'geometry/canopy-coordination-v1.3.0.step'),('coordination/rotating-carrier-coordination-v1.3.0.step',B/'geometry/rotating-carrier-coordination-v1.3.0.step'),('coordination/butterfly-s-coordination-v1.3.0.step',B/'geometry/butterfly-s-coordination-v1.3.0.step'),('coordination/butterfly-m-coordination-v1.3.0.step',B/'geometry/butterfly-m-coordination-v1.3.0.step'),('coordination/butterfly-l-coordination-v1.3.0.step',B/'geometry/butterfly-l-coordination-v1.3.0.step'),('coordination/setout-coordination-v1.3.0.dxf',B/'geometry/setout-coordination-v1.3.0.dxf'),('coordination/vx4800-coordination-v1.3.0.glb',B/'web/vx4800-coordination-v1.3.0.glb'),('coordination/web-geometry-manifest.json',B/'web/manifest.json')]
readme='''# AETHERIA VORTEX\n\nProduct: VX4800-BF-01\nEngineering revision: 1.3.0\nPresentation revision: 5.2.0\n\nThe engineering schedule is controlled v1.3.0 data. Manufacturing STEP/DXF hashes are preserved in geometry-manifest-v1.3.0.json; repository-generated CAD in this ZIP is coordination authority only. V5.2 presentation size allocation, poses, lighting and motion are presentation studies only.\n\nThe HTML is a single product file but requires internet access for pinned Three.js modules from jsDelivr.\n\nLighting remains conceptual until controlled supplier/test IES data exists. This package is not a construction release.\n'''
stamp=(2026,9,3,0,0,0)
out=B/'AETHERIA_VORTEX_v5.2.0.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    zi=zipfile.ZipInfo('README.md',stamp); zi.compress_type=zipfile.ZIP_DEFLATED; z.writestr(zi,readme)
    hashes=[]
    for arc,p in files:
        data=p.read_bytes(); hashes.append(f'{hashlib.sha256(data).hexdigest()}  {arc}')
        zi=zipfile.ZipInfo(arc,stamp); zi.compress_type=zipfile.ZIP_DEFLATED; z.writestr(zi,data)
    zi=zipfile.ZipInfo('SHA256SUMS.txt',stamp); zi.compress_type=zipfile.ZIP_DEFLATED; z.writestr(zi,'\n'.join(hashes)+'\n')
print(out); print(hashlib.sha256(out.read_bytes()).hexdigest())
