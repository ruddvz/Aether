from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "scripts" / "agent_cto_runtime.py"
MODULE_NAME = "_aether_agent_cto_runtime_test"
_spec = importlib.util.spec_from_file_location(MODULE_NAME, RUNTIME_PATH)
assert _spec is not None and _spec.loader is not None
runtime = importlib.util.module_from_spec(_spec)
sys.modules[MODULE_NAME] = runtime
_spec.loader.exec_module(runtime)


def classification(**overrides):
    values = {
        "mode": "edit",
        "authority_surface": "documentation",
        "risk": "low",
        "blast_radius": "local",
        "reversibility": "reversible",
        "evidence_state": "known",
        "delivery_stop": "local-change",
    }
    values.update(overrides)
    return runtime.Classification(**values)


def passing_verification(c, *, visual_acceptance=False):
    frontier = runtime.select_tier(c)["verification_frontier"]
    required, _ = runtime._required_checks(frontier, visual_acceptance=visual_acceptance)
    return {check: "passed" for check in required}


def base_usage(**overrides):
    values = {
        "sources": 1,
        "context_chars": 2000,
        "tool_calls": 2,
        "read_only_agents": 0,
        "mutation_lanes": 1,
        "repair_rounds": 0,
        "duplicate_operations_suppressed": 1,
        "duplicate_operations_executed": 0,
    }
    values.update(overrides)
    return values


def test_start_receipt_is_bounded_and_non_final():
    result = runtime.start_receipt(
        classification(),
        repository_fingerprint="repo-a",
        source_fingerprint="source-a",
    )
    assert result["schema"] == "aether-cto-runtime/v1"
    assert result["phase"] == "start"
    assert result["tier"] == "fast"
    assert result["decision"] == "proceed"
    assert result["repository_fingerprint"] == "repo-a"


def test_fast_green_finish_stops_successfully():
    c = classification()
    result = runtime.runtime_receipt(
        c,
        phase="finish",
        repository_fingerprint="repo-a",
        usage=base_usage(),
        verification=passing_verification(c),
        acceptance_proven=True,
    )
    assert result["decision"] == "stop-success"
    assert result["quality_green"] is True
    assert result["efficient"] is True


def test_green_checkpoint_proceeds_until_acceptance_is_proven():
    c = classification()
    result = runtime.runtime_receipt(
        c,
        phase="checkpoint",
        repository_fingerprint="repo-a",
        usage=base_usage(),
        verification=passing_verification(c),
        acceptance_proven=False,
    )
    assert result["decision"] == "proceed"
    assert result["efficient"] is False


def test_budget_ceiling_requires_re_evaluation_not_automatic_expansion():
    c = classification()
    result = runtime.runtime_receipt(
        c,
        phase="checkpoint",
        repository_fingerprint="repo-a",
        usage=base_usage(sources=99),
        verification=passing_verification(c),
    )
    assert result["decision"] == "re-evaluate-tier-or-evidence-plan"
    assert "budget-ceiling-exceeded" in result["reason_codes"]


def test_duplicate_execution_prevents_efficiency_success():
    c = classification()
    result = runtime.runtime_receipt(
        c,
        phase="finish",
        repository_fingerprint="repo-a",
        usage=base_usage(duplicate_operations_executed=1),
        verification=passing_verification(c),
        acceptance_proven=True,
    )
    assert result["decision"] == "re-evaluate-tier-or-evidence-plan"
    assert result["efficient"] is False
    assert "duplicate-work-executed" in result["reason_codes"]


def test_executed_required_validator_failure_means_repair():
    c = classification(authority_surface="builder-validator", risk="moderate")
    verification = passing_verification(c)
    verification["pytest"] = "failed"
    result = runtime.runtime_receipt(
        c,
        phase="checkpoint",
        repository_fingerprint="repo-a",
        usage=base_usage(),
        verification=verification,
    )
    assert result["decision"] == "repair"
    assert "executed-verification-failed" in result["reason_codes"]


def test_zero_step_or_not_executed_required_check_blocks_external_evidence():
    c = classification(authority_surface="builder-validator", risk="moderate")
    verification = passing_verification(c)
    verification["pytest"] = "not-executed"
    result = runtime.runtime_receipt(
        c,
        phase="checkpoint",
        repository_fingerprint="repo-a",
        usage=base_usage(),
        verification=verification,
    )
    assert result["decision"] == "block-external-evidence"
    assert "required-verification-not-executed" in result["reason_codes"]
    assert "executed-verification-failed" not in result["reason_codes"]


