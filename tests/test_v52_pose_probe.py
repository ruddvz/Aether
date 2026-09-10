import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_vx4800_presentation.py"
SPEC = importlib.util.spec_from_file_location("aether_v52_probe", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_emit_v52_released_pose_probe():
    data = MODULE.build()
    pose = {
        element["id"]: {
            key: element[key]
            for key in ("yaw", "foldL", "foldR", "roll", "pitch")
        }
        for element in data["elements"]
    }
    print("V52_POSE_PROBE_BEGIN")
    print(json.dumps(pose, separators=(",", ":"), sort_keys=True))
    print("V52_POSE_PROBE_SHA", MODULE.canonical_sha(data))
    print("V52_POSE_PROBE_END")
    assert False, "temporary probe: capture pinned CI release pose values"
