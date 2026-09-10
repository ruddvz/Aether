from copy import deepcopy
import json
from pathlib import Path

from tools.photometry.candidate_review import evaluate_candidate


ROOT = Path(__file__).resolve().parents[1]


def test_candidate_evaluator_blocks_duplicate_role_configurations():
    candidate = json.loads((ROOT / "tests/fixtures/photometry/candidate-pass.json").read_text())
    brief = json.loads((ROOT / "fixtures/vx4800/photometry/selection-brief.json").read_text())

    duplicate = deepcopy(candidate["configurations"][0])
    duplicate["exactModelCode"] = "DUPLICATE-TEST"
    candidate["configurations"].append(duplicate)

    review = evaluate_candidate(candidate, brief)
    matches = [
        finding
        for finding in review["findings"]
        if finding["code"] == "duplicate-role-configurations"
    ]

    assert len(matches) == 1
    assert matches[0]["severity"] == "blocker"
    assert review["decision"] == "reject-for-now"
