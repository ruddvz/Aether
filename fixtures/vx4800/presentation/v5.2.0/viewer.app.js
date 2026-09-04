import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const app=$("#app"),frame=$("#frame"),stage=$("#stage"),dock=$("#dock");
const brandLockup=$(".brandLockup"),motionPanel=$("#motionPanel"),lightPanel=$("#lightPanel"),drawer=$("#drawer"),inspect=$("#inspect"),contextHint=$("#contextHint");
const imageAspect=DATA.scene.imageAspect;
const mobile=matchMedia("(max-width:720px)").matches;
const lowPower=mobile || (navigator.hardwareConcurrency && navigator.hardwareConcurrency<=4);

let scene,renderer,sceneCam,studioCam,currentCamera,controls;
let root,fixedGroup,rotorGroup,mechanismGroup,cableMesh,yokeLines,exitPoints,contactShadow;
let studioBackdrop,studioFloor,detailGroup,detailButterfly,detailShadow;
let wingMeshes=[],centralSpot,centralBeam,centralBeamCore,fieldLights=[];
let crystalMat,edgeMat,sparkleMat,cableMat,lightingScene="gallery";
let viewName="scene",motion=true,direction=1,rpm=DATA.scene.defaultRPM,rotorAngle=THREE.MathUtils.degToRad(DATA.scene.defaultRotorDeg);
let manualDrag=false,lastX=0,manualVelocity=0,mechanismRequested=false,hidden=false,dirty=true,last=performance.now(),idleTimer=null;

try{
scene=new THREE.Scene();
sceneCam=new THREE.OrthographicCamera(-1,1,1,-1,.03,100);
studioCam=new THREE.PerspectiveCamera(31,1,.03,100);
currentCamera=sceneCam;

renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:"high-performance"});
renderer.setClearColor(0x000000,0);
renderer.setPixelRatio(Math.min(devicePixelRatio||1,lowPower?.95:1.16));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.33;
stage.appendChild(renderer.domElement);

const pmrem=new THREE.PMREMGenerator(renderer);
const env=new THREE.Scene();
env.add(new THREE.HemisphereLight(0xffead5,0x25384d,1.8));
const e1=new THREE.PointLight(0xffd0a0,20,12,2);e1.position.set(3,3,4);env.add(e1);
const e2=new THREE.PointLight(0xa9d1ff,7,12,2);e2.position.set(-4,0,-3);env.add(e2);
scene.environment=pmrem.fromScene(env,.06).texture;pmrem.dispose();

controls=new OrbitControls(studioCam,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=.055;controls.enablePan=false;controls.zoomToCursor=true;
controls.minDistance=2.6;controls.maxDistance=14;controls.enabled=false;

root=new THREE.Group();fixedGroup=new THREE.Group();rotorGroup=new THREE.Group();mechanismGroup=new THREE.Group();
root.add(fixedGroup,rotorGroup);fixedGroup.add(mechanismGroup);scene.add(root);

// Dedicated warm-white product-review environment.
// Vortex uses a soft ivory cyclorama instead of a flat white plane.
function makeStudioGradient(){
  const c=document.createElement("canvas");c.width=1024;c.height=1024;
  const x=c.getContext("2d");
  const g=x.createRadialGradient(512,340,70,512,450,700);
  g.addColorStop(0,"#ffffff");
  g.addColorStop(.36,"#f8f7f3");
  g.addColorStop(.72,"#efede7");
  g.addColorStop(1,"#e5e1d9");
  x.fillStyle=g;x.fillRect(0,0,1024,1024);
  const v=x.createLinearGradient(0,0,0,1024);
  v.addColorStop(0,"rgba(255,255,255,.22)");
  v.addColorStop(.66,"rgba(255,255,255,0)");
  v.addColorStop(1,"rgba(120,105,88,.055)");
  x.fillStyle=v;x.fillRect(0,0,1024,1024);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;
}
const studioGradientTex=makeStudioGradient();
studioBackdrop=new THREE.Mesh(
  new THREE.PlaneGeometry(24,24),
  new THREE.MeshBasicMaterial({map:studioGradientTex})
);
studioBackdrop.position.set(0,-2.0,-5.0);
scene.add(studioBackdrop);

studioFloor=new THREE.Mesh(
  new THREE.PlaneGeometry(24,24),
  new THREE.MeshStandardMaterial({color:0xf1efe9,roughness:.93,metalness:0})
);
studioFloor.rotation.x=-Math.PI/2;
studioFloor.position.y=-5.25;
scene.add(studioFloor);

detailGroup=new THREE.Group();
detailGroup.visible=false;
scene.add(detailGroup);

function makeSoftShadowTexture(){
  const c=document.createElement("canvas");c.width=c.height=512;
  const x=c.getContext("2d");
  const g=x.createRadialGradient(256,256,12,256,256,246);
  g.addColorStop(0,"rgba(0,0,0,.24)");
  g.addColorStop(.25,"rgba(0,0,0,.12)");
  g.addColorStop(.62,"rgba(0,0,0,.045)");
  g.addColorStop(1,"rgba(0,0,0,0)");
  x.fillStyle=g;x.fillRect(0,0,512,512);
  return new THREE.CanvasTexture(c);
}
const studioShadowTex=makeSoftShadowTexture();

detailShadow=new THREE.Mesh(
  new THREE.PlaneGeometry(1.65,.82),
  new THREE.MeshBasicMaterial({map:studioShadowTex,transparent:true,opacity:.78,depthWrite:false})
);
detailShadow.rotation.x=-Math.PI/2;
detailShadow.position.set(0,-.23,.11);
detailGroup.add(detailShadow);

studioBackdrop.visible=false;
studioFloor.visible=false;
const fixtureFloorShadow=new THREE.Mesh(
  new THREE.PlaneGeometry(4.0,2.4),
  new THREE.MeshBasicMaterial({map:studioShadowTex,transparent:true,opacity:.30,depthWrite:false})
);
fixtureFloorShadow.rotation.x=-Math.PI/2;
fixtureFloorShadow.position.set(0,-5.22,.10);
fixtureFloorShadow.visible=false;
scene.add(fixtureFloorShadow);

// Soft horizon band gives the full-fixture view a photographic cyclorama feel.
const horizonBand=new THREE.Mesh(
  new THREE.PlaneGeometry(15,2.7),
  new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.18,depthWrite:false})
);
horizonBand.position.set(0,-4.25,-4.85);
horizonBand.visible=false;
scene.add(horizonBand);

