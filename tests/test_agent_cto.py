import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "agent_cto.py"
SPEC = importlib.util.spec_from_file_location("aether_agent_cto", MODULE_PATH)
assert SPEC and SPEC.loader
agent_cto = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = agent_cto
SPEC.loader.exec_module(agent_cto)

Classification = agent_cto.Classification
advise_expansion = agent_cto.advise_expansion
evaluate_run_efficiency = agent_cto.evaluate_run_efficiency
load_config = agent_cto.load_config
operation_fingerprint = agent_cto.operation_fingerprint
select_capability_class = agent_cto.select_capability_class
select_tier = agent_cto.select_tier
should_parallelize = agent_cto.should_parallelize
should_reuse_operation = agent_cto.should_reuse_operation
validate_config = agent_cto.validate_config


def test_config_is_valid():
    result = validate_config(load_config())
    assert result["ok"], result["errors"]


def test_documentation_answer_is_fast_and_read_only():
    result = select_tier(
        Classification(
            mode="answer",
            authority_surface="documentation",
            risk="low",
            blast_radius="local",
            reversibility="reversible",
            evidence_state="known",
            delivery_stop="answer",
        )
    )
    assert result["tier"] == "fast"
    assert result["mutation_allowed"] is False


def test_presentation_visual_change_stays_bounded_but_gets_visual_proof():
    result = select_tier(
        Classification(
            mode="edit",
            authority_surface="presentation",
            risk="low",
            blast_radius="feature",
            reversibility="reversible",
            evidence_state="known",
            delivery_stop="local-change",
        )
    )
    assert result["tier"] == "standard"
    assert "build-site" in result["verification_frontier"]
    assert "browser-visual-when-acceptance-is-visual" in result["verification_frontier"]


def test_canonical_fixture_change_is_deep():
    result = select_tier(
        Classification(
            mode="edit",
            authority_surface="canonical-fixture",
            risk="moderate",
            blast_radius="generated-formats",
            reversibility="compensable",
            evidence_state="known",
            delivery_stop="pull-request",
        )
    )
    assert result["tier"] == "deep"
    assert "validate-repository" in result["verification_frontier"]
    assert "qa-geometry" in result["verification_frontier"]
    assert "qa-web-geometry" in result["verification_frontier"]
    assert "qa-optimized-web-geometry" in result["verification_frontier"]


def test_source_geometry_requires_deep_engineering_review():
    result = select_tier(
        Classification(
            mode="geometry-build",
            authority_surface="source-geometry",
            risk="high",
            blast_radius="product",
            reversibility="compensable",
            evidence_state="known",
            delivery_stop="pull-request",
        )
    )
    assert result["tier"] == "deep"
    assert "independent-engineering-review" in result["verification_frontier"]


def test_photometry_evidence_is_critical_and_not_generic_qa():
    result = select_tier(
        Classification(
            mode="validation",
            authority_surface="photometry-evidence",
            risk="high",
            blast_radius="product",
            reversibility="hard-to-reverse",
            evidence_state="missing-controlled-evidence",
            delivery_stop="pull-request",
        )
    )
    assert result["tier"] == "critical"
    assert "qualified-photometry-evidence-review" in result["verification_frontier"]


def test_release_manufacturing_is_critical():
    result = select_tier(
        Classification(
            mode="release",
            authority_surface="release-manufacturing",
            risk="critical",
            blast_radius="release",
            reversibility="hard-to-reverse",
            evidence_state="known",
            delivery_stop="release-verification",
        )
    )
    assert result["tier"] == "critical"
    assert "owner-release-review" in result["verification_frontier"]
    assert "release-current-head-verification" in result["verification_frontier"]


def test_no_value_means_stop_even_under_budget():
    result = advise_expansion(
        tier="fast",
        category="max_sources",
        used=1,
        expected_decision_value=False,
    )
    assert result["allowed"] is False
    assert "no expected" in result["reason"]


def test_ceiling_requires_reevaluation():
    result = advise_expansion(
        tier="standard",
        category="max_sources",
        used=10,
        expected_decision_value=True,
    )
    assert result["allowed"] is False
    assert result["reevaluate"] is True
    assert result["reason_required"] is True


def test_protected_proof_can_exceed_soft_ceiling_with_reason():
    result = advise_expansion(
        tier="critical",
        category="max_sources",
        used=30,
        expected_decision_value=True,
        protected_proof=True,
    )
    assert result["allowed"] is True
    assert result["reason_required"] is True


