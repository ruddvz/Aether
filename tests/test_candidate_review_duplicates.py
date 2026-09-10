import copy
import json
from pathlib import Path

from tools.photometry.candidate_review import evaluate_candidate


ROOT = Path(__file__).resolve().parents[1]


def test_duplicate_role_configurations_fail_closed():
    candidate = json.loads((ROOT / "tests/fixtures/photometry/candidate-pass.json").read_text())
    brief = json.loads((ROOT / "fixtures/vx4800/photometry/selection-brief.json").read_text())

    duplicate = copy.deepcopy(candidate["configurations"][0])
    duplicate["exactModelCode"] = "SECOND-CONFIGURATION"
    candidate["configurations"].append(duplicate)

    review = evaluate_candidate(candidate, brief)
    duplicates = [
        finding
        for finding in review["findings"]
        if finding["code"] == "duplicate-role-configurations"
    ]

    assert review["decision"] == "reject-for-now"
    assert len(duplicates) == 1
    assert duplicates[0]["severity"] == "blocker"
    assert "found 2" in duplicates[0]["message"]
    assert "SECOND-CONFIGURATION" in duplicates[0]["message"]