// ---------------- Butterfly object ----------------
const palette=[
 new THREE.Color(0xecf7f9),new THREE.Color(0xd3e7ef),new THREE.Color(0xf6ebdc),
 new THREE.Color(0xdde1f1),new THREE.Color(0xd0e9e4),new THREE.Color(0xefdcc7),
 new THREE.Color(0xe5f0f8),new THREE.Color(0xcbdbea)
];

function wingShape(kind,span,length){
 const s=new THREE.Shape();
 if(kind==="fore"){
   s.moveTo(.013*span,.024*length);
   s.bezierCurveTo(.09*span,.19*length,.30*span,.44*length,.49*span,.37*length);
   s.bezierCurveTo(.54*span,.33*length,.50*span,.18*length,.425*span,.082*length);
   s.bezierCurveTo(.31*span,-.018*length,.115*span,-.035*length,.013*span,.005*length);
 }else{
   s.moveTo(.013*span,-.014*length);
   s.bezierCurveTo(.12*span,-.015*length,.31*span,-.075*length,.41*span,-.215*length);
   s.bezierCurveTo(.46*span,-.31*length,.37*span,-.43*length,.235*span,-.445*length);
   s.bezierCurveTo(.115*span,-.44*length,.043*span,-.27*length,.013*span,-.07*length);
 }
 s.closePath();return s;
}
function makeWing(kind,side,spanMM,lengthMM,seed){
 const sp=spanMM/1000,ln=lengthMM/1000;
 const g=new THREE.ExtrudeGeometry(wingShape(kind,sp,ln),{
   depth:.0025,bevelEnabled:true,bevelThickness:.00055,bevelSize:.00065,bevelSegments:1,
   curveSegments:22,steps:1
 });
 g.rotateX(-Math.PI/2);g.translate(0,-.00125,0);if(side<0)g.scale(-1,1,1);
 const ng=g.index?g.toNonIndexed():g,p=ng.getAttribute("position"),cols=new Float32Array(p.count*3);
 for(let t=0;t<p.count/3;t++){
   const c=palette[(t+seed)%palette.length].clone();
   const mod=1+(((t*31+seed*13)%7)-3)*.012;c.multiplyScalar(mod);
   for(let k=0;k<3;k++){const j=(t*3+k)*3;cols[j]=c.r;cols[j+1]=c.g;cols[j+2]=c.b}
 }
 ng.setAttribute("color",new THREE.BufferAttribute(cols,3));ng.computeVertexNormals();return ng;
}

const sizeDims={S:[108,60],M:[146,82],L:[186,108]},wingGeoms={};
for(const s of ["S","M","L"]){
 const [sp,ln]=sizeDims[s];
 wingGeoms[s]={LF:makeWing("fore",1,sp,ln,1),RF:makeWing("fore",-1,sp,ln,3),LH:makeWing("hind",1,sp,ln,5),RH:makeWing("hind",-1,sp,ln,7)};
}

