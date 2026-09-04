from pathlib import Path
from collections import Counter
import subprocess,sys
import cadquery as cq
import ezdxf

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/vx4800/geometry'
errors=[]
def req(c,m):
    if not c: errors.append(m)
def bounds(path):
    obj=cq.importers.importStep(str(path)); bb=obj.val().BoundingBox(); return (bb.xlen,bb.ylen,bb.zlen)
subprocess.run([sys.executable,str(ROOT/'scripts/generate_geometry.py')],check=True)
for name,expected in [('canopy-coordination-v1.3.0.step',(2400,1500,150)),('rotating-carrier-coordination-v1.3.0.step',(2260,1330,24))]:
    try:
        b=bounds(OUT/name); req(all(abs(b[i]-expected[i])<1.0 for i in range(3)),f'{name}: bounds {b} != {expected}')
    except Exception as e: errors.append(f'{name}: STEP failed {e}')
for key,expected in [('s',(108,60)),('m',(146,82)),('l',(186,108))]:
    try:
        b=bounds(OUT/f'butterfly-{key}-coordination-v1.3.0.step'); req(max(b[:2])>=expected[0]*.80,f'butterfly {key}: suspicious bounds {b}')
    except Exception as e: errors.append(f'butterfly {key}: STEP failed {e}')
try:
    doc=ezdxf.readfile(OUT/'setout-coordination-v1.3.0.dxf'); m=doc.modelspace(); layers=Counter(e.dxf.layer for e in m)
    req(layers['CABLE_EXITS']==240,f"DXF cable exits {layers['CABLE_EXITS']} != 240")
    req(layers['FIXED_LEDS']==14,f"DXF fixed LEDs {layers['FIXED_LEDS']} != 14")
    req(layers['FIXED_CANOPY']==1,'DXF fixed canopy missing')
    req(layers['ROTATING_CARRIER']==1,'DXF rotating carrier missing')
except Exception as e: errors.append(f'DXF failed {e}')
if errors:
    print('GEOMETRY QA FAILED'); [print('-',x) for x in errors]; raise SystemExit(1)
print('GEOMETRY QA PASSED - repository-generated geometry is coordination authority only')
