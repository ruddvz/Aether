#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

BASE_PATH = Path(__file__).with_name("agent_cto.py")
BASE_MODULE_NAME = "_aether_agent_cto_base"
_spec = importlib.util.spec_from_file_location(BASE_MODULE_NAME, BASE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to load AETHERIA CTO base module from {BASE_PATH}")
_base = importlib.util.module_from_spec(_spec)
sys.modules[BASE_MODULE_NAME] = _base
_spec.loader.exec_module(_base)

Classification = _base.Classification
advise_expansion = _base.advise_expansion
evaluate_run_efficiency = _base.evaluate_run_efficiency
load_config = _base.load_config
select_capability_class = _base.select_capability_class
select_tier = _base.select_tier
should_reuse_operation = _base.should_reuse_operation

SCHEMA_VERSION = "aether-cto-runtime/v1"
VERIFICATION_STATES = {"passed", "failed", "not-executed", "skipped", "not-required"}
DECISIONS = {
    "stop-success",
    "proceed",
    "re-evaluate-tier-or-evidence-plan",
    "repair",
    "block-external-evidence",
}
CONDITIONAL_VISUAL_CHECK = "browser-visual-when-acceptance-is-visual"
REVIEW_CHECKS = {
    "independent-engineering-review",
    "qualified-photometry-evidence-review",
    "owner-release-review",
}
CURRENT_HEAD_CHECK = "release-current-head-verification"
BLOCKING_EXPANSION_CODES = {
    "protected-expansion-reason-missing",
    "expansion-not-authorised",
}


def _classification_from_dict(data: dict[str, Any]) -> Classification:
    return Classification(
        mode=str(data.get("mode", "edit")),
        authority_surface=str(data.get("authority_surface", "documentation")),
        risk=str(data.get("risk", "low")),
        blast_radius=str(data.get("blast_radius", "local")),
        reversibility=str(data.get("reversibility", "reversible")),
        evidence_state=str(data.get("evidence_state", "known")),
        delivery_stop=str(data.get("delivery_stop", "local-change")),
    )


def _classification_dict(classification: Classification) -> dict[str, str]:
    return {
        "mode": classification.mode,
        "authority_surface": classification.authority_surface,
        "risk": classification.risk,
        "blast_radius": classification.blast_radius,
        "reversibility": classification.reversibility,
        "evidence_state": classification.evidence_state,
        "delivery_stop": classification.delivery_stop,
    }


def _required_checks(
    frontier: list[str], *, visual_acceptance: bool
) -> tuple[list[str], list[str]]:
    required: list[str] = []
    not_required: list[str] = []
    for check in frontier:
        if check == "focused":
            continue
        if check == CONDITIONAL_VISUAL_CHECK and not visual_acceptance:
            not_required.append(check)
            continue
        required.append(check)
    return required, not_required


def _normalise_verification(
    frontier: list[str], supplied: dict[str, Any] | None, *, visual_acceptance: bool
) -> tuple[dict[str, str], list[str]]:
    supplied = supplied or {}
    required, not_required = _required_checks(frontier, visual_acceptance=visual_acceptance)
    states: dict[str, str] = {}

    for check in not_required:
        states[check] = "not-required"

    for check in required:
        raw = str(supplied.get(check, "not-executed"))
        if raw not in VERIFICATION_STATES:
            raise ValueError(
                f"Unknown verification state for {check}: {raw}; expected one of {', '.join(sorted(VERIFICATION_STATES))}"
            )
        if raw == "not-required":
            raise ValueError(f"Required verification cannot be marked not-required: {check}")
        states[check] = raw

    return states, required


def _limits_from_budget(budget: dict[str, Any]) -> dict[str, int | float]:
    return {
        "sources": budget.get("max_sources", float("inf")),
        "context_chars": budget.get(
            "context_chars", budget.get("soft_context_chars", float("inf"))
        ),
        "tool_calls": budget.get("tool_calls_before_reevaluation", float("inf")),
        "read_only_agents": budget.get("parallel_read_only_agents", float("inf")),
        "mutation_lanes": budget.get("parallel_mutation_lanes", 1),
        "repair_rounds": budget.get("repair_rounds", float("inf")),
    }


def reuse_decision(
    *,
    seen: set[str],
    key: str,
    protected_evidence: bool = False,
    state_changed: bool = False,
) -> dict[str, Any]:
    base = should_reuse_operation(
        seen=seen,
        key=key,
        protected_evidence=protected_evidence,
        state_changed=state_changed,
    )
    if protected_evidence:
        reason_code = "protected-current-proof-required"
    elif state_changed:
        reason_code = "fingerprint-changed"
    elif base["reuse"]:
        reason_code = "fingerprint-valid-reuse"
    else:
        reason_code = "no-reusable-operation"
    return {**base, "reason_code": reason_code}


def start_receipt(
    classification: Classification,
    *,
    repository_fingerprint: str,
    source_fingerprint: str = "",
    visual_acceptance: bool = False,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or load_config()
    selected = select_tier(classification, config)
    frontier = selected["verification_frontier"]
    verification, required = _normalise_verification(
        frontier, {}, visual_acceptance=visual_acceptance
    )

    return {
        "schema": SCHEMA_VERSION,
        "phase": "start",
        "classification": _classification_dict(classification),
        "tier": selected["tier"],
        "authority_surface": classification.authority_surface,
        "repository_fingerprint": repository_fingerprint,
        "source_fingerprint": source_fingerprint,
        "limits": _limits_from_budget(selected["budget"]),
        "actual": {},
        "verification_frontier": frontier,
        "required_verification": required,
        "verification": verification,
        "capability_class": select_capability_class(
            classification, visual_acceptance=visual_acceptance
        ),
        "duplicate_operations_suppressed": 0,
        "duplicate_operations_executed": 0,
        "expansion": None,
        "decision": "proceed",
        "reason_codes": ["classified", "bounded-work-authorised"],
    }


def _expansion_decision(
    *,
    tier: str,
    expansion: dict[str, Any] | None,
    config: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[str]]:
    if not expansion:
        return None, []

    result = advise_expansion(
        tier=tier,
        category=str(expansion["category"]),
        used=int(expansion["used"]),
        expected_decision_value=bool(expansion.get("expected_decision_value", False)),
        protected_proof=bool(expansion.get("protected_proof", False)),
        config=config,
    )
    reason = str(expansion.get("reason", "")).strip()
    protected_reason_missing = (
        bool(expansion.get("protected_proof", False))
        and result.get("reason_required") is True
        and not reason
    )
    payload = {
        "category": str(expansion["category"]),
        "used": int(expansion["used"]),
        "expected_decision_value": bool(
            expansion.get("expected_decision_value", False)
        ),
        "protected_proof": bool(expansion.get("protected_proof", False)),
        "reason": reason or None,
        "allowed_by_base": bool(result["allowed"]),
        "reason_required": bool(result["reason_required"]),
        "base_reason": str(result["reason"]),
    }
    codes: list[str] = []
    if protected_reason_missing:
        codes.append("protected-expansion-reason-missing")
    elif not result["allowed"]:
        codes.append("expansion-not-authorised")
    elif result["reason_required"]:
        codes.append("protected-expansion-reason-recorded")
    return payload, codes


def runtime_receipt(
    classification: Classification,
    *,
    phase: str,
    repository_fingerprint: str,
    source_fingerprint: str = "",
    usage: dict[str, Any] | None = None,
    verification: dict[str, Any] | None = None,
    acceptance_proven: bool = False,
    authority_violation: bool = False,
    evidence_claim_overstated: bool = False,
    visual_acceptance: bool = False,
    expansion: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if phase not in {"checkpoint", "finish"}:
        raise ValueError("runtime phase must be checkpoint or finish")

    config = config or load_config()
    usage = dict(usage or {})
    selected = select_tier(classification, config)
    tier = selected["tier"]
    frontier = selected["verification_frontier"]
    verification_states, required_checks = _normalise_verification(
        frontier, verification, visual_acceptance=visual_acceptance
    )

    failed = [check for check in required_checks if verification_states[check] == "failed"]
    unavailable = [
        check
        for check in required_checks
        if verification_states[check] in {"not-executed", "skipped"}
    ]
    missing_review = [check for check in unavailable if check in REVIEW_CHECKS]
    missing_current_head = CURRENT_HEAD_CHECK in unavailable

    required_verification_passed = all(
        verification_states[check] == "passed" for check in required_checks
    )
    review_required = any(check in REVIEW_CHECKS for check in required_checks)
    review_passed = all(
        verification_states.get(check) == "passed"
        for check in required_checks
        if check in REVIEW_CHECKS
    )
    current_head_required = CURRENT_HEAD_CHECK in required_checks
    current_head_passed = verification_states.get(CURRENT_HEAD_CHECK) == "passed"

    usage_for_base = dict(usage)
    usage_for_base.update(
        {
            "required_verification_passed": required_verification_passed,
            "required_engineering_review_passed": (not review_required) or review_passed,
            "current_head_proof_passed": (not current_head_required)
            or current_head_passed,
            "authority_violation": authority_violation,
            "evidence_claim_overstated": evidence_claim_overstated,
            "acceptance_proven": acceptance_proven,
        }
    )
    efficiency = evaluate_run_efficiency(classification, usage_for_base, config)
    expansion_receipt, expansion_codes = _expansion_decision(
        tier=tier, expansion=expansion, config=config
    )
    blocking_expansion = any(
        code in BLOCKING_EXPANSION_CODES for code in expansion_codes
    )

    duplicate_executed = int(usage.get("duplicate_operations_executed", 0))
    reason_codes: list[str] = []

    if authority_violation:
        reason_codes.append("authority-violation")
    if evidence_claim_overstated:
        reason_codes.append("evidence-claim-overstated")
    if failed:
        reason_codes.append("executed-verification-failed")
    if unavailable:
        reason_codes.append("required-verification-not-executed")
    if missing_review:
        reason_codes.append("required-review-unavailable")
    if missing_current_head:
        reason_codes.append("current-head-proof-unavailable")
    if efficiency["exceeded"]:
        reason_codes.append("budget-ceiling-exceeded")
    if duplicate_executed:
        reason_codes.append("duplicate-work-executed")
    reason_codes.extend(expansion_codes)

    if authority_violation or evidence_claim_overstated or failed:
        decision = "repair"
    elif unavailable:
        decision = "block-external-evidence"
    elif blocking_expansion:
        decision = "re-evaluate-tier-or-evidence-plan"
    elif efficiency["exceeded"] or duplicate_executed:
        decision = "re-evaluate-tier-or-evidence-plan"
    elif phase == "finish" and acceptance_proven and efficiency["quality_green"]:
        decision = "stop-success"
        reason_codes.append("acceptance-proven")
    else:
        decision = "proceed"
        reason_codes.append("more-work-still-has-acceptance-value")

    if decision not in DECISIONS:
        raise AssertionError(f"Unexpected runtime decision: {decision}")

    return {
        "schema": SCHEMA_VERSION,
        "phase": phase,
        "classification": _classification_dict(classification),
        "tier": tier,
        "authority_surface": classification.authority_surface,
        "repository_fingerprint": repository_fingerprint,
        "source_fingerprint": source_fingerprint,
        "limits": efficiency["limits"],
        "actual": efficiency["actual"],
        "verification_frontier": frontier,
        "required_verification": required_checks,
        "verification": verification_states,
        "quality_green": efficiency["quality_green"],
        "within_budget": efficiency["within_budget"],
        "efficient": (
            decision == "stop-success"
            and efficiency["within_budget"]
            and not efficiency["duplicate_waste_detected"]
        ),
        "duplicate_operations_suppressed": int(
            usage.get("duplicate_operations_suppressed", 0)
        ),
        "duplicate_operations_executed": duplicate_executed,
        "expansion": expansion_receipt,
        "decision": decision,
        "reason_codes": list(dict.fromkeys(reason_codes)),
    }


def _load_payload(path: str | None) -> dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AETHERIA CTO closed-loop runtime controller"
    )
    parser.add_argument(
        "--phase", choices=["start", "checkpoint", "finish"], required=True
    )
    parser.add_argument("--input", help="JSON input file; reads stdin when omitted")
    args = parser.parse_args()

    payload = _load_payload(args.input)
    classification = _classification_from_dict(payload.get("classification", {}))
    common = {
        "repository_fingerprint": str(payload.get("repository_fingerprint", "")),
        "source_fingerprint": str(payload.get("source_fingerprint", "")),
        "visual_acceptance": bool(payload.get("visual_acceptance", False)),
    }

    if args.phase == "start":
        result = start_receipt(classification, **common)
    else:
        result = runtime_receipt(
            classification,
            phase=args.phase,
            usage=payload.get("usage", {}),
            verification=payload.get("verification", {}),
            acceptance_proven=bool(payload.get("acceptance_proven", False)),
            authority_violation=bool(payload.get("authority_violation", False)),
            evidence_claim_overstated=bool(
                payload.get("evidence_claim_overstated", False)
            ),
            expansion=payload.get("expansion"),
            **common,
        )

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
