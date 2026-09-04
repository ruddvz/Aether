from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/build_interchange_loss_report.py"
FIXTURE_PATH = ROOT / "fixtures/vx4800/fixture.json"
PROFILE_PATH = ROOT / "fixtures/vx4800/interchange/export-profile-v1.json"
SCHEMA_PATH = ROOT / "schemas/aether-interchange-loss-report.schema.json"

spec = importlib.util.spec_from_file_location("build_interchange_loss_report", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_all_target_reports_validate_and_preserve_controlled_counts():
    schema = json.loads(SCHEMA_PATH.read_text())
    validator = Draft202012Validator(schema)
    for target in module.TARGETS:
        report = module.build_report(FIXTURE_PATH, PROFILE_PATH, target)
        errors = sorted(validator.iter_errors(report), key=lambda error: list(error.path))
        assert not errors, [error.message for error in errors]
        assert report["fixtureId"] == "vx4800-bf-01"
        assert report["designRevision"] == "1.3.0"
        assert report["sourceFacts"]["elementCount"] == 240
        assert report["sourceFacts"]["familyCounts"] == {"S": 66, "M": 144, "L": 30}
        assert report["sourceFacts"]["suspensionLineCount"] == 240
        assert report["sourceFacts"]["fixedHeadCount"] == 14


def test_ifc_is_coordination_only_and_not_engineering_authority():
    report = module.build_report(FIXTURE_PATH, PROFILE_PATH, "ifc")
    assert report["summary"]["exportEligible"] is True
    assert report["summary"]["exportAuthority"] == "coordination-only"
    assert report["summary"]["blockingLosses"] == 0
    assert all(value is False for value in report["authorityBoundary"].values())
    assert any(loss["id"] == "IFC_NO_MANUFACTURING_GEOMETRY" for loss in report["losses"])


def test_gdtf_is_blocked_until_exact_head_and_control_personality_are_released():
    report = module.build_report(FIXTURE_PATH, PROFILE_PATH, "gdtf")
    assert report["summary"]["exportEligible"] is False
    assert report["summary"]["exportAuthority"] == "blocked"
    ids = {loss["id"] for loss in report["losses"] if loss["severity"] == "blocking"}
    assert ids == {"GDTF_EXACT_HEAD_UNRESOLVED", "GDTF_CONTROL_PERSONALITY_UNRESOLVED"}


def test_mvr_is_blocked_until_gdtf_dependency_and_aiming_are_released():
    report = module.build_report(FIXTURE_PATH, PROFILE_PATH, "mvr")
    assert report["summary"]["exportEligible"] is False
    assert report["summary"]["exportAuthority"] == "blocked"
    ids = {loss["id"] for loss in report["losses"] if loss["severity"] == "blocking"}
    assert ids == {"MVR_GDTF_DEPENDENCY_UNRESOLVED", "MVR_AIMING_NOT_RELEASED"}


def test_reports_are_deterministic_for_unchanged_source():
    first = module.build_report(FIXTURE_PATH, PROFILE_PATH, "ifc")
    second = module.build_report(FIXTURE_PATH, PROFILE_PATH, "ifc")
    assert first == second


def test_changed_controlled_counts_fail_before_report_generation():
    fixture = json.loads(FIXTURE_PATH.read_text())
    profile = json.loads(PROFILE_PATH.read_text())
    changed = copy.deepcopy(fixture)
    changed["composition"]["elementCount"] = 239
    with pytest.raises(ValueError, match="elementCount"):
        module.validate_source_contract(changed, profile)


def test_profile_cannot_claim_release_authority():
    fixture = json.loads(FIXTURE_PATH.read_text())
    profile = json.loads(PROFILE_PATH.read_text())
    changed = copy.deepcopy(profile)
    changed["authorityBoundary"]["manufacturingAuthority"] = True
    with pytest.raises(ValueError, match="authority"):
        module.validate_source_contract(fixture, changed)
