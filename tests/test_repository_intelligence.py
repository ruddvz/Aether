from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "repository_intelligence.py"
SPEC = importlib.util.spec_from_file_location("aether_repository_intelligence", MODULE_PATH)
assert SPEC and SPEC.loader
ri = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ri
SPEC.loader.exec_module(ri)


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout.strip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_config() -> dict:
    return {
        "protocol": ri.PROTOCOL,
        "schema_version": 1,
        "extractor_version": "test-1",
        "hard_gate_provenance": ["deterministic", "declared"],
        "declarations": [".aether/repository-graph-declarations.json"],
        "exclude_prefixes": [
            ".git/",
            ".pytest_cache/",
            ".venv/",
            "__pycache__/",
            "node_modules/",
            "build/",
            "_site/",
        ],
        "generated_output_prefixes": ["build/", "_site/"],
        "budgets": {
            "max_nodes": 32,
            "max_depth": 4,
            "max_context_chars": 8000,
        },
        "validation_frontiers": {
            "presentation": ["presentation-check"],
            "public_surface": ["public-check"],
            "controlled_engineering": ["engineering-check"],
            "canonical_fixture": ["canonical-check"],
            "release_facing": ["release-check"],
        },
    }


def fixture_payload() -> dict:
    return {
        "$schema": "../../schemas/aether-fixture.schema.json",
        "identity": {
            "fixtureId": "vx4800-bf-01",
            "productCode": "VX4800-BF-01",
            "name": "VORTEX",
            "designRevision": "1.3.0",
            "presentationRevision": "5.2.0",
            "lifecycle": "prototype",
        },
        "optical": {"status": "conceptual"},
        "assets": [
            {
                "id": "composition-engineering-1.3.0",
                "role": "schedule",
                "path": "composition/engineering-v1.3.0.csv",
                "authority": "controlled",
                "sha256": "a" * 64,
            },
            {
                "id": "presentation-study-5.2.0",
                "role": "document",
                "path": "presentation/v5.2.0/study.json",
                "authority": "reference",
                "sha256": "b" * 64,
            },
            {
                "id": "presentation-runtime-5.2.0",
                "role": "source",
                "path": "presentation/v5.2.0/viewer.app.js",
                "authority": "visual",
                "sha256": "c" * 64,
            },
            {
                "id": "photometry-concept-5.2.0",
                "role": "photometry",
                "path": "photometry/concept-v5.2.0.json",
                "authority": "reference",
                "sha256": "d" * 64,
            },
            {
                "id": "geometry-manifest-1.3.0",
                "role": "document",
                "path": "geometry/manifest.json",
                "authority": "controlled",
                "sha256": "e" * 64,
            },
        ],
    }


def declarations_payload() -> dict:
    return {
        "protocol": ri.PROTOCOL,
        "nodes": [
            {
                "id": "output:build/vx4800",
                "kind": "derived_output_group",
                "label": "VX4800 product build",
                "path": "build/vx4800/",
                "authority": "derived",
            },
            {
                "id": "output:_site",
                "kind": "derived_output_group",
                "label": "GitHub Pages site",
                "path": "_site/",
                "authority": "derived",
            },
        ],
        "edges": [
            {
                "source": "output:build/vx4800",
                "target": "file:scripts/build_product.py",
                "relation": "BUILT_BY",
                "provenance": "declared",
                "authority": "build-contract",
            },
            {
                "source": "output:build/vx4800",
                "target": "file:fixtures/vx4800/fixture.json",
                "relation": "GENERATED_FROM",
                "provenance": "declared",
                "authority": "canonical-to-derived",
            },
            {
                "source": "output:_site",
                "target": "file:scripts/build_site.py",
                "relation": "BUILT_BY",
                "provenance": "declared",
                "authority": "build-contract",
            },
            {
                "source": "output:_site",
                "target": "output:build/vx4800",
                "relation": "GENERATED_FROM",
                "provenance": "declared",
                "authority": "derived-chain",
            },
            {
                "source": "file:fixtures/vx4800/fixture.json",
                "target": "file:scripts/validate_repository.py",
                "relation": "VALIDATED_BY",
                "provenance": "declared",
                "authority": "repository-validation",
            },
        ],
    }


