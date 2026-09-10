import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_vx4800_presentation.py"
SNAPSHOT = ROOT / "fixtures" / "vx4800" / "presentation" / "v5.2.0" / "released-pose.json"
SPEC = importlib.util.spec_from_file_location("aether_v52_release_pose", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_v52_release_pose_snapshot_covers_every_element_and_field():
    snapshot = json.loads(SNAPSHOT.read_text())
    assert snapshot["presentationRevision"] == "5.2.0"
    assert snapshot["expectedViewerDataSha256"] == "bb6014386e9422b7bf87969c28533e8e67645fb0afdc36965bac418be6865b4c"
    assert tuple(snapshot["poseFields"]) == MODULE.V52_POSE_FIELDS
    assert len(snapshot["elements"]) == 240
    assert set(snapshot["elements"]) == {f"VX-{index:03d}" for index in range(1, 241)}
    for values in snapshot["elements"].values():
        assert set(values) == set(MODULE.V52_POSE_FIELDS)


def test_v52_release_pose_overrides_computed_pose_drift_for_all_elements():
    snapshot = json.loads(SNAPSHOT.read_text())
    elements = [
        {
            "id": element_id,
            **{field: 999.0 for field in MODULE.V52_POSE_FIELDS},
        }
        for element_id in snapshot["elements"]
    ]

    MODULE._freeze_v52_release_pose(elements, snapshot)

    by_id = {element["id"]: element for element in elements}
    for element_id, expected in snapshot["elements"].items():
        for field in MODULE.V52_POSE_FIELDS:
            assert by_id[element_id][field] == expected[field]


def test_v52_build_preserves_immutable_viewer_fingerprint():
    data = MODULE.build()
    assert MODULE.canonical_sha(data) == "bb6014386e9422b7bf87969c28533e8e67645fb0afdc36965bac418be6865b4c"
