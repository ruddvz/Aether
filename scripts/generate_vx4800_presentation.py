from pathlib import Path
import json, math, hashlib
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'fixtures/vx4800'

def canonical_sha(data):
    return hashlib.sha256(json.dumps(data,separators=(',',':'),sort_keys=True).encode()).hexdigest()

def build():
    sched=pd.read_csv(FIX/'composition/engineering-v1.3.0.csv')
    study=json.loads((FIX/'presentation/v5.2.0/study.json').read_text())
    phot=json.loads((FIX/'photometry/concept-v5.2.0.json').read_text())
    pts=np.c_[sched.ceiling_x_mm.to_numpy(),-sched.element_origin_drop_mm.to_numpy(),sched.ceiling_y_mm.to_numpy()]
    D=np.linalg.norm(pts[:,None,:]-pts[None,:,:],axis=2); D[D==0]=np.inf
    nearest=D.min(axis=1)
    depth=((sched.element_origin_drop_mm-sched.element_origin_drop_mm.min())/(sched.element_origin_drop_mm.max()-sched.element_origin_drop_mm.min())).to_numpy()
    phase=np.arctan2(-sched.ceiling_y_mm.to_numpy(),sched.ceiling_x_mm.to_numpy())
    n=len(sched); nnorm=(nearest-nearest.min())/(nearest.max()-nearest.min())
    score=.50*(1-depth)+.38*nnorm+.12*(np.sin(phase*2.1+np.arange(n)*.27)+1)/2
    order=np.argsort(score); sizes=np.array(['M']*n,dtype=object)
    sizes[order[:54]]='S'; sizes[order[-54:]]='L'
    span={'S':108.,'M':146.,'L':186.}; length={'S':60.,'M':82.,'L':108.}
    gold=math.pi*(3-math.sqrt(5)); elements=[]; folds=[]
    for i,r in sched.iterrows():
        s=sizes[i]; sp=span[s]; d=depth[i]; ph=phase[i]; nn=nearest[i]
        base=16+28*d+5.5*math.sin(ph*1.7+i*.11)+2.5*math.sin(i*gold)
        ratio=min(1,max(0,(.84*nn)/sp)); min_fold=math.degrees(math.acos(ratio)) if ratio<1 else 0
        base += -2 if s=='L' else 2 if s=='S' else 0
        f=max(12,min(58,max(base,min_fold))); folds.append(f)
        asym=2.6*math.sin(i*gold*1.9+ph*.5)
        fl=max(9,min(62,f+asym)); fr=max(9,min(62,f-asym))
        roll=4.6*math.sin(ph*1.9+i*.15); pitch=3.4*math.sin(ph-d*2+i*.09); yawtrim=2.8*math.sin(i*gold*.8+ph*.35)
        elements.append({'id':r.element_id,'size':s,'x':float(r.ceiling_x_mm),'z':float(r.ceiling_y_mm),'cable':float(r.finished_main_cable_mm),'yoke':float(r.yoke_drop_mm),'drop':float(r.element_origin_drop_mm),'bottom':float(r.lowest_edge_drop_mm),'yaw':float((r.target_yaw_deg+yawtrim)%360),'span':sp,'length':length[s],'foldL':float(fl),'foldR':float(fr),'roll':float(roll),'pitch':float(pitch),'depthNorm':float(d),'clearance':float(nn)})
    out={'version':study['presentationRevision'],'elements':elements,'counts':{s:int((sizes==s).sum()) for s in ['S','M','L']},'poseStats':{'foldMin':round(min(folds),1),'foldMax':round(max(folds),1),'foldMedian':round(float(np.median(folds)),1),'cableMin':round(float(sched.finished_main_cable_mm.min()),1),'cableMax':round(float(sched.finished_main_cable_mm.max()),1),'largeMinClearance':round(float(nearest[sizes=='L'].min()),1)},'lighting':phot['heads'],'scene':{'imageAspect':2/3,'orthoHeight':8.2,'camera':[0,-5.1,15.0],'target':[0,-2.88,0],'defaultRotorDeg':-12.0,'defaultRPM':.36,'fixedOuterRadius':1.26,'rotorRadius':1.14,'centralHubRadius':.125,'vortexTurns':1.72}}
    return out

if __name__=='__main__':
    data=build(); out=ROOT/'build/vx4800'; out.mkdir(parents=True,exist_ok=True)
    p=out/'viewer-data-v5.2.0.json'; p.write_text(json.dumps(data,indent=2)+'\n')
    print(p); print(canonical_sha(data))
