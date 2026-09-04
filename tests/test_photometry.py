from pathlib import Path
import json
import subprocess
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.photometry.ies_lm63 import parse_ies, to_report
from tools.photometry.polar_svg import render_polar_svg

TEST_IES = ROOT / "tests/fixtures/photometry/synthetic-narrow.ies"


def test_lm63_parser_preserves_source_and_distribution():
    p = parse_ies(TEST_IES)
    assert p.version == "IESNA:LM-63-2002"
    assert p.tilt == "NONE"
    assert p.number_of_lamps == 1
    assert p.vertical_angles == [0,2,4,6,8,10,15,20,30,45]
    assert p.horizontal_angles == [0]
    assert p.candela[0][0] == 1000
    assert p.max_candela == (1000, 0, 0)
    assert len(p.sha256) == 64


def test_report_schema_and_synthetic_warning():
    p = parse_ies(TEST_IES)
    report = to_report(p, filename=TEST_IES.name, provenance_status="synthetic-test", manufacturer="AETHERIA TEST ONLY", model="SYNTHETIC-NARROW")
    schema = json.loads((ROOT / "schemas/aether-ies-report.schema.json").read_text())
    errors = list(Draft202012Validator(schema).iter_errors(report))
    assert not errors, [e.message for e in errors]
    assert "This report is not approved product photometry" in report["warnings"]
    assert report["photometry"]["estimatedBeam"]["fullWidthHalfMaximumDeg"] is not None


def test_polar_svg_is_generated(tmp_path):
    report = to_report(parse_ies(TEST_IES), filename=TEST_IES.name, provenance_status="synthetic-test")
    output = render_polar_svg(report, tmp_path / "polar.svg")
    s = output.read_text()
    assert s.startswith("<svg")
    assert "Normalized polar distribution" in s
    assert "1000 cd" in s


def test_cli_ingest_keeps_raw_file_untouched(tmp_path):
    before = TEST_IES.read_bytes()
    subprocess.run([
        sys.executable,
        str(ROOT / "scripts/ingest_ies.py"),
        str(TEST_IES),
        "--out", str(tmp_path),
        "--provenance", "synthetic-test",
        "--manufacturer", "AETHERIA TEST ONLY",
        "--model", "SYNTHETIC-NARROW",
    ], check=True)
    copied = tmp_path / TEST_IES.name
    assert copied.read_bytes() == before
    report = json.loads((tmp_path / "synthetic-narrow.report.json").read_text())
    assert report["integrity"]["sha256"] == parse_ies(TEST_IES).sha256

from tools.photometry.candidate_review import evaluate_candidate, render_markdown


def test_candidate_evaluator_accepts_complete_synthetic_candidate():
    candidate = json.loads((ROOT / "tests/fixtures/photometry/candidate-pass.json").read_text())
    brief = json.loads((ROOT / "fixtures/vx4800/photometry/selection-brief.json").read_text())
    review = evaluate_candidate(candidate, brief)
    assert review["counts"]["blocker"] == 0
    assert review["decision"] == "technical-shortlist"
    assert "Photometry candidate review" in render_markdown(review)


def test_candidate_evaluator_blocks_missing_photometry():
    candidate = json.loads((ROOT / "tests/fixtures/photometry/candidate-pass.json").read_text())
    candidate["review"]["officialPhotometryAvailable"] = False
    candidate["configurations"][0]["photometryStatus"] = "missing"
    candidate["configurations"][0]["iesPath"] = None
    candidate["configurations"][0]["iesSha256"] = None
    brief = json.loads((ROOT / "fixtures/vx4800/photometry/selection-brief.json").read_text())
    review = evaluate_candidate(candidate, brief)
    assert review["counts"]["blocker"] >= 2
    assert review["decision"] == "reject-for-now"


def test_candidate_schema_allows_honest_unknown_exact_fields():
    schema = json.loads((ROOT / "schemas/aether-photometry-candidate.schema.json").read_text())
    candidate = json.loads((ROOT / "fixtures/vx4800/photometry/candidates/reggiani-yori-evo-ghostrack-43.json").read_text())
    errors = list(Draft202012Validator(schema).iter_errors(candidate))
    assert not errors, [e.message for e in errors]
    assert candidate["configurations"][0]["exactModelCode"] is None
    assert candidate["configurations"][0]["opticCode"] is None


def test_candidate_evaluator_blocks_unconfirmed_exact_fields():
    candidate = json.loads((ROOT / "fixtures/vx4800/photometry/candidates/reggiani-yori-evo-ghostrack-43.json").read_text())
    brief = json.loads((ROOT / "fixtures/vx4800/photometry/selection-brief.json").read_text())
    review = evaluate_candidate(candidate, brief)
    codes = {f["code"] for f in review["findings"]}
    assert "exact-model-code-missing" in codes
    assert "optic-code-missing" in codes
    assert review["decision"] == "reject-for-now"


def test_measured_browser_adapter_node_suite():
    subprocess.run([
        "node",
        str(ROOT / "tests/js/measured-photometry-adapter.test.mjs"),
    ], check=True)
