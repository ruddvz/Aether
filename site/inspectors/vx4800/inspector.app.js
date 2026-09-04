import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { acceleratedRaycast, computeBoundsTree, disposeBoundsTree } from 'three-mesh-bvh';

THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;

const MODEL_URL = '../../../downloads/vx4800/1.3.0/vx4800-coordination-v1.3.0.optimized.glb';
const STORAGE_KEY = 'aetheria-vx4800-review-annotations-v1';
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const viewport = $('#viewport');
const status = $('.status');
const loadStatus = $('#loadStatus');
const loading = $('#loading');
const hint = $('#hint');
const toast = $('#toast');

let modelRoot = null;
let mode = 'inspect';
let pointerDown = null;
let selectedMesh = null;
let selectedReviewName = '';
let measureStart = null;
let measurementSeq = 0;
let annotationSeq = 0;
const pickableMeshes = [];
const elementMeshes = [];
const uniqueGeometries = new Set();
const measurements = [];
const annotations = [];

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0b0c);
scene.fog = new THREE.FogExp2(0x0b0b0c, 0.035);

const camera = new THREE.PerspectiveCamera(36, innerWidth / innerHeight, 0.01, 100);
camera.position.set(4.2, -1.8, 8.2);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.5));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
viewport.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.enablePan = true;
controls.zoomToCursor = true;
controls.minDistance = 0.8;
controls.maxDistance = 20;
controls.target.set(0, -2.3, 0);

scene.add(new THREE.HemisphereLight(0xdce5ec, 0x1a110b, 1.7));
const key = new THREE.DirectionalLight(0xffe1bc, 3.0);
key.position.set(4, 5, 7);
scene.add(key);
const fill = new THREE.DirectionalLight(0xb8d0ec, 1.1);
fill.position.set(-5, 1, -4);
scene.add(fill);

const grid = new THREE.GridHelper(5.4, 27, 0x4b4136, 0x242326);
grid.position.y = -4.82;
grid.material.transparent = true;
grid.material.opacity = 0.22;
scene.add(grid);

const selectionBounds = new THREE.Box3();
const selectionHelper = new THREE.Box3Helper(selectionBounds, 0xd8b17a);
selectionHelper.visible = false;
scene.add(selectionHelper);

const reviewLayer = new THREE.Group();
scene.add(reviewLayer);
const proximityLayer = new THREE.Group();
scene.add(proximityLayer);

const raycaster = new THREE.Raycaster();
raycaster.firstHitOnly = true;
const pointer = new THREE.Vector2();

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(window.__aetherToast);
  window.__aetherToast = setTimeout(() => toast.classList.remove('show'), 2200);
}

function classify(name) {
  if (name.startsWith('element-VX-')) return 'Butterfly element';
  if (name.startsWith('cable-VX-')) return 'Suspension cable';
  if (name.startsWith('led-LED-')) return 'Fixed LED head';
  if (name.includes('carrier')) return 'Rotating carrier';
  if (name.includes('canopy')) return 'Fixed canopy';
  return 'Coordination mesh';
}

function reviewNameFor(object) {
  let o = object;
  while (o && o !== modelRoot) {
    const n = o.name || '';
    if (/^(element-VX-|cable-VX-|led-LED-)/.test(n) || n.includes('carrier') || n.includes('canopy')) return n;
    o = o.parent;
  }
  return object.name || 'unnamed coordination mesh';
}

function vectorMm(v) {
  return `${Math.round(v.x * 1000)}, ${Math.round(v.y * 1000)}, ${Math.round(v.z * 1000)} mm`;
}

function makeTextSprite(text, accent = '#d8b17a') {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 128;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'rgba(8,8,10,.86)';
  ctx.strokeStyle = 'rgba(255,255,255,.12)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(8, 16, 496, 96, 20);
  ctx.fill();
  ctx.stroke();
  ctx.font = '600 34px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif';
  ctx.fillStyle = accent;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 256, 65);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false }));
  sprite.scale.set(0.54, 0.135, 1);
  return sprite;
}

function makePointMarker(point, color = 0xd8b17a, radius = 0.013) {
  const marker = new THREE.Mesh(
    new THREE.SphereGeometry(radius, 18, 12),
    new THREE.MeshBasicMaterial({ color, depthTest: false, transparent: true, opacity: 0.95 })
  );
  marker.position.copy(point);
  marker.renderOrder = 20;
  reviewLayer.add(marker);
  return marker;
}

