from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "photometry" / "candidate_review.py"
SPEC = importlib.util.spec_from_file_location("aether_candidate_review", MODULE_PATH)
assert SPEC and SPEC.loader
candidate_review = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = candidate_review
SPEC.loader.exec_module(candidate_review)
evaluate_candidate = candidate_review.evaluate_candidate


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