def make_repo(tmp_path: Path) -> tuple[Path, dict]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "tests@example.invalid")
    git(repo, "config", "user.name", "AETHERIA Tests")

    config = minimal_config()
    write(repo / ".aether/repository-graph.json", json.dumps(config, indent=2) + "\n")
    write(
        repo / ".aether/repository-graph-declarations.json",
        json.dumps(declarations_payload(), indent=2) + "\n",
    )
    write(
        repo / "fixtures/vx4800/fixture.json",
        json.dumps(fixture_payload(), indent=2) + "\n",
    )
    write(repo / "fixtures/vx4800/composition/engineering-v1.3.0.csv", "id,size\n1,S\n")
    write(repo / "fixtures/vx4800/presentation/v5.2.0/study.json", '{"authority":"presentation-only"}\n')
    write(repo / "fixtures/vx4800/presentation/v5.2.0/viewer.app.js", "export const viewer = true\n")
    write(repo / "fixtures/vx4800/photometry/concept-v5.2.0.json", '{"status":"conceptual"}\n')
    write(repo / "fixtures/vx4800/geometry/manifest.json", '{"designRevision":"1.3.0"}\n')
    write(repo / "schemas/aether-fixture.schema.json", '{"type":"object"}\n')
    write(repo / "project.json", '{"brand":"AETHERIA"}\n')
    write(repo / "scripts/build_product.py", "from pathlib import Path\n")
    write(repo / "scripts/build_site.py", "from pathlib import Path\n")
    write(repo / "scripts/validate_repository.py", "from pathlib import Path\n")
    write(repo / "scripts/helper.py", "VALUE = 1\n")
    write(repo / "scripts/consumer.py", "from .helper import VALUE\n")
    write(repo / "tests/test_placeholder.py", "def test_placeholder():\n    assert True\n")
    write(repo / "notes/baseline.txt", "baseline\n")

    git(repo, "add", ".")
    git(repo, "commit", "-m", "baseline")
    return repo, config


def graph(repo: Path, config: dict):
    nodes, edges = ri.build_graph(repo, config)
    return nodes, edges


def build_snapshot(repo: Path, config: dict):
    nodes, edges = graph(repo, config)
    snapshot = ri.write_snapshot(repo, config, nodes, edges)
    return nodes, edges, snapshot


def test_build_status_is_fresh_then_tracked_edit_is_stale(tmp_path: Path):
    repo, config = make_repo(tmp_path)
    _, _, snapshot = build_snapshot(repo, config)
    current = ri.status(repo, config)
    assert current["fresh"] is True
    assert current["fingerprint"] == snapshot["fingerprint"]
    assert Path(snapshot["cache"]).is_file()
    assert Path(snapshot["cache"]).is_relative_to(ri.worktree_git_dir(repo))

    write(repo / "notes/baseline.txt", "changed\n")
    stale = ri.status(repo, config)
    assert stale["fresh"] is False
    assert stale["reason"] == "fingerprint-mismatch"
    assert stale["checks"]["source_state_digest"] is False


def test_untracked_source_invalidates_snapshot_but_generated_output_does_not(tmp_path: Path):
    repo, config = make_repo(tmp_path)
    build_snapshot(repo, config)

    write(repo / "build/vx4800/generated.json", '{"derived":true}\n')
    write(repo / "_site/index.html", "<p>derived</p>\n")
    assert ri.status(repo, config)["fresh"] is True

    write(repo / "notes/untracked.txt", "new source state\n")
    stale = ri.status(repo, config)
    assert stale["fresh"] is False
    assert stale["checks"]["source_state_digest"] is False


def test_worktree_cache_path_is_isolated(tmp_path: Path):
    repo, config = make_repo(tmp_path)
    git(repo, "branch", "parallel")
    worktree = tmp_path / "parallel-worktree"
    git(repo, "worktree", "add", str(worktree), "parallel")

    assert ri.cache_path(repo) != ri.cache_path(worktree)
    main_nodes, main_edges = graph(repo, config)
    wt_config = ri.load_config(worktree / ".aether/repository-graph.json")
    wt_nodes, wt_edges = graph(worktree, wt_config)
    ri.write_snapshot(repo, config, main_nodes, main_edges)
    ri.write_snapshot(worktree, wt_config, wt_nodes, wt_edges)
    assert ri.cache_path(repo).is_file()
    assert ri.cache_path(worktree).is_file()