function fitModel() {
  if (!modelRoot) return;
  const box = new THREE.Box3().setFromObject(modelRoot);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const distance = maxDim / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov * 0.5))) * 1.18;
  controls.target.copy(center);
  camera.position.set(center.x + distance * 0.48, center.y + maxDim * 0.04, center.z + distance);
  camera.near = Math.max(0.01, distance / 500);
  camera.far = Math.max(50, distance * 5);
  camera.updateProjectionMatrix();
  controls.update();
}

function updateStatus(message, state = 'ready') {
  loadStatus.textContent = message;
  status.classList.remove('ready', 'error');
  status.classList.add(state);
}

function prepareModel(root) {
  root.updateMatrixWorld(true);
  root.traverse((o) => {
    if (!o.isMesh) return;
    o.geometry.computeBoundingBox();
    o.geometry.computeBoundingSphere();
    if (!uniqueGeometries.has(o.geometry)) {
      o.geometry.computeBoundsTree({ indirect: true });
      uniqueGeometries.add(o.geometry);
    }
    o.userData.reviewName = reviewNameFor(o);
    pickableMeshes.push(o);
    if (o.userData.reviewName.startsWith('element-VX-')) elementMeshes.push(o);
  });
}

function pick(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  return raycaster.intersectObjects(pickableMeshes, false)[0] || null;
}

function removeObjectDeep(object) {
  object.traverse?.((o) => {
    o.geometry?.dispose?.();
    if (Array.isArray(o.material)) o.material.forEach((m) => m.dispose?.());
    else o.material?.dispose?.();
  });
  object.removeFromParent();
}

function clearProximity() {
  while (proximityLayer.children.length) removeObjectDeep(proximityLayer.children[0]);
  $('#nearestName').textContent = '—';
  $('#nearestDistance').textContent = '—';
}

function worldSphere(mesh) {
  const s = mesh.geometry.boundingSphere.clone();
  return s.applyMatrix4(mesh.matrixWorld);
}

function nearestElement(mesh, reviewName) {
  clearProximity();
  if (!reviewName.startsWith('element-VX-')) return;
  mesh.updateMatrixWorld(true);
  const sourceSphere = worldSphere(mesh);
  const candidates = elementMeshes
    .filter((m) => m !== mesh && m.userData.reviewName !== reviewName)
    .map((m) => {
      m.updateMatrixWorld(true);
      const s = worldSphere(m);
      return { mesh: m, lowerBound: Math.max(0, sourceSphere.center.distanceTo(s.center) - sourceSphere.radius - s.radius) };
    })
    .sort((a, b) => a.lowerBound - b.lowerBound);

  let best = null;
  const inv = mesh.matrixWorld.clone().invert();
  for (const candidate of candidates) {
    // Bounding-sphere separation is a conservative lower bound on surface
    // distance. Once it cannot beat the current exact result, no later
    // candidate can be closer. This preserves exact nearest-neighbour behavior
    // without an arbitrary candidate-count cap.
    if (best && candidate.lowerBound >= best.distance) break;

    const other = candidate.mesh;
    const geometryToBvh = inv.clone().multiply(other.matrixWorld);
    const onA = {};
    const onB = {};
    const result = mesh.geometry.boundsTree.closestPointToGeometry(
      other.geometry,
      geometryToBvh,
      onA,
      onB,
      0,
      best ? best.distance : Infinity
    );
    if (!result) continue;
    if (!best || result.distance < best.distance) {
      const aWorld = onA.point.clone().applyMatrix4(mesh.matrixWorld);
      const bWorld = onB.point.clone().applyMatrix4(other.matrixWorld);
      best = { distance: result.distance, mesh: other, aWorld, bWorld };
    }
  }

  if (!best) return;
  const name = best.mesh.userData.reviewName;
  const mm = best.distance * 1000;
  $('#nearestName').textContent = name.replace('element-', '');
  $('#nearestDistance').textContent = `${mm.toFixed(mm < 10 ? 1 : 0)} mm`;

  const lineGeom = new THREE.BufferGeometry().setFromPoints([best.aWorld, best.bWorld]);
  const line = new THREE.Line(lineGeom, new THREE.LineBasicMaterial({ color: 0xd8b17a, transparent: true, opacity: 0.75, depthTest: false }));
  line.renderOrder = 21;
  proximityLayer.add(line);
  for (const p of [best.aWorld, best.bWorld]) {
    const dot = new THREE.Mesh(new THREE.SphereGeometry(0.008, 12, 8), new THREE.MeshBasicMaterial({ color: 0xd8b17a, depthTest: false }));
    dot.position.copy(p);
    dot.renderOrder = 21;
    proximityLayer.add(dot);
  }
}