def test_duplicate_operation_reuses_only_when_current_and_unprotected():
    key = operation_fingerprint(
        kind="validator-read",
        target="fixture:vortex",
        source_fingerprint="engineering-rev-1.3.0",
        purpose="authority",
    )
    seen = {key}
    assert should_reuse_operation(seen=seen, key=key)["reuse"] is True
    assert should_reuse_operation(seen=seen, key=key, protected_evidence=True)["reuse"] is False
    assert should_reuse_operation(seen=seen, key=key, state_changed=True)["reuse"] is False


def test_capability_routing_tracks_authority_surface():
    docs = Classification("edit", "documentation", "low", "local", "reversible", "known", "local-change")
    geometry = Classification("edit", "source-geometry", "high", "product", "compensable", "known", "pull-request")
    photometry = Classification("validation", "photometry-evidence", "high", "product", "hard-to-reverse", "missing-controlled-evidence", "pull-request")

    assert select_capability_class(docs) == "routine-code-document-edit"
    assert select_capability_class(geometry) == "geometry-engineering-reasoning"
    assert select_capability_class(photometry) == "qualified-engineering-evidence-review"
    assert select_capability_class(docs, deterministic=True) == "deterministic-builder-validator"
    assert select_capability_class(docs, independent_review=True) == "independent-review"
    assert select_capability_class(docs, visual_acceptance=True) == "visual-browser-verification"


def test_parallelism_avoids_duplicate_or_shared_canonical_work():
    assert should_parallelize(independent=True)["parallel"] is True
    assert should_parallelize(independent=True, shared_authority_decision=True)["parallel"] is False
    assert should_parallelize(independent=True, shared_canonical_mutation=True)["parallel"] is False
    assert should_parallelize(independent=True, duplicated_context=True)["parallel"] is False
    assert should_parallelize(independent=True, decisive_evidence_already_found=True)["parallel"] is False


def test_efficient_presentation_run_stops_when_proven():
    classification = Classification(
        mode="edit",
        authority_surface="presentation",
        risk="low",
        blast_radius="feature",
        reversibility="reversible",
        evidence_state="known",
        delivery_stop="local-change",
    )
    result = evaluate_run_efficiency(
        classification,
        {
            "sources": 3,
            "context_chars": 9000,
            "tool_calls": 6,
            "read_only_agents": 0,
            "mutation_lanes": 1,
            "repair_rounds": 1,
            "duplicate_operations_suppressed": 2,
            "duplicate_operations_executed": 0,
            "required_verification_passed": True,
            "acceptance_proven": True,
            "authority_violation": False,
            "evidence_claim_overstated": False,
        },
    )
    assert result["within_budget"] is True
    assert result["quality_green"] is True
    assert result["efficient"] is True
    assert result["decision"] == "stop-success"


def test_deep_geometry_run_requires_engineering_review():
    classification = Classification(
        mode="geometry-build",
        authority_surface="source-geometry",
        risk="high",
        blast_radius="product",
        reversibility="compensable",
        evidence_state="known",
        delivery_stop="pull-request",
    )
    result = evaluate_run_efficiency(
        classification,
        {
            "sources": 6,
            "context_chars": 22000,
            "tool_calls": 10,
            "mutation_lanes": 1,
            "required_verification_passed": True,
            "required_engineering_review_passed": False,
            "acceptance_proven": True,
        },
    )
    assert result["quality_green"] is False
    assert result["decision"] == "repair-review-or-block"


def test_duplicate_execution_is_waste_even_when_quality_is_green():
    classification = Classification(
        mode="edit",
        authority_surface="documentation",
        risk="low",
        blast_radius="local",
        reversibility="reversible",
        evidence_state="known",
        delivery_stop="local-change",
    )
    result = evaluate_run_efficiency(
        classification,
        {
            "sources": 2,
            "context_chars": 4000,
            "tool_calls": 4,
            "mutation_lanes": 1,
            "duplicate_operations_executed": 1,
            "required_verification_passed": True,
            "acceptance_proven": True,
        },
    )
    assert result["quality_green"] is True
    assert result["duplicate_waste_detected"] is True
    assert result["efficient"] is False


def test_exceeding_budget_forces_re_evaluation():
    classification = Classification(
        mode="edit",
        authority_surface="documentation",
        risk="low",
        blast_radius="local",
        reversibility="reversible",
        evidence_state="known",
        delivery_stop="local-change",
    )
    result = evaluate_run_efficiency(
        classification,
        {
            "sources": 5,
            "required_verification_passed": True,
            "acceptance_proven": False,
        },
    )
    assert result["within_budget"] is False
    assert "sources" in result["exceeded"]
    assert result["decision"] == "re-evaluate-tier-or-evidence-plan"