// High-detail isolated L butterfly used only in Detail mode.
// It reuses the same V5 wing language but renders as a dedicated object,
// so the viewer can inspect the ornament without the chandelier behind it.
function buildDetailButterfly(){
  const g=new THREE.Group();
  const sp=.186,ln=.108;
  const foldL=22,foldR=18;

  const detailCrystal=lowPower
    ? new THREE.MeshStandardMaterial({
        color:0xf4f8f9,roughness:.10,metalness:.03,transparent:true,opacity:.95,side:THREE.DoubleSide,
        vertexColors:true
      })
    : new THREE.MeshPhysicalMaterial({
        color:0xffffff,roughness:.026,metalness:.008,clearcoat:1,clearcoatRoughness:.012,
        transmission:.22,thickness:.010,ior:1.50,
        iridescence:.34,iridescenceIOR:1.30,iridescenceThicknessRange:[105,420],
        specularIntensity:1,specularColor:new THREE.Color(0xfff6e8),
        transparent:true,opacity:.94,side:THREE.DoubleSide,vertexColors:true
      });

  const detailEdge=new THREE.MeshPhysicalMaterial({
    color:0xcfa36a,metalness:.54,roughness:.16,clearcoat:.65,clearcoatRoughness:.05,
    transparent:true,opacity:.30,side:THREE.BackSide,depthWrite:false
  });
  const dBrass=new THREE.MeshPhysicalMaterial({
    color:0xb7864d,metalness:.96,roughness:.13,clearcoat:.58,clearcoatRoughness:.055
  });
  const dBrassLight=new THREE.MeshPhysicalMaterial({
    color:0xd7b579,metalness:.90,roughness:.18,clearcoat:.45,clearcoatRoughness:.07
  });

  const rootMounts=[];
  const keys=[["LF",1,foldL],["RF",-1,foldR],["LH",1,foldL-2],["RH",-1,foldR-2]];
  keys.forEach(([key,side,fold],index)=>{
    const wing=new THREE.Mesh(wingGeoms.L[key],detailCrystal);
    wing.rotation.z=THREE.MathUtils.degToRad(side*fold);
    const rim=new THREE.Mesh(wingGeoms.L[key],detailEdge);
    rim.rotation.copy(wing.rotation);rim.scale.set(1.014,1.016,1.014);

    // Root jewel / mechanical mounting tab visible only in close-up.
    const mount=new THREE.Mesh(
      new THREE.CylinderGeometry(.0046,.0046,.004,14),
      index<2?dBrassLight:dBrass
    );
    mount.rotation.x=Math.PI/2;
    mount.position.set(side*.009,.003,index<2?ln*.045:-ln*.045);
    mount.rotation.z=wing.rotation.z;

    g.add(rim,wing,mount);
    rootMounts.push(mount);
  });

  // Segmented abdomen, tapered from thorax to tail.
  const abdomenGroup=new THREE.Group();
  const segCount=7;
  for(let i=0;i<segCount;i++){
    const t=i/(segCount-1);
    const radius=THREE.MathUtils.lerp(sp*.027,sp*.011,t);
    const length=ln*.078;
    const segment=new THREE.Mesh(
      new THREE.CylinderGeometry(radius*.86,radius,length,16,1),
      i%2===0?dBrass:dBrassLight
    );
    segment.rotation.x=Math.PI/2;
    segment.position.z=ln*.055-i*length*.77;
    abdomenGroup.add(segment);
  }
  g.add(abdomenGroup);

  // Thorax has an inner dark core and a polished outer shell.
  const thorax=new THREE.Mesh(new THREE.SphereGeometry(sp*.039,28,18),dBrass);
  thorax.scale.set(1,.88,1.10);thorax.position.set(0,.002,ln*.105);g.add(thorax);
  const thoraxCore=new THREE.Mesh(
    new THREE.SphereGeometry(sp*.025,20,14),
    new THREE.MeshPhysicalMaterial({color:0x3a2a1b,metalness:.82,roughness:.20,clearcoat:.30})
  );
  thoraxCore.position.set(0,.002,ln*.104);g.add(thoraxCore);

  const head=new THREE.Mesh(new THREE.SphereGeometry(sp*.026,28,18),dBrassLight);
  head.scale.set(1,.92,1.0);head.position.set(0,.005,ln*.218);g.add(head);

  // Tiny dark eye details help the ornament read as a butterfly without becoming biological.
  const eyeMat=new THREE.MeshPhysicalMaterial({color:0x201915,metalness:.55,roughness:.22,clearcoat:.55});
  for(const side of [-1,1]){
    const eye=new THREE.Mesh(new THREE.SphereGeometry(.0022,12,8),eyeMat);
    eye.position.set(side*.0042,.008,ln*.237);g.add(eye);
  }

  // Curved antennae use TubeGeometry rather than straight cylinders.
  const antennaMat=new THREE.MeshPhysicalMaterial({color:0xb98750,metalness:.94,roughness:.18});
  for(const side of [-1,1]){
    const curve=new THREE.CatmullRomCurve3([
      new THREE.Vector3(side*.0035,.010,ln*.238),
      new THREE.Vector3(side*.010,.022,ln*.285),
      new THREE.Vector3(side*.022,.030,ln*.335),
      new THREE.Vector3(side*.035,.026,ln*.375)
    ]);
    const tube=new THREE.Mesh(new THREE.TubeGeometry(curve,30,.00075,8,false),antennaMat);
    g.add(tube);
    const tip=new THREE.Mesh(new THREE.SphereGeometry(.00145,10,7),antennaMat);
    tip.position.copy(curve.getPoint(1));g.add(tip);
  }

  // Suspension hardware: cap, eyelet and tiny pin above the thorax.
  const cap=new THREE.Mesh(new THREE.CylinderGeometry(.006,.007,.006,18),dBrassLight);
  cap.position.set(0,.021,ln*.105);g.add(cap);
  const eyelet=new THREE.Mesh(new THREE.TorusGeometry(.005,.0009,8,24),dBrassLight);
  eyelet.rotation.x=Math.PI/2;eyelet.position.set(0,.026,ln*.105);g.add(eyelet);
  const pin=new THREE.Mesh(new THREE.CylinderGeometry(.0012,.0012,.010,10),dBrassLight);
  pin.position.set(0,.031,ln*.105);g.add(pin);

  // Close-up vein and facet network.
  const veinVerts=[];
  const facetVerts=[];
  const seg=(arr,a,b)=>arr.push(a.x,a.y,a.z,b.x,b.y,b.z);

  for(const side of [-1,1]){
    const f=side>0?foldL:foldR;
    const q=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,0,1),THREE.MathUtils.degToRad(side*f));
    const p=(x,z,y=.0034)=>new THREE.Vector3(side*x,y,z).applyQuaternion(q);

    // Primary veins.
    seg(veinVerts,p(.004,ln*.035),p(.054,ln*.305));
    seg(veinVerts,p(.006,ln*.012),p(.083,ln*.170));
    seg(veinVerts,p(.004,-ln*.040),p(.060,-ln*.255));
    seg(veinVerts,p(.025,ln*.178),p(.075,ln*.300));
    seg(veinVerts,p(.026,-ln*.115),p(.062,-ln*.278));

    // Secondary veins/facet boundaries.
    seg(facetVerts,p(.024,ln*.165,.0042),p(.054,ln*.225,.0042));
    seg(facetVerts,p(.054,ln*.225,.0042),p(.082,ln*.170,.0042));
    seg(facetVerts,p(.030,ln*.070,.0042),p(.074,ln*.120,.0042));
    seg(facetVerts,p(.027,-ln*.105,.0042),p(.058,-ln*.170,.0042));
    seg(facetVerts,p(.058,-ln*.170,.0042),p(.075,-ln*.235,.0042));
  }

  const veinG=new THREE.BufferGeometry();
  veinG.setAttribute("position",new THREE.Float32BufferAttribute(veinVerts,3));
  g.add(new THREE.LineSegments(veinG,new THREE.LineBasicMaterial({
    color:0xb88d59,transparent:true,opacity:.44,depthWrite:false
  })));

  const facetG=new THREE.BufferGeometry();
  facetG.setAttribute("position",new THREE.Float32BufferAttribute(facetVerts,3));
  g.add(new THREE.LineSegments(facetG,new THREE.LineBasicMaterial({
    color:0xc8dce4,transparent:true,opacity:.48,depthWrite:false
  })));

  // Four small crystal accent facets near the wing roots.
  const facetMat=new THREE.MeshPhysicalMaterial({
    color:0xe9f6fb,roughness:.02,metalness:.02,clearcoat:1,clearcoatRoughness:.01,
    transmission:.24,thickness:.008,ior:1.52,transparent:true,opacity:.86
  });
  for(const side of [-1,1]){
    for(const z of [ln*.10,-ln*.08]){
      const gem=new THREE.Mesh(new THREE.OctahedronGeometry(.0085,0),facetMat);
      gem.scale.set(1.5,.38,1.0);gem.position.set(side*.025,.008,z);g.add(gem);
    }
  }

  g.scale.set(4.45,4.45,4.45);
  g.rotation.x=THREE.MathUtils.degToRad(-7);
  g.rotation.y=THREE.MathUtils.degToRad(-9);
  g.position.set(0,.075,0);
  return g;
}


crystalMat=lowPower
 ? new THREE.MeshStandardMaterial({
    color:0xf2f7f8,vertexColors:true,roughness:.16,metalness:.06,emissive:0x1b130a,emissiveIntensity:.10,
    side:THREE.DoubleSide,transparent:true,opacity:.91,depthWrite:true
   })
 : new THREE.MeshPhysicalMaterial({
    color:0xffffff,vertexColors:true,roughness:.050,metalness:.016,clearcoat:1,clearcoatRoughness:.022,
    iridescence:.48,iridescenceIOR:1.30,iridescenceThicknessRange:[100,520],
    specularIntensity:1,specularColor:new THREE.Color(0xfff5e7),
    emissive:0x1b1309,emissiveIntensity:.11,side:THREE.DoubleSide,transparent:true,opacity:.90,depthWrite:true
   });