function selectHit(hit) {
  if (!hit) return;
  selectedMesh = hit.object;
  selectedReviewName = selectedMesh.userData.reviewName || reviewNameFor(selectedMesh);
  selectionBounds.setFromObject(selectedMesh);
  selectionHelper.visible = true;
  $('#selectionName').textContent = selectedReviewName;
  $('#selectionMeta').textContent = 'BVH-accelerated surface hit on coordination geometry.';
  $('#selectionType').textContent = classify(selectedReviewName);
  $('#selectionPoint').textContent = vectorMm(hit.point);
  nearestElement(selectedMesh, selectedReviewName);
}

function renderMeasurements() {
  const list = $('#measurementList');
  list.innerHTML = '';
  $('#measurementSummary').textContent = measurements.length ? `${measurements.length} review measurement${measurements.length === 1 ? '' : 's'}.` : 'No measurements yet.';
  for (const m of measurements) {
    const item = document.createElement('div');
    item.className = 'item';
    item.innerHTML = `<div class="itemHead"><b>M${m.id} · ${m.distanceMm.toFixed(m.distanceMm < 10 ? 1 : 0)} mm</b><button>Remove</button></div><small>${m.aName} → ${m.bName}</small>`;
    item.querySelector('button').onclick = () => {
      removeObjectDeep(m.group);
      measurements.splice(measurements.indexOf(m), 1);
      renderMeasurements();
    };
    list.appendChild(item);
  }
}

function beginOrFinishMeasurement(hit) {
  const name = hit.object.userData.reviewName || reviewNameFor(hit.object);
  if (!measureStart) {
    const marker = makePointMarker(hit.point, 0xc8d9e9);
    measureStart = { point: hit.point.clone(), name, marker };
    hint.textContent = 'Measure mode: click the second surface point.';
    showToast('First measurement point set');
    return;
  }

  measurementSeq += 1;
  const a = measureStart.point;
  const b = hit.point.clone();
  const distanceMm = a.distanceTo(b) * 1000;
  const group = new THREE.Group();
  reviewLayer.add(group);
  measureStart.marker.removeFromParent();
  group.add(measureStart.marker);
  group.add(makeDetachedMarker(b, 0xc8d9e9));
  const line = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([a, b]),
    new THREE.LineBasicMaterial({ color: 0xc8d9e9, depthTest: false, transparent: true, opacity: 0.88 })
  );
  line.renderOrder = 22;
  group.add(line);
  const label = makeTextSprite(`${distanceMm.toFixed(distanceMm < 10 ? 1 : 0)} mm`, '#c8d9e9');
  label.position.copy(a).lerp(b, 0.5).add(new THREE.Vector3(0, 0.035, 0));
  label.renderOrder = 23;
  group.add(label);
  measurements.push({ id: measurementSeq, distanceMm, aName: measureStart.name, bName: name, group });
  measureStart = null;
  hint.textContent = 'Measure mode: click two surface points.';
  renderMeasurements();
  showToast(`Measurement M${measurementSeq}: ${distanceMm.toFixed(0)} mm`);
}

function makeDetachedMarker(point, color) {
  const marker = new THREE.Mesh(
    new THREE.SphereGeometry(0.013, 18, 12),
    new THREE.MeshBasicMaterial({ color, depthTest: false, transparent: true, opacity: 0.95 })
  );
  marker.position.copy(point);
  marker.renderOrder = 22;
  return marker;
}

