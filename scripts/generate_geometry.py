from pathlib import Path
import json, math, re
import pandas as pd
import cadquery as cq
import ezdxf

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'fixtures/vx4800'
OUT=ROOT/'build/vx4800/geometry'

def export_step_deterministic(obj,path):
    cq.exporters.export(obj,str(path))
    txt=Path(path).read_text(errors='strict')
    txt=re.sub(r"(FILE_NAME\('Open CASCADE Shape Model',)'[^']+'",r"\1'2026-09-03T00:00:00'",txt,count=1)
    Path(path).write_text(txt)

def rounded_box(width, depth, height, radius):
    solid=cq.Workplane("XY").rect(width,depth).extrude(height)
    return solid.edges("|Z").fillet(radius)

def make_butterfly(span, length, thickness):
    # Lightweight coordination silhouette only. Manufacturing butterfly geometry remains external controlled STEP.
    body_w=max(4, span*.035)
    body=cq.Workplane('XY').ellipse(body_w/2, length*.28).extrude(thickness)
    wing_len=length*.86
    # Four elliptical wing lobes, original coordination abstraction.
    shapes=[body]
    for side in (-1,1):
        fore=(cq.Workplane('XY').center(side*span*.24,length*.11).ellipse(span*.25, wing_len*.28).extrude(thickness).rotate((0,0,0),(0,0,1),-side*28))
        hind=(cq.Workplane('XY').center(side*span*.20,-length*.16).ellipse(span*.20, wing_len*.22).extrude(thickness).rotate((0,0,0),(0,0,1),side*20))
        shapes += [fore,hind]
    out=shapes[0]
    for x in shapes[1:]: out=out.union(x)
    return out

def build():
    P=json.loads((FIX/'geometry/parameters-v1.3.0.json').read_text())
    OUT.mkdir(parents=True,exist_ok=True)
    c=P['canopy']; carrier=P['rotatingCarrier']
    canopy=rounded_box(c['widthMm'],c['depthMm'],c['heightMm'],c['cornerRadiusMm'])
    export_step_deterministic(canopy,OUT/'canopy-coordination-v1.3.0.step')
    rotor=rounded_box(carrier['widthMm'],carrier['depthMm'],carrier['thicknessMm'],carrier['cornerRadiusMm'])
    export_step_deterministic(rotor,OUT/'rotating-carrier-coordination-v1.3.0.step')
    for key,d in P['butterflies'].items():
        export_step_deterministic(make_butterfly(d['spanMm'],d['lengthMm'],d['thicknessMm']),OUT/f'butterfly-{key.lower()}-coordination-v1.3.0.step')
    # Set-out regenerated directly from controlled schedules.
    sched=pd.read_csv(FIX/'composition/engineering-v1.3.0.csv')
    leds=pd.read_csv(FIX/'photometry/led-setout-engineering-v1.3.0.csv')
    doc=ezdxf.new('R12'); doc.units=4 # millimetres; old DXF keeps the deterministic setout simple
    for name,color in [('FIXED_CANOPY',7),('ROTATING_CARRIER',3),('CABLE_EXITS',8),('FIXED_LEDS',2),('TEXT',7)]:
        doc.layers.add(name,color=color)
    m=doc.modelspace()
    # Review geometry uses rounded-rectangle polylines only; schedule locations remain exact.
    def rr_points(w,d,r,n=16):
        pts=[]
        centers=[(w/2-r,d/2-r),(-w/2+r,d/2-r),(-w/2+r,-d/2+r),(w/2-r,-d/2+r)]
        starts=[0,90,180,270]
        for (cx,cy),start in zip(centers,starts):
            for j in range(n+1):
                a=math.radians(start+j*90/n); pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
        return pts
    m.add_polyline2d(rr_points(c['widthMm'],c['depthMm'],c['cornerRadiusMm']),close=True,dxfattribs={'layer':'FIXED_CANOPY'})
    m.add_polyline2d(rr_points(carrier['widthMm'],carrier['depthMm'],carrier['cornerRadiusMm']),close=True,dxfattribs={'layer':'ROTATING_CARRIER'})
    for _,r in sched.iterrows(): m.add_circle((float(r.ceiling_x_mm),float(r.ceiling_y_mm)),2.0,dxfattribs={'layer':'CABLE_EXITS'})
    # LED source columns are x_mm/y_mm in controlled schedule.
    for _,r in leds.iterrows(): m.add_circle((float(r.x_mm),float(r.y_mm)),8.0,dxfattribs={'layer':'FIXED_LEDS'})
    m.add_text('AETHERIA VX4800 COORDINATION SETOUT - NOT MANUFACTURING AUTHORITY',dxfattribs={'height':24,'layer':'TEXT'}).set_placement((-1150,-850))
    dxf_path=OUT/'setout-coordination-v1.3.0.dxf'; doc.saveas(dxf_path)
    txt=dxf_path.read_text()
    txt=re.sub(r'(\$TDCREATE\s+40\s+)\S+',r'\g<1>2461287.5',txt)
    txt=re.sub(r'(\$TDUPDATE\s+40\s+)\S+',r'\g<1>2461287.5',txt)
    txt=re.sub(r'(\$TDUCREATE\s+40\s+)\S+',r'\g<1>0.0',txt)
    txt=re.sub(r'(\$TDUUPDATE\s+40\s+)\S+',r'\g<1>0.0',txt)
    txt=re.sub(r'1\.4\.4 @ [^\r\n]+', '1.4.4 @ 2026-09-03T00:00:00+00:00', txt)
    dxf_path.write_text(txt)
    return OUT

if __name__=='__main__': print(build())