edgeMat=new THREE.MeshBasicMaterial({color:0xe0b279,transparent:true,opacity:.105,side:THREE.BackSide,depthWrite:false});
const brassMat=new THREE.MeshPhysicalMaterial({color:0xb78952,metalness:.94,roughness:.16,clearcoat:.46,clearcoatRoughness:.08});
const brassLight=new THREE.MeshPhysicalMaterial({color:0xd8b77f,metalness:.88,roughness:.20,clearcoat:.36});
detailButterfly=buildDetailButterfly();
detailGroup.add(detailButterfly);


const dummy=new THREE.Object3D(),euler=new THREE.Euler(),qBase=new THREE.Quaternion(),qFold=new THREE.Quaternion(),qFinal=new THREE.Quaternion();
const zAxis=new THREE.Vector3(0,0,1);

function baseQ(r){
 euler.set(THREE.MathUtils.degToRad(r.pitch),THREE.MathUtils.degToRad(r.yaw),THREE.MathUtils.degToRad(r.roll),"YXZ");
 return qBase.setFromEuler(euler);
}
function tint(r){
 const d=r.depthNorm,a=Math.atan2(-r.z,r.x),ph=d*Math.PI*2*DATA.scene.vortexTurns-.74;
 const delta=Math.atan2(Math.sin(a-ph),Math.cos(a-ph)),b=Math.pow((Math.cos(delta)+1)/2,3);
 const c=new THREE.Color();c.setHSL(THREE.MathUtils.lerp(.56,.09,b),THREE.MathUtils.lerp(.05,.16,b),THREE.MathUtils.lerp(.92,1,b));return c
}

for(const s of ["S","M","L"]){
 const rows=DATA.elements.filter(r=>r.size===s);
 for(const key of ["LF","RF","LH","RH"]){
   const mesh=new THREE.InstancedMesh(wingGeoms[s][key],crystalMat,rows.length);
   const rim=new THREE.InstancedMesh(wingGeoms[s][key],edgeMat,rows.length);
   mesh.userData.rows=rows;mesh.frustumCulled=false;rim.frustumCulled=false;

   rows.forEach((r,i)=>{
     const side=key[0]==="L"?1:-1,fore=key[1]==="F";
     const fold=(side>0?r.foldL:r.foldR)+(fore?0:-2.8);
     const base=baseQ(r).clone();
     qFold.setFromAxisAngle(zAxis,THREE.MathUtils.degToRad(side*fold));
     qFinal.copy(base).multiply(qFold);

     dummy.position.set(r.x/1000,-r.drop/1000,-r.z/1000);
     dummy.quaternion.copy(qFinal);dummy.scale.set(1,1,1);dummy.updateMatrix();
     mesh.setMatrixAt(i,dummy.matrix);mesh.setColorAt(i,tint(r));

     dummy.scale.set(1.009,1.010,1.009);dummy.updateMatrix();rim.setMatrixAt(i,dummy.matrix);
   });
   mesh.instanceMatrix.needsUpdate=true;rim.instanceMatrix.needsUpdate=true;
   if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true;
   rotorGroup.add(rim,mesh);wingMeshes.push(mesh);
 }
}

// Body anatomy
for(const s of ["S","M","L"]){
 const rows=DATA.elements.filter(r=>r.size===s),[spMM,lnMM]=sizeDims[s],sp=spMM/1000,ln=lnMM/1000;
 const abdG=new THREE.CylinderGeometry(sp*.024,sp*.014,ln*.45,10,1);abdG.rotateX(Math.PI/2);
 const thorG=new THREE.SphereGeometry(sp*.034,12,8),headG=new THREE.SphereGeometry(sp*.023,12,8),capG=new THREE.SphereGeometry(sp*.017,10,8);
 const abd=new THREE.InstancedMesh(abdG,brassMat,rows.length),thor=new THREE.InstancedMesh(thorG,brassMat,rows.length),head=new THREE.InstancedMesh(headG,brassLight,rows.length),cap=new THREE.InstancedMesh(capG,brassLight,rows.length);

 rows.forEach((r,i)=>{
   const q=baseQ(r).clone(),origin=new THREE.Vector3(r.x/1000,-r.drop/1000,-r.z/1000);
   const place=v=>{
     dummy.position.copy(v.clone().applyQuaternion(q).add(origin));dummy.quaternion.copy(q);dummy.scale.set(1,1,1);dummy.updateMatrix();return dummy.matrix
   };
   abd.setMatrixAt(i,place(new THREE.Vector3(0,0,-ln*.03)));
   thor.setMatrixAt(i,place(new THREE.Vector3(0,.001,ln*.10)));
   head.setMatrixAt(i,place(new THREE.Vector3(0,.002,ln*.19)));
   cap.setMatrixAt(i,place(new THREE.Vector3(0,.015,ln*.10)));
 });
 [abd,thor,head,cap].forEach(m=>{m.instanceMatrix.needsUpdate=true;rotorGroup.add(m)});
}

// Fine anatomy / veins, one draw call
const detailVerts=[];
const seg=(a,b)=>detailVerts.push(a.x,a.y,a.z,b.x,b.y,b.z);
DATA.elements.forEach(r=>{
 const sp=r.span/1000,ln=r.length/1000,q=baseQ(r).clone(),origin=new THREE.Vector3(r.x/1000,-r.drop/1000,-r.z/1000);
 const tr=v=>v.clone().applyQuaternion(q).add(origin);
 seg(tr(new THREE.Vector3(-sp*.010,.004,ln*.205)),tr(new THREE.Vector3(-sp*.103,.015,ln*.34)));
 seg(tr(new THREE.Vector3( sp*.010,.004,ln*.205)),tr(new THREE.Vector3( sp*.103,.015,ln*.34)));
 for(const side of [-1,1]){
   const fold=THREE.MathUtils.degToRad((side>0?r.foldL:r.foldR)*side);
   const qf=new THREE.Quaternion().setFromAxisAngle(zAxis,fold);
   const wp=(x,z)=>new THREE.Vector3(side*x,0,z).applyQuaternion(qf).applyQuaternion(q).add(origin);
   seg(wp(sp*.014,ln*.032),wp(sp*.30,ln*.29));
   seg(wp(sp*.018,ln*.005),wp(sp*.44,ln*.16));
   seg(wp(sp*.014,-ln*.050),wp(sp*.31,-ln*.25));
 }
});
const detailG=new THREE.BufferGeometry();detailG.setAttribute("position",new THREE.Float32BufferAttribute(detailVerts,3));
rotorGroup.add(new THREE.LineSegments(detailG,new THREE.LineBasicMaterial({color:0xd4ad78,transparent:true,opacity:.21,depthWrite:false})));