def test_fixture_authority_and_revision_boundary_are_explicit(tmp_path: Path):
    repo, config = make_repo(tmp_path)
    nodes, edges = graph(repo, config)

    fixture = nodes["file:fixtures/vx4800/fixture.json"]
    controlled = nodes["file:fixtures/vx4800/composition/engineering-v1.3.0.csv"]
    presentation = nodes["file:fixtures/vx4800/presentation/v5.2.0/viewer.app.js"]
    photometry = nodes["file:fixtures/vx4800/photometry/concept-v5.2.0.json"]
    engineering_revision = nodes["revision:engineering:vx4800-bf-01:1.3.0"]
    presentation_revision = nodes["revision:presentation:vx4800-bf-01:5.2.0"]

    assert fixture.authority == "canonical"
    assert controlled.kind == "controlled_engineering_asset"
    assert controlled.authority == "controlled"
    assert presentation.kind == "presentation_asset"
    assert presentation.authority == "visual"
    assert engineering_revision.authority == "controlled"
    assert presentation_revision.authority == "visual"
    assert photometry.kind == "photometry_reference"
    assert photometry.authority == "reference"
    assert photometry.metadata["evidence_state"] == "conceptual"
    assert photometry.metadata["measured_photometry"] is False

    assert any(
        edge.source == presentation_revision.id
        and edge.target == engineering_revision.id
        and edge.relation == "DECLARES_DIVERGENCE_FROM"
        for edge in edges
    )


def test_generated_outputs_remain_derived_and_point_back_to_sources(tmp_path: Path):
    repo, config = make_repo(tmp_path)
    nodes, edges = graph(repo, config)

    assert nodes["output:build/vx4800"].authority == "derived"
    assert nodes["output:_site"].authority == "derived"
    assert any(
        edge.source == "output:build/vx4800"
        and edge.target == "file:fixtures/vx4800/fixture.json"
        and edge.relation == "GENERATED_FROM"
        for edge in edges
    )
    assert any(
        edge.source == "output:_site"
        and edge.target == "output:build/vx4800"
        and edge.relation == "GENERATED_FROM"
        for edge in edges
    )


def test_authority_validator_rejects_reverse_generation_and_photometry_promotion():
    nodes = {
        "canonical": ri.Node("canonical", "canonical_fixture", "canonical", authority="canonical"),
        "derived": ri.Node("derived", "derived_output_group", "derived", authority="derived"),
        "phot": ri.Node(
            "phot",
            "photometry_reference",
            "concept",
            authority="controlled",
            metadata={"evidence_state": "conceptual", "measured_photometry": True},
        ),
    }
    edges = [
        ri.Edge(
            "canonical",
            "derived",
            "GENERATED_FROM",
            "declared",
            "invalid-test",
            "test",
            "test",
        )
    ]
    errors = ri.validate_graph(nodes, edges)
    assert any("authority inversion" in error for error in errors)
    assert any("conceptual photometry promoted" in error for error in errors)


def test_reverse_impact_reaches_product_build_site_and_validator_without_reversing_authority(tmp_path: Path):
    repo, config = make_repo(tmp_path)
    nodes, edges = graph(repo, config)
    result = ri.impact_slice(
        nodes,
        edges,
        ["file:fixtures/vx4800/fixture.json"],
        max_nodes=32,
        max_depth=4,
    )
    impacted = {item["id"] for item in result["nodes"]}
    assert "product:vx4800-bf-01" in impacted
    assert "output:build/vx4800" in impacted
    assert "output:_site" in impacted
    assert "file:scripts/validate_repository.py" in impacted
    assert nodes["file:fixtures/vx4800/fixture.json"].authority == "canonical"
    assert nodes["output:build/vx4800"].authority == "derived"


def test_preflight_separates_canonical_derived_validation_and_conceptual_evidence(tmp_path: Path):
    repo, config = make_repo(tmp_path)
    nodes, edges, _ = build_snapshot(repo, config)
    resolution = ri.resolve_seeds(nodes, ["VX4800-BF-01"])
    packet = ri.preflight_packet(nodes, edges, resolution, config)

    canonical_ids = {item["id"] for item in packet["canonical_inputs"]}
    derived_ids = {item["id"] for item in packet["derived_outputs"]}
    unknown_ids = {item["id"] for item in packet["unknown_or_conceptual_evidence"]}
    assert "file:fixtures/vx4800/fixture.json" in canonical_ids
    assert "output:build/vx4800" in derived_ids
    assert "output:_site" in derived_ids
    assert "file:fixtures/vx4800/photometry/concept-v5.2.0.json" in unknown_ids
    assert packet["verification"]["level"] in {"canonical_fixture", "controlled_engineering"}


