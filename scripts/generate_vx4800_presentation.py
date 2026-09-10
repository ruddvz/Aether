from pathlib import Path
import base64
import hashlib
import json
import math
import struct

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'fixtures/vx4800'
V52_DERIVED = FIX / 'presentation/v5.2.0/release-derived-state.json'
V52_ROW = struct.Struct('>B7d')
V52_FIELDS = ('yaw', 'foldL', 'foldR', 'roll', 'pitch', 'depthNorm', 'clearance')
SPAN = {'S': 108., 'M': 146., 'L': 186.}
LENGTH = {'S': 60., 'M': 82., 'L': 108.}


def canonical_sha(data):
    return hashlib.sha256(json.dumps(data, separators=(',', ':'), sort_keys=True).encode()).hexdigest()


def _load_v52_release_derived(study, schedule_ids):
    frozen = json.loads(V52_DERIVED.read_text())
    expected_fields = ['sizeCode', *V52_FIELDS]
    if frozen.get('schemaVersion') != '1.0.0':
        raise ValueError('Unsupported V5.2 derived-state schema')
    if frozen.get('presentationRevision') != '5.2.0':
        raise ValueError('V5.2 derived-state revision mismatch')
    if frozen.get('authority') != 'immutable-presentation-derived-state':
        raise ValueError('V5.2 derived-state authority mismatch')
    if frozen.get('expectedViewerDataSha256') != study.get('expectedViewerDataSha256'):
        raise ValueError('V5.2 derived-state viewer fingerprint mismatch')
    if frozen.get('fields') != expected_fields:
        raise ValueError('V5.2 derived-state field contract mismatch')
    if frozen.get('rowCount') != len(schedule_ids):
        raise ValueError('V5.2 derived-state row count does not match engineering schedule')

    try:
        payload = base64.b64decode(frozen['data'], validate=True)
    except Exception as exc:
        raise ValueError('Invalid V5.2 derived-state base64 payload') from exc
    if hashlib.sha256(payload).hexdigest() != frozen.get('payloadSha256'):
        raise ValueError('V5.2 derived-state payload SHA-256 mismatch')
    if len(payload) != len(schedule_ids) * V52_ROW.size:
        raise ValueError('V5.2 derived-state payload length mismatch')

    size_codes = {int(code): size for code, size in frozen.get('sizeCodes', {}).items()}
    if size_codes != {0: 'S', 1: 'M', 2: 'L'}:
        raise ValueError('V5.2 derived-state size-code contract mismatch')

    rows = []
    for index, element_id in enumerate(schedule_ids):
        values = V52_ROW.unpack_from(payload, index * V52_ROW.size)
        size_code, *derived = values
        if size_code not in size_codes:
            raise ValueError(f'Unknown V5.2 size code for {element_id}: {size_code}')
        rows.append((element_id, size_codes[size_code], dict(zip(V52_FIELDS, derived))))
    return rows


def _apply_v52_release_derived(elements, study):
    frozen_rows = _load_v52_release_derived(study, [element['id'] for element in elements])
    if len(frozen_rows) != len(elements):
        raise ValueError('V5.2 derived-state element coverage mismatch')
    for element, (element_id, size, derived) in zip(elements, frozen_rows):
        if element['id'] != element_id:
            raise ValueError('V5.2 derived-state order does not match engineering schedule')
        element['size'] = size
        element['span'] = SPAN[size]
        element['length'] = LENGTH[size]
        element.update(derived)


def _summary(elements, sched):
    counts = {size: sum(element['size'] == size for element in elements) for size in ('S', 'M', 'L')}
    folds = [(element['foldL'] + element['foldR']) / 2 for element in elements]
    large_clearance = [element['clearance'] for element in elements if element['size'] == 'L']
    return counts, {
        'foldMin': round(min(folds), 1),
        'foldMax': round(max(folds), 1),
        'foldMedian': round(float(np.median(folds)), 1),
        'cableMin': round(float(sched.finished_main_cable_mm.min()), 1),
        'cableMax': round(float(sched.finished_main_cable_mm.max()), 1),
        'largeMinClearance': round(float(min(large_clearance)), 1),
    }