// ---------------- Stable suspension ----------------
// Cylindrical geometry avoids one-pixel line shimmer/twitching during rotation.
const cableG=new THREE.CylinderGeometry(.00052,.00052,1,6,1);
cableMat=new THREE.MeshBasicMaterial({
 color:0xc4ccd1,transparent:true,opacity:lowPower?.045:.058,depthWrite:false,alphaToCoverage:true
});
cableMesh=new THREE.InstancedMesh(cableG,cableMat,DATA.elements.length);
DATA.elements.forEach((r,i)=>{
 const L=r.cable/1000;
 dummy.position.set(r.x/1000,-L/2,-r.z/1000);
 dummy.rotation.set(0,0,0);dummy.scale.set(1,L,1);dummy.updateMatrix();cableMesh.setMatrixAt(i,dummy.matrix);
});
cableMesh.instanceMatrix.needsUpdate=true;rotorGroup.add(cableMesh);

const yokeVerts=[];
const addY=(a,b)=>yokeVerts.push(a.x,a.y,a.z,b.x,b.y,b.z);
DATA.elements.forEach(r=>{
 const y=-r.yoke/1000,a=THREE.MathUtils.degToRad(r.yaw),ca=Math.cos(a),sa=Math.sin(a);
 const cx=r.x/1000,cz=-r.z/1000,dx=.015*ca,dz=-.015*sa;
 const pL=new THREE.Vector3(cx-dx,y,cz-dz),pR=new THREE.Vector3(cx+dx,y,cz+dz);
 addY(pL,pR);
 const q=baseQ(r).clone(),origin=new THREE.Vector3(cx,-r.drop/1000,cz);
 const aL=new THREE.Vector3(-.006,.014,.008).applyQuaternion(q).add(origin);
 const aR=new THREE.Vector3( .006,.014,.008).applyQuaternion(q).add(origin);
 addY(pL,aL);addY(pR,aR);
});
const yokeG=new THREE.BufferGeometry();yokeG.setAttribute("position",new THREE.Float32BufferAttribute(yokeVerts,3));
yokeLines=new THREE.LineSegments(yokeG,new THREE.LineBasicMaterial({color:0xba9e78,transparent:true,opacity:lowPower?.14:.18,depthWrite:false}));
rotorGroup.add(yokeLines);

// ---------------- Ceiling assembly ----------------
function radialTexture(kind){
 const c=document.createElement("canvas");c.width=c.height=256;const x=c.getContext("2d"),g=x.createRadialGradient(128,128,8,128,128,126);
 if(kind==="shadow"){g.addColorStop(0,"rgba(0,0,0,.42)");g.addColorStop(.52,"rgba(0,0,0,.19)");g.addColorStop(1,"rgba(0,0,0,0)")}
 else{g.addColorStop(0,"rgba(255,255,255,1)");g.addColorStop(.10,"rgba(255,231,195,.96)");g.addColorStop(.40,"rgba(255,187,108,.21)");g.addColorStop(1,"rgba(255,150,70,0)")}
 x.fillStyle=g;x.fillRect(0,0,256,256);return new THREE.CanvasTexture(c)
}
const shadowTex=radialTexture("shadow"),glowTex=radialTexture("glow");
contactShadow=new THREE.Mesh(new THREE.CircleGeometry(DATA.scene.fixedOuterRadius*1.08,128),
 new THREE.MeshBasicMaterial({map:shadowTex,transparent:true,opacity:.82,depthWrite:false,side:THREE.DoubleSide}));
contactShadow.rotation.x=Math.PI/2;contactShadow.position.y=.112;fixedGroup.add(contactShadow);

const fixedMetal=new THREE.MeshPhysicalMaterial({color:0x3c2d20,metalness:.91,roughness:.17,clearcoat:.32,clearcoatRoughness:.09});
const bezel=new THREE.Mesh(new THREE.CylinderGeometry(DATA.scene.fixedOuterRadius*1.01,DATA.scene.fixedOuterRadius*1.01,.024,180),fixedMetal);
bezel.position.y=.108;fixedGroup.add(bezel);
const collar=new THREE.Mesh(new THREE.CylinderGeometry(DATA.scene.fixedOuterRadius,DATA.scene.fixedOuterRadius,.082,180),fixedMetal);
collar.position.y=.053;fixedGroup.add(collar);
const annulus=new THREE.Mesh(new THREE.RingGeometry(DATA.scene.rotorRadius+.024,DATA.scene.fixedOuterRadius-.035,180),
 new THREE.MeshStandardMaterial({color:0x080706,metalness:.60,roughness:.24,side:THREE.DoubleSide}));
annulus.rotation.x=Math.PI/2;annulus.position.y=-.011;fixedGroup.add(annulus);

const rotorMetal=new THREE.MeshPhysicalMaterial({color:0x241c16,metalness:.92,roughness:.17,clearcoat:.40,clearcoatRoughness:.08});
const rotorDisc=new THREE.Mesh(new THREE.CylinderGeometry(DATA.scene.rotorRadius,DATA.scene.rotorRadius,.024,180),rotorMetal);
rotorDisc.position.y=-.039;rotorGroup.add(rotorDisc);
const rotorEdge=new THREE.Mesh(new THREE.TorusGeometry(DATA.scene.rotorRadius,.006,10,180),
 new THREE.MeshBasicMaterial({color:0xc69761,transparent:true,opacity:.38}));
rotorEdge.rotation.x=Math.PI/2;rotorEdge.position.y=-.054;rotorGroup.add(rotorEdge);

const hub=new THREE.Mesh(new THREE.CylinderGeometry(DATA.scene.centralHubRadius,DATA.scene.centralHubRadius,.038,96),
 new THREE.MeshPhysicalMaterial({color:0x654a31,metalness:.94,roughness:.14,clearcoat:.40}));
hub.position.y=-.061;fixedGroup.add(hub);
const lens=new THREE.Mesh(new THREE.CircleGeometry(.055,64),new THREE.MeshBasicMaterial({color:0xffdfad}));
lens.rotation.x=Math.PI/2;lens.position.y=-.082;fixedGroup.add(lens);
const haloSprite=new THREE.Sprite(new THREE.SpriteMaterial({map:glowTex,color:0xffd09a,transparent:true,opacity:.38,depthWrite:false,blending:THREE.AdditiveBlending}));
haloSprite.position.set(0,-.09,0);haloSprite.scale.set(.22,.22,.22);fixedGroup.add(haloSprite);