function saveAnnotations() {
  const data = annotations.map((a) => ({
    id: a.id,
    point: a.point.toArray(),
    nodeName: a.nodeName,
    note: a.note,
  }));
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function createAnnotationVisual(record) {
  const group = new THREE.Group();
  reviewLayer.add(group);
  const marker = makeDetachedMarker(record.point, 0xe6b47d);
  group.add(marker);
  const label = makeTextSprite(`A${record.id}`, '#e6b47d');
  label.position.copy(record.point).add(new THREE.Vector3(0, 0.045, 0));
  group.add(label);
  record.group = group;
}

function renderAnnotations() {
  const list = $('#annotationList');
  list.innerHTML = '';
  if (!annotations.length) {
    list.innerHTML = '<div class="muted">No local annotations yet.</div>';
    return;
  }
  for (const a of annotations) {
    const item = document.createElement('div');
    item.className = 'item';
    item.innerHTML = `<div class="itemHead"><b>A${a.id} · ${a.nodeName}</b><button>Remove</button></div><small>${vectorMm(a.point)}</small><input aria-label="Annotation A${a.id}" value="">`;
    const input = item.querySelector('input');
    input.value = a.note;
    input.onchange = () => { a.note = input.value.trim(); saveAnnotations(); };
    item.querySelector('button').onclick = () => {
      removeObjectDeep(a.group);
      annotations.splice(annotations.indexOf(a), 1);
      saveAnnotations();
      renderAnnotations();
    };
    list.appendChild(item);
  }
}

function addAnnotation(hit) {
  annotationSeq += 1;
  const record = {
    id: annotationSeq,
    point: hit.point.clone(),
    nodeName: hit.object.userData.reviewName || reviewNameFor(hit.object),
    note: '',
    group: null,
  };
  createAnnotationVisual(record);
  annotations.push(record);
  saveAnnotations();
  renderAnnotations();
  showToast(`Annotation A${record.id} added`);
}

function restoreAnnotations() {
  let saved = [];
  try { saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); } catch { saved = []; }
  for (const item of saved) {
    if (!Array.isArray(item.point) || item.point.length !== 3) continue;
    const record = {
      id: Number(item.id) || ++annotationSeq,
      point: new THREE.Vector3().fromArray(item.point),
      nodeName: item.nodeName || 'coordination point',
      note: item.note || '',
      group: null,
    };
    annotationSeq = Math.max(annotationSeq, record.id);
    createAnnotationVisual(record);
    annotations.push(record);
  }
  renderAnnotations();
}

function setMode(next) {
  mode = next;
  $$('.toolbar [data-mode]').forEach((b) => b.classList.toggle('active', b.dataset.mode === mode));
  if (measureStart) {
    measureStart.marker.removeFromParent();
    measureStart = null;
  }
  const messages = {
    inspect: 'Inspect mode: click an element, cable, head, carrier or canopy.',
    measure: 'Measure mode: click two surface points.',
    annotate: 'Annotate mode: click a surface point to add a local browser note.',
  };
  hint.textContent = messages[mode];
}

function clearReview() {
  if (measureStart) {
    measureStart.marker.removeFromParent();
    measureStart = null;
  }
  for (const m of [...measurements]) removeObjectDeep(m.group);
  for (const a of [...annotations]) removeObjectDeep(a.group);
  measurements.length = 0;
  annotations.length = 0;
  localStorage.removeItem(STORAGE_KEY);
  renderMeasurements();
  renderAnnotations();
  showToast('Local review data cleared');
}

$$('.toolbar [data-mode]').forEach((b) => b.onclick = () => setMode(b.dataset.mode));
$('#fitBtn').onclick = fitModel;
$('#clearBtn').onclick = clearReview;
$('#panelToggle').onclick = () => $('#panel').classList.add('closed');
$('#panelBtn').onclick = () => $('#panel').classList.toggle('closed');

renderer.domElement.addEventListener('pointerdown', (e) => {
  pointerDown = [e.clientX, e.clientY];
});
renderer.domElement.addEventListener('pointerup', (e) => {
  if (!pointerDown || Math.hypot(e.clientX - pointerDown[0], e.clientY - pointerDown[1]) > 5) return;
  pointerDown = null;
  const hit = pick(e);
  if (!hit) return;
  selectHit(hit);
  if (mode === 'measure') beginOrFinishMeasurement(hit);
  else if (mode === 'annotate') addAnnotation(hit);
});

const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);
loader.load(
  MODEL_URL,
  (gltf) => {
    modelRoot = gltf.scene;
    modelRoot.name = modelRoot.name || 'vx4800-coordination-root';
    scene.add(modelRoot);
    prepareModel(modelRoot);
    restoreAnnotations();
    fitModel();
    loading.classList.add('hide');
    updateStatus(`BVH ready · ${pickableMeshes.length} meshes · ${uniqueGeometries.size} shared geometries`);
  },
  (event) => {
    if (event.total) loadStatus.textContent = `Loading ${Math.round(event.loaded / event.total * 100)}%`;
  },
  (error) => {
    console.error(error);
    loading.classList.add('hide');
    updateStatus('Model load failed', 'error');
    showToast('Could not load the optimized coordination model');
  }
);

function resize() {
  const w = innerWidth;
  const h = innerHeight;
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize, { passive: true });

function animate() {
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
renderMeasurements();
renderAnnotations();
animate();