def build():
    sched = pd.read_csv(FIX / 'composition/engineering-v1.3.0.csv')
    study = json.loads((FIX / 'presentation/v5.2.0/study.json').read_text())
    phot = json.loads((FIX / 'photometry/concept-v5.2.0.json').read_text())
    pts = np.c_[sched.ceiling_x_mm.to_numpy(), -sched.element_origin_drop_mm.to_numpy(), sched.ceiling_y_mm.to_numpy()]
    D = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
    D[D == 0] = np.inf
    nearest = D.min(axis=1)
    depth = ((sched.element_origin_drop_mm - sched.element_origin_drop_mm.min()) / (sched.element_origin_drop_mm.max() - sched.element_origin_drop_mm.min())).to_numpy()
    phase = np.arctan2(-sched.ceiling_y_mm.to_numpy(), sched.ceiling_x_mm.to_numpy())
    n = len(sched)
    nnorm = (nearest - nearest.min()) / (nearest.max() - nearest.min())
    score = .50 * (1 - depth) + .38 * nnorm + .12 * (np.sin(phase * 2.1 + np.arange(n) * .27) + 1) / 2
    order = np.argsort(score)
    sizes = np.array(['M'] * n, dtype=object)
    sizes[order[:54]] = 'S'
    sizes[order[-54:]] = 'L'
    gold = math.pi * (3 - math.sqrt(5))
    elements = []
    for i, r in sched.iterrows():
        s = sizes[i]
        sp = SPAN[s]
        d = depth[i]
        ph = phase[i]
        nn = nearest[i]
        base = 16 + 28 * d + 5.5 * math.sin(ph * 1.7 + i * .11) + 2.5 * math.sin(i * gold)
        ratio = min(1, max(0, (.84 * nn) / sp))
        min_fold = math.degrees(math.acos(ratio)) if ratio < 1 else 0
        base += -2 if s == 'L' else 2 if s == 'S' else 0
        f = max(12, min(58, max(base, min_fold)))
        asym = 2.6 * math.sin(i * gold * 1.9 + ph * .5)
        fl = max(9, min(62, f + asym))
        fr = max(9, min(62, f - asym))
        roll = 4.6 * math.sin(ph * 1.9 + i * .15)
        pitch = 3.4 * math.sin(ph - d * 2 + i * .09)
        yawtrim = 2.8 * math.sin(i * gold * .8 + ph * .35)
        elements.append({
            'id': r.element_id, 'size': s, 'x': float(r.ceiling_x_mm), 'z': float(r.ceiling_y_mm),
            'cable': float(r.finished_main_cable_mm), 'yoke': float(r.yoke_drop_mm),
            'drop': float(r.element_origin_drop_mm), 'bottom': float(r.lowest_edge_drop_mm),
            'yaw': float((r.target_yaw_deg + yawtrim) % 360), 'span': sp, 'length': LENGTH[s],
            'foldL': float(fl), 'foldR': float(fr), 'roll': float(roll), 'pitch': float(pitch),
            'depthNorm': float(d), 'clearance': float(nn),
        })

    if study['presentationRevision'] == '5.2.0':
        _apply_v52_release_derived(elements, study)
    counts, pose_stats = _summary(elements, sched)
    return {
        'version': study['presentationRevision'],
        'elements': elements,
        'counts': counts,
        'poseStats': pose_stats,
        'lighting': phot['heads'],
        'scene': {
            'imageAspect': 2 / 3, 'orthoHeight': 8.2, 'camera': [0, -5.1, 15.0],
            'target': [0, -2.88, 0], 'defaultRotorDeg': -12.0, 'defaultRPM': .36,
            'fixedOuterRadius': 1.26, 'rotorRadius': 1.14, 'centralHubRadius': .125,
            'vortexTurns': 1.72,
        },
    }


if __name__ == '__main__':
    data = build()
    out = ROOT / 'build/vx4800'
    out.mkdir(parents=True, exist_ok=True)
    p = out / 'viewer-data-v5.2.0.json'
    p.write_text(json.dumps(data, indent=2) + '\n')
    print(p)
    print(canonical_sha(data))