const exitG=new THREE.BufferGeometry();
exitG.setAttribute("position",new THREE.Float32BufferAttribute(DATA.elements.flatMap(r=>[r.x/1000,-.055,-r.z/1000]),3));
exitPoints=new THREE.Points(exitG,new THREE.PointsMaterial({color:0xc59a65,size:.007,transparent:true,opacity:.52,sizeAttenuation:true}));
exitPoints.visible=false;rotorGroup.add(exitPoints);

// ---------------- Lighting ----------------
const headMat=new THREE.MeshPhysicalMaterial({color:0x121110,metalness:.88,roughness:.20,clearcoat:.20});
const faceMat=new THREE.MeshBasicMaterial({color:0xffdeb0});
fieldLights=[];

DATA.lighting.forEach((h,i)=>{
 const body=new THREE.Mesh(new THREE.CylinderGeometry(.026,.026,.030,18),headMat);
 body.position.set(h.x,-.045,h.z);fixedGroup.add(body);
 const face=new THREE.Mesh(new THREE.CircleGeometry(.018,18),faceMat);
 face.rotation.x=Math.PI/2;face.position.set(h.x,-.063,h.z);fixedGroup.add(face);

 // Mobile keeps all 14 physical heads but calculates 7 real spotlights.
 if(!lowPower || i%2===0){
   const light=new THREE.SpotLight(0xffd2a1,h.gallery,6.5,THREE.MathUtils.degToRad(h.beam/2),.82,1.65);
   light.position.set(h.x,-.075,h.z);light.target.position.set(h.targetX,h.targetY,h.targetZ);
   fixedGroup.add(light,light.target);fieldLights.push({light,meta:h});
 }
});

centralSpot=new THREE.SpotLight(0xffd7a8,650,6.3,THREE.MathUtils.degToRad(4),.90,1.6);
centralSpot.position.set(0,-.085,0);centralSpot.target.position.set(0,-3.5,0);fixedGroup.add(centralSpot,centralSpot.target);

centralBeam=new THREE.Mesh(new THREE.ConeGeometry(.17,4.7,30,1,true),
 new THREE.MeshBasicMaterial({color:0xffd9ab,transparent:true,opacity:.010,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide}));
centralBeam.position.y=-2.43;fixedGroup.add(centralBeam);
centralBeamCore=new THREE.Mesh(new THREE.CylinderGeometry(.022,.060,4.55,18,1,true),
 new THREE.MeshBasicMaterial({color:0xffe6c2,transparent:true,opacity:.006,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide}));
centralBeamCore.position.y=-2.36;fixedGroup.add(centralBeamCore);

const sparkRows=DATA.elements.filter((r,i)=>r.size==="L"||i%12===0).slice(0,lowPower?24:38);
const sg=new THREE.BufferGeometry();
sg.setAttribute("position",new THREE.Float32BufferAttribute(sparkRows.flatMap(r=>[r.x/1000,-r.drop/1000,-r.z/1000]),3));
sparkleMat=new THREE.PointsMaterial({map:glowTex,size:lowPower?.048:.058,transparent:true,opacity:.30,depthWrite:false,blending:THREE.AdditiveBlending,sizeAttenuation:true,color:0xffdfb7});
rotorGroup.add(new THREE.Points(sg,sparkleMat));

const mechMat=new THREE.MeshStandardMaterial({color:0x65696f,metalness:.90,roughness:.27});
const bearing=new THREE.Mesh(new THREE.TorusGeometry(.30,.040,14,72),mechMat);bearing.rotation.x=Math.PI/2;bearing.position.y=-.009;mechanismGroup.add(bearing);
const axis=new THREE.Mesh(new THREE.CylinderGeometry(.052,.052,.12,24),mechMat);axis.position.y=-.020;mechanismGroup.add(axis);
mechanismGroup.visible=false;

scene.add(new THREE.HemisphereLight(0xdce6ef,0x130b07,.90));
const key=new THREE.DirectionalLight(0xffe1ba,1.6);key.position.set(3.5,3.1,5);scene.add(key);
const cool=new THREE.DirectionalLight(0xa9c7e9,.66);cool.position.set(-4,-.8,-4);scene.add(cool);

const studioKey=new THREE.DirectionalLight(0xffffff,2.8);studioKey.position.set(3.8,5.0,5.5);scene.add(studioKey);
const studioFill=new THREE.DirectionalLight(0xdfe8f2,1.3);studioFill.position.set(-4.5,1.8,3.0);scene.add(studioFill);
const studioWarm=new THREE.DirectionalLight(0xffdfbd,1.0);studioWarm.position.set(1.5,-1.0,-2.5);scene.add(studioWarm);
[studioKey,studioFill,studioWarm].forEach(l=>l.visible=false);


