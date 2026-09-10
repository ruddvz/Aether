import json

from scripts.generate_vx4800_presentation import build, canonical_sha


def test_emit_v52_released_pose_probe():
    data = build()
    pose = {
        element["id"]: {
            key: element[key]
            for key in ("yaw", "foldL", "foldR", "roll", "pitch")
        }
        for element in data["elements"]
    }
    print("V52_POSE_PROBE_BEGIN")
    print(json.dumps(pose, separators=(",", ":"), sort_keys=True))
    print("V52_POSE_PROBE_SHA", canonical_sha(data))
    print("V52_POSE_PROBE_END")
    assert False, "temporary probe: capture pinned CI release pose values"