def test_missing_engineering_review_blocks_instead_of_triggering_code_repair():
    c = classification(
        authority_surface="source-geometry",
        risk="high",
        blast_radius="generated-formats",
    )
    verification = passing_verification(c)
    verification["independent-engineering-review"] = "not-executed"
    result = runtime.runtime_receipt(
        c,
        phase="finish",
        repository_fingerprint="repo-a",
        usage=base_usage(),
        verification=verification,
        acceptance_proven=True,
    )
    assert result["decision"] == "block-external-evidence"
    assert "required-review-unavailable" in result["reason_codes"]


def test_missing_photometry_acceptance_cannot_be_manufactured_by_more_agent_work():
    c = classification(
        authority_surface="photometry-evidence",
        risk="critical",
        evidence_state="missing-controlled-evidence",
    )
    verification = passing_verification(c)
    verification["qualified-photometry-evidence-review"] = "not-executed"
    result = runtime.runtime_receipt(
        c,
        phase="finish",
        repository_fingerprint="repo-a",
        usage=base_usage(),
        verification=verification,
        acceptance_proven=True,
    )
    assert result["decision"] == "block-external-evidence"
    assert "required-review-unavailable" in result["reason_codes"]


def test_release_without_current_head_proof_blocks():
    c = classification(
        authority_surface="release-manufacturing",
        risk="critical",
        blast_radius="release",
        reversibility="hard-to-reverse",
        delivery_stop="release-verification",
    )
    verification = passing_verification(c)
    verification["release-current-head-verification"] = "not-executed"
    result = runtime.runtime_receipt(
        c,
        phase="finish",
        repository_fingerprint="repo-a",
        usage=base_usage(),
        verification=verification,
        acceptance_proven=True,
    )
    assert result["decision"] == "block-external-evidence"
    assert "current-head-proof-unavailable" in result["reason_codes"]


def test_protected_expansion_at_ceiling_requires_explicit_reason():
    c = classification()
    ceiling = runtime.select_tier(c)["budget"]["max_sources"]
    result = runtime.runtime_receipt(
        c,
        phase="checkpoint",
        repository_fingerprint="repo-a",
        usage=base_usage(),
        verification=passing_verification(c),
        expansion={
            "category": "max_sources",
            "used": ceiling,
            "expected_decision_value": True,
            "protected_proof": True,
        },
    )
    assert result["decision"] == "re-evaluate-tier-or-evidence-plan"
    assert "protected-expansion-reason-missing" in result["reason_codes"]


def test_protected_expansion_with_reason_can_continue_but_is_not_success_at_checkpoint():
    c = classification()
    ceiling = runtime.select_tier(c)["budget"]["max_sources"]
    result = runtime.runtime_receipt(
        c,
        phase="checkpoint",
        repository_fingerprint="repo-a",
        usage=base_usage(),
        verification=passing_verification(c),
        expansion={
            "category": "max_sources",
            "used": ceiling,
            "expected_decision_value": True,
            "protected_proof": True,
            "reason": "current controlled evidence is required to settle the engineering claim",
        },
    )
    assert result["decision"] == "proceed"
    assert result["efficient"] is False
    assert "protected-expansion-reason-recorded" in result["reason_codes"]


def test_stale_source_or_repository_state_invalidates_ordinary_reuse():
    result = runtime.reuse_decision(
        seen={"read|fixture|sha-a|impact"},
        key="read|fixture|sha-a|impact",
        state_changed=True,
    )
    assert result["reuse"] is False
    assert result["reason_code"] == "fingerprint-changed"


def test_protected_evidence_never_uses_ordinary_cache():
    result = runtime.reuse_decision(
        seen={"read|release|sha-a|proof"},
        key="read|release|sha-a|proof",
        protected_evidence=True,
    )
    assert result["reuse"] is False
    assert result["reason_code"] == "protected-current-proof-required"


def test_authority_reversal_attempt_can_never_finish_green():
    c = classification(authority_surface="canonical-fixture", risk="high")
    result = runtime.runtime_receipt(
        c,
        phase="finish",
        repository_fingerprint="repo-a",
        usage=base_usage(),
        verification=passing_verification(c),
        acceptance_proven=True,
        authority_violation=True,
    )
    assert result["decision"] == "repair"
    assert result["efficient"] is False
    assert "authority-violation" in result["reason_codes"]