// ---------------- Scene / responsive UI ----------------
function setFrame(studio=false){
 const vw=innerWidth,vh=innerHeight;let w,h,left,top;
 if(studio){w=vw;h=vh;left=0;top=0;app.classList.add("studio")}
 else{
   app.classList.remove("studio");
   if(vw/vh>imageAspect){h=vh;w=h*imageAspect;left=(vw-w)/2;top=0}
   else{w=vw;h=w/imageAspect;left=0;top=(vh-h)/2}
 }
 frame.style.left=left+"px";frame.style.top=top+"px";frame.style.width=w+"px";frame.style.height=h+"px";
 renderer.setSize(w,h,false);

 const safe=mobile?10:18;
 brandLockup.style.left=(left+w/2)+"px";brandLockup.style.top=(top+(mobile?15:20))+"px";
 dock.style.left=(left+w/2)+"px";dock.style.top=(top+h-(mobile?61:58))+"px";
 contextHint.style.left=(left+w/2)+"px";contextHint.style.top=(top+h-(mobile?94:92))+"px";
 const panelLeft=Math.max(8,left+w/2-122);
 motionPanel.style.left=panelLeft+"px";motionPanel.style.top=(top+h-(mobile?245:238))+"px";
 lightPanel.style.left=panelLeft+"px";lightPanel.style.top=(top+h-(mobile?230:224))+"px";
 drawer.style.left=Math.max(9,left+w-Math.min(398,w-18)-safe)+"px";
 drawer.style.top=(top+(mobile?66:70))+"px";drawer.style.height=Math.min(h-(mobile?150:142),650)+"px";
 inspect.style.left=(left+safe)+"px";inspect.style.top=(top+h-(mobile?126:116))+"px";
 return {w,h,left,top};
}
function configureSceneCam(w,h){
 const H=DATA.scene.orthoHeight,W=H*(w/h);
 sceneCam.left=-W/2;sceneCam.right=W/2;sceneCam.top=H/2;sceneCam.bottom=-H/2;
 sceneCam.position.set(...DATA.scene.camera);sceneCam.up.set(0,1,0);
 sceneCam.lookAt(new THREE.Vector3(...DATA.scene.target));sceneCam.updateProjectionMatrix();
}
const studioViews={
  vortex:{p:[3.75,-.60,9.25],t:[0,-2.34,0],f:27},
  detail:{p:[0.0,.30,2.42],t:[0,.055,0],f:23}
};
function sceneView(){
 viewName="scene";const r=setFrame(false);configureSceneCam(r.w,r.h);currentCamera=sceneCam;
 controls.enabled=false;controls.enableRotate=true;controls.enableZoom=true;
 renderer.setClearColor(0x000000,0);
 $("#motionBtn").style.display="grid";
 root.visible=true;detailGroup.visible=false;studioBackdrop.visible=false;studioFloor.visible=false;fixtureFloorShadow.visible=false;horizonBand.visible=false;
 [studioKey,studioFill,studioWarm].forEach(l=>l.visible=false);
 root.position.set(0,0,0);contactShadow.visible=true;mechanismGroup.visible=mechanismRequested;exitPoints.visible=mechanismRequested;
 cableMat.opacity=lowPower?.045:.058;yokeLines.material.opacity=lowPower?.14:.18;
 app.classList.remove("whiteStudio");
 contextHint.textContent="Drag to rotate the chandelier";
 $("#motionBtn").disabled=false;
 $$(".view").forEach(b=>b.classList.toggle("active",b.dataset.view==="scene"));dirty=true;
}
function studioView(name){
 viewName=name;const r=setFrame(true);currentCamera=studioCam;studioCam.aspect=r.w/r.h;
 const v=studioViews[name];studioCam.position.set(...v.p);studioCam.fov=v.f;studioCam.updateProjectionMatrix();
 controls.target.set(...v.t);
 controls.enabled=true;controls.enableRotate=(name==="vortex");controls.enableZoom=true;controls.enablePan=false;
 controls.update();
 renderer.setClearColor(0xf6f6f4,1);
 app.classList.add("whiteStudio");
 studioBackdrop.visible=true;studioFloor.visible=(name==="vortex");fixtureFloorShadow.visible=(name==="vortex");horizonBand.visible=(name==="vortex");
 [studioKey,studioFill,studioWarm].forEach(l=>l.visible=true);

 $("#motionBtn").disabled=(name==="detail");
 $("#lightBtn").disabled=false;
 if(name==="vortex"){
   root.visible=true;detailGroup.visible=false;
   root.position.set(0,.20,0);contactShadow.visible=false;
   mechanismGroup.visible=false;exitPoints.visible=false;
   cableMat.opacity=lowPower?.052:.067;yokeLines.material.opacity=lowPower?.11:.15;
   studioBackdrop.position.set(0,-2.15,-5.0);
   horizonBand.position.set(0,-4.22,-4.88);
   contextHint.textContent="Drag to orbit · pinch or scroll to zoom";
 }else{
   root.visible=false;detailGroup.visible=true;
   detailButterfly.rotation.x=THREE.MathUtils.degToRad(-7);
   detailButterfly.rotation.y=THREE.MathUtils.degToRad(-9);
   studioBackdrop.position.set(0,0,-3.8);studioFloor.visible=false;horizonBand.visible=false;
   contextHint.textContent="Drag the butterfly · pinch or scroll to zoom";
 }
 $$(".view").forEach(b=>b.classList.toggle("active",b.dataset.view===name));dirty=true;
}
sceneView();

// ---------------- Lighting scenes ----------------
function setLightingScene(name){
 lightingScene=name;
 app.classList.remove("scene-ambient","scene-gallery","scene-flight");app.classList.add("scene-"+name);
 $$("[data-light]").forEach(b=>b.classList.toggle("active",b.dataset.light===name));
 $("#lightBtn").classList.toggle("active",name!=="ambient");

 const info={
  ambient:"Low-contrast warm room mode. The chandelier remains calm and reflective.",
  gallery:"Balanced 3000K-like sculpture lighting. The butterflies move visually because highlights travel across the field, not because the strings move.",
  flight:"Higher-contrast presentation. A slow highlight wave travels from the upper field into the vortex tail."
 }[name];
 $("#lightInfo").textContent=info;

 const cfg={
  ambient:{exposure:1.26,emissive:.06,edge:.07,spark:.14,beam:.003,core:.002,central:160},
  gallery:{exposure:1.33,emissive:.11,edge:.105,spark:.30,beam:.010,core:.006,central:650},
  flight:{exposure:1.45,emissive:.20,edge:.16,spark:.50,beam:.022,core:.014,central:1250}
 }[name];

 renderer.toneMappingExposure=cfg.exposure;crystalMat.emissiveIntensity=cfg.emissive;
 edgeMat.opacity=cfg.edge;sparkleMat.opacity=cfg.spark;
 centralBeam.material.opacity=cfg.beam;centralBeamCore.material.opacity=cfg.core;centralSpot.intensity=cfg.central;
 fieldLights.forEach(({light,meta})=>light.intensity=meta[name]);
 dirty=true;
}
setLightingScene("gallery");

// ---------------- UI ----------------
function updateMotion(){
 $("#rpmRead").textContent=rpm.toFixed(2)+" rpm";$("#turnRead").textContent=Math.round(60/rpm)+" s / turn";
}
updateMotion();

$("#motionBtn").onclick=()=>{
 if($("#motionBtn").disabled)return;
 drawer.classList.remove("open");lightPanel.classList.remove("open");motionPanel.classList.toggle("open");
};
$("#lightBtn").onclick=()=>{
 drawer.classList.remove("open");motionPanel.classList.remove("open");lightPanel.classList.toggle("open");
};
$("#pauseBtn").onclick=()=>{motion=!motion;$("#pauseBtn").textContent=motion?"Pause":"Play";$("#motionBtn").classList.toggle("active",motion);dirty=true};
$("#cwBtn").onclick=()=>{direction=1;$("#cwBtn").classList.add("active");$("#ccwBtn").classList.remove("active")};
$("#ccwBtn").onclick=()=>{direction=-1;$("#ccwBtn").classList.add("active");$("#cwBtn").classList.remove("active")};
$("#speed").oninput=e=>{rpm=Number(e.target.value);updateMotion()};
$$("[data-light]").forEach(b=>b.onclick=()=>setLightingScene(b.dataset.light));

