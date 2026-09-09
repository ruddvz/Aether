from scripts.agent_cto import Classification, advise_expansion, load_config, select_tier, validate_config


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