def test_bounded_context_is_cycle_safe_and_honours_node_limit():
    nodes = {
        key: ri.Node(key, "file", key, authority="unknown")
        for key in ("a", "b", "c")
    }
    edges = [
        ri.Edge("a", "b", "DEPENDS_ON", "deterministic", "test", "test", "test"),
        ri.Edge("b", "c", "DEPENDS_ON", "deterministic", "test", "test", "test"),
        ri.Edge("c", "a", "DEPENDS_ON", "deterministic", "test", "test", "test"),
    ]
    result = ri.bounded_context(
        nodes,
        edges,
        ["a"],
        max_nodes=2,
        max_depth=10,
        max_chars=5000,
    )
    assert result["node_count"] == 2
    assert result["truncated"] is True


def test_context_character_budget_truncates_payload():
    nodes = {
        f"n{i}": ri.Node(f"n{i}", "file", "x" * 200, authority="unknown")
        for i in range(8)
    }
    edges = [
        ri.Edge(f"n{i}", f"n{i + 1}", "DEPENDS_ON", "deterministic", "test", "test", "test")
        for i in range(7)
    ]
    result = ri.bounded_context(
        nodes,
        edges,
        ["n0"],
        max_nodes=8,
        max_depth=8,
        max_chars=900,
    )
    assert result["truncated"] is True
    assert result["node_count"] < 8


def test_seed_resolution_reports_unknown_and_ambiguous_without_guessing():
    nodes = {
        "one": ri.Node("one", "file", "One", metadata={"aliases": ["shared"]}),
        "two": ri.Node("two", "file", "Two", metadata={"aliases": ["shared"]}),
    }
    result = ri.resolve_seeds(nodes, ["shared", "missing"])
    assert result["resolved"] == []
    assert result["ambiguous"]["shared"] == ["one", "two"]
    assert result["unresolved"] == ["missing"]


def test_diff_impact_reports_delete_add_and_expected_scope_escalation(tmp_path: Path):
    repo, config = make_repo(tmp_path)
    baseline = git(repo, "rev-parse", "HEAD")
    (repo / "notes/baseline.txt").unlink()
    write(repo / "outside/new.txt", "outside scope\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "change scope")

    nodes, edges = graph(repo, config)
    packet = ri.diff_impact_packet(
        repo,
        nodes,
        edges,
        config,
        baseline,
        ["fixtures/"],
    )
    statuses = {(item["status"], item["path"]) for item in packet["changes"]}
    assert ("D", "notes/baseline.txt") in statuses
    assert ("A", "outside/new.txt") in statuses
    assert "notes/baseline.txt" in packet["unresolved_changes"]
    assert packet["scope_escalated"] is True
    assert "outside/new.txt" in packet["out_of_expected_scope"]
    assert packet["uncertainty"] is True
    assert packet["verification"]["uncertainty_escalated"] is True
    assert packet["verification"]["level"] == "controlled_engineering"


def test_declared_edge_must_reference_existing_node(tmp_path: Path):
    repo, config = make_repo(tmp_path)
    declaration_path = repo / ".aether/repository-graph-declarations.json"
    declarations = declarations_payload()
    declarations["edges"].append(
        {
            "source": "output:_site",
            "target": "file:missing.py",
            "relation": "BUILT_BY",
            "provenance": "declared",
            "authority": "bad",
        }
    )
    write(declaration_path, json.dumps(declarations, indent=2) + "\n")
    with pytest.raises(ValueError, match="missing node"):
        ri.build_graph(repo, config)


def test_product_identity_impact_reaches_derived_surfaces(tmp_path: Path):
    repo, config = make_repo(tmp_path)
    nodes, edges = graph(repo, config)
    result = ri.impact_slice(
        nodes,
        edges,
        ["product:vx4800-bf-01"],
        max_nodes=32,
        max_depth=4,
    )
    impacted = {item["id"] for item in result["nodes"]}
    assert "output:build/vx4800" in impacted
    assert "output:_site" in impacted
    assert nodes["product:vx4800-bf-01"].authority == "canonical"
    assert nodes["output:build/vx4800"].authority == "derived"