$("#infoBtn").onclick=()=>{
 motionPanel.classList.remove("open");lightPanel.classList.remove("open");drawer.classList.toggle("open");
};
$("#close").onclick=()=>drawer.classList.remove("open");
$("#fullBtn").onclick=async()=>{try{document.fullscreenElement?await document.exitFullscreen():await document.documentElement.requestFullscreen()}catch(e){}};

$$(".view").forEach(b=>b.onclick=()=>{
 const n=b.dataset.view;
 if(n==="scene")sceneView();
 else if(n==="vortex"||n==="detail")studioView(n);

});
$("#cableToggle").onclick=()=>{
 const visible=!cableMesh.visible;cableMesh.visible=visible;yokeLines.visible=visible;
 $("#cableToggle").classList.toggle("on",visible);dirty=true;
};
$("#mechanism").onclick=()=>{
 mechanismRequested=!mechanismRequested;mechanismGroup.visible=mechanismRequested;exitPoints.visible=mechanismRequested;
 $("#mechanism").classList.toggle("on",mechanismRequested);dirty=true;
};

// Detail mode drag rotates the isolated butterfly for close inspection.
let detailDrag=false,detailLastX=0,detailLastY=0;
renderer.domElement.addEventListener("pointerdown",e=>{
 if(viewName!=="detail")return;
 detailDrag=true;detailLastX=e.clientX;detailLastY=e.clientY;
 renderer.domElement.setPointerCapture?.(e.pointerId);wakeHUD();
});
renderer.domElement.addEventListener("pointermove",e=>{
 if(!detailDrag||viewName!=="detail")return;
 const dx=e.clientX-detailLastX,dy=e.clientY-detailLastY;detailLastX=e.clientX;detailLastY=e.clientY;
 detailButterfly.rotation.y+=dx*.007;
 detailButterfly.rotation.x=THREE.MathUtils.clamp(detailButterfly.rotation.x+dy*.004,-.45,.35);
 dirty=true;
});
addEventListener("pointerup",()=>detailDrag=false);

// Architectural scene drag rotates the complete field as one rigid object.
renderer.domElement.addEventListener("pointerdown",e=>{
 if(viewName!=="scene")return;manualDrag=true;lastX=e.clientX;manualVelocity=0;
 renderer.domElement.setPointerCapture?.(e.pointerId);wakeHUD();
});
renderer.domElement.addEventListener("pointermove",e=>{
 if(!manualDrag||viewName!=="scene")return;
 const dx=e.clientX-lastX;lastX=e.clientX;rotorAngle+=dx*.0058;manualVelocity=dx*.00062;dirty=true;
});
addEventListener("pointerup",()=>manualDrag=false);

// Inspector
const ray=new THREE.Raycaster(),mouse=new THREE.Vector2();let pd=null;
renderer.domElement.addEventListener("pointerdown",e=>pd=[e.clientX,e.clientY]);
renderer.domElement.addEventListener("pointerup",e=>{
 if(!pd||Math.hypot(e.clientX-pd[0],e.clientY-pd[1])>5||viewName==="scene")return;
 const r=renderer.domElement.getBoundingClientRect();
 mouse.x=((e.clientX-r.left)/r.width)*2-1;mouse.y=-((e.clientY-r.top)/r.height)*2+1;
 ray.setFromCamera(mouse,currentCamera);
 const h=ray.intersectObjects(wingMeshes,false)[0];if(!h)return;
 const row=h.object.userData.rows[h.instanceId];
 $("#iid").textContent=row.id;
 $("#imeta").textContent=`${row.size} · ${row.span.toFixed(0)} mm · cable ${row.cable.toFixed(0)} mm · wings ${row.foldL.toFixed(0)}° / ${row.foldR.toFixed(0)}°`;
 inspect.classList.add("show");clearTimeout(window.__inspect);window.__inspect=setTimeout(()=>inspect.classList.remove("show"),3800);
});

controls.addEventListener("change",()=>dirty=true);
document.addEventListener("visibilitychange",()=>hidden=document.hidden);
function resize(){
 renderer.setPixelRatio(Math.min(devicePixelRatio||1,(matchMedia("(max-width:720px)").matches||lowPower)?.95:1.16));
 if(viewName==="scene")sceneView();else studioView(viewName);dirty=true;
}
addEventListener("resize",resize,{passive:true});

function wakeHUD(){
 app.classList.remove("idle");clearTimeout(idleTimer);
 idleTimer=setTimeout(()=>{
   if(!drawer.classList.contains("open")&&!motionPanel.classList.contains("open")&&!lightPanel.classList.contains("open"))app.classList.add("idle");
 },5200);
}
addEventListener("pointermove",wakeHUD,{passive:true});addEventListener("pointerdown",wakeHUD,{passive:true});wakeHUD();

// ---------------- Render loop ----------------
function loop(now){
 const dt=Math.min((now-last)/1000,.05);last=now;
 if(hidden){requestAnimationFrame(loop);return}
 let moving=false;

 if(motion&&!manualDrag&&viewName!=="detail"){rotorAngle+=direction*(rpm*2*Math.PI/60)*dt;moving=true}
 if(!manualDrag&&Math.abs(manualVelocity)>.00001){
   rotorAngle+=manualVelocity*60*dt;manualVelocity*=Math.pow(.84,60*dt);moving=true;
 }

 // Strict physical-visual invariant:
 // cables, yokes and butterflies are children of ONE rotor group.
 // No independent string motion exists anywhere in V5.
 fixedGroup.rotation.set(0,0,0);
 rotorGroup.rotation.set(0,rotorAngle,0);

 // "Flight" is a slow illumination wave, not geometry animation.
 if(lightingScene==="flight"){
   const t=now*.00022;
   fieldLights.forEach(({light,meta},i)=>{
     const wave=.80+.22*Math.sin(t*Math.PI*2 - meta.targetDepth*Math.PI*2.3 + i*.08);
     light.intensity=meta.flight*wave;
   });
   sparkleMat.opacity=.46+.055*Math.sin(now*.00135);
   moving=true;
 }

 if(viewName==="vortex"||viewName==="detail")controls.update();
 if(viewName==="detail"&&!detailDrag){
   detailButterfly.rotation.y+=dt*.055;
   moving=true;
 }
 if(moving||dirty){renderer.render(scene,currentCamera);dirty=false}
 requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
$("#loader").classList.add("hide");

}catch(err){
 console.error(err);$("#loader").classList.add("hide");
}
