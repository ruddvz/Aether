#!/usr/bin/env python3
"""AETHERIA authority-aware repository intelligence.

The graph is a disposable index. It never becomes fixture, engineering,
photometry, manufacturing, or release authority.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / ".aether" / "repository-graph.json"
PROTOCOL = "aether-repository-intelligence/v1"
PROVENANCE = {"deterministic", "declared", "observed", "inferred"}
HARD_PROVENANCE = {"deterministic", "declared"}
IMPORT_RE = re.compile(
    r"(?:^|\n)\s*(?:import\s+(?:[^'\"\n]+?\s+from\s+)?|require\s*\(\s*)['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)


@dataclass
class Node:
    id: str
    kind: str
    label: str
    path: str | None = None
    authority: str = "unknown"
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    relation: str
    provenance: str
    authority: str
    source_ref: str
    extractor: str
    confidence: float = 1.0


def run_git(*args: str, root: Path = ROOT, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout.strip()


def load_config(path: Path = CONFIG_PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("protocol") != PROTOCOL:
        raise ValueError(f"unsupported graph protocol: {data.get('protocol')!r}")
    if not set(data.get("hard_gate_provenance", [])).issubset(HARD_PROVENANCE):
        raise ValueError("hard_gate_provenance may contain deterministic/declared only")
    budgets = data.get("budgets", {})
    for key in ("max_nodes", "max_depth", "max_context_chars"):
        if int(budgets.get(key, 0)) <= 0:
            raise ValueError(f"invalid graph budget: {key}")
    return data


def current_revision(root: Path = ROOT) -> str:
    return run_git("rev-parse", "HEAD", root=root)


def current_branch(root: Path = ROOT) -> str:
    value = run_git("rev-parse", "--abbrev-ref", "HEAD", root=root)
    return value or "DETACHED"


def worktree_git_dir(root: Path = ROOT) -> Path:
    raw = Path(run_git("rev-parse", "--git-dir", root=root))
    return raw if raw.is_absolute() else (root / raw).resolve()


def cache_path(root: Path = ROOT) -> Path:
    return worktree_git_dir(root) / "aether-repository-intelligence" / "graph.sqlite3"


def _excluded(rel: str, config: dict) -> bool:
    normalized = rel.replace(os.sep, "/").lstrip("./")
    for prefix in config.get("exclude_prefixes", []):
        clean = prefix.strip("/")
        if normalized == clean or normalized.startswith(clean + "/"):
            return True
        if clean == "__pycache__" and "/__pycache__/" in f"/{normalized}/":
            return True
    return False


def iter_source_files(root: Path, config: dict) -> list[Path]:
    listed = run_git(
        "ls-files", "--cached", "--others", "--exclude-standard", root=root
    ).splitlines()
    files: list[Path] = []
    for rel in sorted(set(listed)):
        if not rel or _excluded(rel, config):
            continue
        path = root / rel
        if path.is_file():
            files.append(path)
    return files


def declaration_digest(config: dict, root: Path = ROOT) -> str:
    digest = hashlib.sha256()
    rels = [CONFIG_PATH.name]
    config_rel = ".aether/repository-graph.json"
    rels = [config_rel, *config.get("declarations", [])]
    for rel in sorted(set(rels)):
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        path = root / rel
        digest.update(path.read_bytes() if path.exists() else b"<missing>")
        digest.update(b"\0")
    return digest.hexdigest()


def source_state_digest(config: dict, root: Path = ROOT) -> str:
    digest = hashlib.sha256()
    for path in iter_source_files(root, config):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        try:
            digest.update(path.read_bytes())
        except OSError:
            digest.update(b"<unreadable>")
        digest.update(b"\0")
    return digest.hexdigest()


def snapshot_fingerprint(
    config: dict,
    revision: str,
    source_digest: str,
    declarations: str,
) -> str:
    payload = {
        "protocol": config["protocol"],
        "schema_version": config["schema_version"],
        "extractor_version": config["extractor_version"],
        "revision": revision,
        "source_state_digest": source_digest,
        "declaration_digest": declarations,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def file_id(rel: str) -> str:
    return f"file:{rel}"


def classify_file(rel: str) -> tuple[str, str]:
    lower = rel.lower()
    name = Path(rel).name.lower()
    if re.fullmatch(r"fixtures/[^/]+/fixture\.json", rel):
        return "canonical_fixture", "canonical"
    if rel.startswith("schemas/"):
        return "schema", "contract"
    if "/presentation/" in f"/{lower}":
        return "presentation", "visual"
    if rel.startswith("site/"):
        return "public_surface", "presentation"
    if rel.startswith("tests/") or name.startswith("test_") or ".test." in name:
        return "test", "verification"
    if rel.startswith("scripts/"):
        if name.startswith(("validate_", "qa_", "check_")):
            return "validator", "verification"
        if name.startswith(("build_", "generate_", "export_", "optimize_", "assemble_")):
            return "builder", "code"
        return "script", "code"
    if rel.startswith("fixtures/"):
        return "fixture_record", "unknown"
    if rel.startswith("docs/") or rel.endswith(".md"):
        return "documentation", "advisory"
    return "file", "unknown"


def _text(path: Path, limit: int = 2_000_000) -> str | None:
    try:
        if path.stat().st_size > limit:
            return None
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def parse_python_imports(path: Path) -> list[str]:
    source = _text(path)
    if source is None:
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    result: list[str] = []
    for item in ast.walk(tree):
        if isinstance(item, ast.Import):
            result.extend(alias.name for alias in item.names)
        elif isinstance(item, ast.ImportFrom):
            module = item.module or ""
            prefix = "." * int(item.level or 0)
            if module or prefix:
                result.append(prefix + module)
    return result


def parse_js_imports(path: Path) -> list[str]:
    source = _text(path)
    return [] if source is None else [m.group(1) for m in IMPORT_RE.finditer(source)]


def module_candidates(import_name: str, rel: str) -> list[str]:
    base = Path(rel).parent
    candidates: list[str] = []
    if import_name.startswith("../") or import_name.startswith("./"):
        raw = import_name
        while raw.startswith("../"):
            base = base.parent
            raw = raw[3:]
        raw = raw.removeprefix("./")
        stem = (base / raw).as_posix()
        for suffix in (
            "", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
            "/index.js", "/index.mjs", "/index.ts", "/index.tsx",
        ):
            candidates.append(stem + suffix)
    elif import_name.startswith("."):
        dots = len(import_name) - len(import_name.lstrip("."))
        raw = import_name[dots:]
        for _ in range(max(0, dots - 1)):
            base = base.parent
        raw = raw.replace(".", "/")
        stem = (base / raw).as_posix() if raw else base.as_posix()
        candidates.extend([stem, stem + ".py", stem + "/__init__.py"])
    else:
        dotted = import_name.replace(".", "/")
        candidates.extend([f"{dotted}.py", f"{dotted}/__init__.py"])
    return list(dict.fromkeys(candidates))


def resolve_import(import_name: str, rel: str, rels: set[str]) -> str | None:
    for candidate in module_candidates(import_name, rel):
        if candidate in rels:
            return candidate
    if import_name.startswith("."):
        return None
    top = import_name.split(".", 1)[0]
    if not any(
        p == f"{top}/__init__.py" or p.endswith(f"/{top}/__init__.py")
        for p in rels
    ):
        return None
    matches = sorted(
        {
            existing
            for candidate in module_candidates(import_name, rel)
            for existing in rels
            if existing.endswith("/" + candidate)
        }
    )
    return matches[0] if len(matches) == 1 else None


def _normal_rel(base: Path, value: str, root: Path) -> str | None:
    try:
        candidate = (base / value).resolve()
        return candidate.relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return None


def _asset_kind(role: str, authority: str, path: str, status: str | None) -> str:
    if role == "photometry":
        return "photometry_reference" if status == "conceptual" or authority != "controlled" else "photometry_evidence"
    if authority == "controlled":
        return "controlled_engineering_asset"
    if authority == "visual":
        return "presentation_asset"
    if authority == "reference":
        return "reference_asset"
    return "fixture_asset"


def parse_fixture(
    fixture_path: Path,
    root: Path,
    nodes: dict[str, Node],
    edges: list[Edge],
) -> None:
    rel = fixture_path.relative_to(root).as_posix()
    try:
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    identity = data.get("identity", {})
    fixture_id = str(identity.get("fixtureId") or fixture_path.parent.name)
    product_code = str(identity.get("productCode") or fixture_id)
    name = str(identity.get("name") or product_code)
    design_revision = str(identity.get("designRevision") or "unknown")
    presentation_revision = str(identity.get("presentationRevision") or "unknown")
    product_node = f"product:{fixture_id}"
    engineering_node = f"revision:engineering:{fixture_id}:{design_revision}"
    presentation_node = f"revision:presentation:{fixture_id}:{presentation_revision}"
    nodes[product_node] = Node(
        product_node,
        "product",
        f"{name} / {product_code}",
        rel,
        "canonical",
        {
            "aliases": [fixture_id, product_code, name, fixture_path.parent.name],
            "design_revision": design_revision,
            "presentation_revision": presentation_revision,
            "lifecycle": identity.get("lifecycle"),
        },
    )
    nodes[engineering_node] = Node(
        engineering_node,
        "engineering_revision",
        f"{name} engineering {design_revision}",
        rel,
        "controlled",
        {"aliases": [design_revision, f"engineering {design_revision}"]},
    )
    nodes[presentation_node] = Node(
        presentation_node,
        "presentation_revision",
        f"{name} presentation {presentation_revision}",
        rel,
        "visual",
        {"aliases": [presentation_revision, f"presentation {presentation_revision}"]},
    )
    edges.extend(
        [
            Edge(product_node, file_id(rel), "DEPENDS_ON", "deterministic", "fixture-identity", rel, "fixture-parser"),
            Edge(engineering_node, file_id(rel), "DEPENDS_ON", "deterministic", "engineering-revision", rel, "fixture-parser"),
            Edge(presentation_node, engineering_node, "DECLARES_DIVERGENCE_FROM", "deterministic", "revision-boundary", rel, "fixture-parser"),
        ]
    )
    schema_ref = data.get("$schema")
    if isinstance(schema_ref, str):
        schema_rel = _normal_rel(fixture_path.parent, schema_ref, root)
        if schema_rel and file_id(schema_rel) in nodes:
            edges.append(
                Edge(file_id(rel), file_id(schema_rel), "VALIDATED_BY", "deterministic", "schema-contract", rel, "fixture-parser")
            )
    photometry_status = str(data.get("optical", {}).get("status") or "unknown")
    for asset in data.get("assets", []):
        if not isinstance(asset, dict) or not isinstance(asset.get("path"), str):
            continue
        asset_rel = _normal_rel(fixture_path.parent, asset["path"], root)
        if not asset_rel or file_id(asset_rel) not in nodes:
            continue
        authority = str(asset.get("authority") or "unknown")
        role = str(asset.get("role") or "unknown")
        status = photometry_status if role == "photometry" else None
        node = nodes[file_id(asset_rel)]
        node.authority = authority
        node.kind = _asset_kind(role, authority, asset_rel, status)
        node.metadata.update(
            {
                "asset_id": asset.get("id"),
                "role": role,
                "declared_authority": authority,
                "declared_sha256": asset.get("sha256"),
            }
        )
        if role == "photometry":
            node.metadata["evidence_state"] = photometry_status
            if status == "conceptual":
                node.metadata["measured_photometry"] = False
        edges.append(
            Edge(file_id(rel), file_id(asset_rel), "DEPENDS_ON", "deterministic", "fixture-asset-declaration", rel, "fixture-parser")
        )
        if authority == "controlled":
            edges.append(
                Edge(engineering_node, file_id(asset_rel), "DEPENDS_ON", "deterministic", "controlled-engineering", rel, "fixture-parser")
            )
        elif authority in {"reference", "visual"}:
            edges.append(
                Edge(presentation_node, file_id(asset_rel), "DEPENDS_ON", "deterministic", "presentation-reference", rel, "fixture-parser")
            )
    output_id = f"output:build/{fixture_path.parent.name}"
    if output_id in nodes:
        edges.append(
            Edge(output_id, file_id(rel), "GENERATED_FROM", "deterministic", "canonical-to-derived", rel, "fixture-parser")
        )
        edges.append(
            Edge(output_id, product_node, "PRESENTS", "deterministic", "derived-product-surface", rel, "fixture-parser")
        )


def load_declarations(
    root: Path,
    config: dict,
    nodes: dict[str, Node],
    edges: list[Edge],
) -> None:
    for rel in config.get("declarations", []):
        path = root / rel
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("protocol") != PROTOCOL:
            raise ValueError(f"unsupported declarations protocol in {rel}")
        for item in raw.get("nodes", []):
            node = Node(
                item["id"],
                item["kind"],
                item.get("label", item["id"]),
                item.get("path"),
                item.get("authority", "unknown"),
                item.get("metadata", {}),
            )
            nodes[node.id] = node
        for item in raw.get("edges", []):
            if item.get("provenance", "declared") != "declared":
                raise ValueError("repository graph declarations may contain declared edges only")
            if item["source"] not in nodes or item["target"] not in nodes:
                raise ValueError(f"declared edge references missing node: {item}")
            edges.append(
                Edge(
                    item["source"],
                    item["target"],
                    item["relation"],
                    "declared",
                    item.get("authority", "declaration"),
                    rel,
                    "declaration-loader",
                    float(item.get("confidence", 1.0)),
                )
            )


def validate_graph(nodes: dict[str, Node], edges: Sequence[Edge]) -> list[str]:
    errors: list[str] = []
    for edge in edges:
        if edge.provenance not in PROVENANCE:
            errors.append(f"invalid provenance {edge.provenance}: {edge.source}->{edge.target}")
        if edge.source not in nodes or edge.target not in nodes:
            errors.append(f"edge references missing node: {edge.source}->{edge.target}")
        if edge.relation == "GENERATED_FROM":
            source = nodes.get(edge.source)
            target = nodes.get(edge.target)
            if source and target and source.authority in {"canonical", "controlled"} and target.authority in {"derived", "visual", "reference"}:
                errors.append(f"authority inversion in GENERATED_FROM: {edge.source}->{edge.target}")
        if edge.relation == "DECLARES_DIVERGENCE_FROM":
            source = nodes.get(edge.source)
            target = nodes.get(edge.target)
            if source and target and source.authority in {"canonical", "controlled"}:
                errors.append(f"presentation divergence source has engineering authority: {edge.source}")
    for node in nodes.values():
        if node.kind == "photometry_reference" and node.metadata.get("evidence_state") == "conceptual":
            if node.authority == "controlled" or node.metadata.get("measured_photometry") is True:
                errors.append(f"conceptual photometry promoted to measured/control authority: {node.id}")
        if node.kind == "derived_output_group" and node.authority != "derived":
            errors.append(f"derived output group has non-derived authority: {node.id}")
    return errors


def build_graph(root: Path, config: dict) -> tuple[dict[str, Node], list[Edge]]:
    files = iter_source_files(root, config)
    rels = {path.relative_to(root).as_posix() for path in files}
    nodes: dict[str, Node] = {}
    edges: list[Edge] = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        kind, authority = classify_file(rel)
        nodes[file_id(rel)] = Node(file_id(rel), kind, Path(rel).name, rel, authority)
    load_declarations(root, config, nodes, edges)
    for path in files:
        rel = path.relative_to(root).as_posix()
        imports: list[str] = []
        if path.suffix == ".py":
            imports = parse_python_imports(path)
        elif path.suffix.lower() in {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}:
            imports = parse_js_imports(path)
        for import_name in imports:
            target = resolve_import(import_name, rel, rels)
            if not target or target == rel:
                continue
            edges.append(
                Edge(file_id(rel), file_id(target), "DEPENDS_ON", "deterministic", "source-import", rel, "import-extractor")
            )
    for path in files:
        rel = path.relative_to(root).as_posix()
        if re.fullmatch(r"fixtures/[^/]+/fixture\.json", rel):
            parse_fixture(path, root, nodes, edges)
    errors = validate_graph(nodes, edges)
    if errors:
        raise ValueError("graph authority validation failed:\n- " + "\n- ".join(errors))
    unique_edges = sorted(
        set(edges),
        key=lambda e: (e.source, e.target, e.relation, e.provenance, e.source_ref),
    )
    return nodes, unique_edges


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _initialize(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS metadata;
        DROP TABLE IF EXISTS edges;
        DROP TABLE IF EXISTS nodes;
        CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE nodes (
          id TEXT PRIMARY KEY,
          kind TEXT NOT NULL,
          label TEXT NOT NULL,
          path TEXT,
          authority TEXT NOT NULL,
          metadata_json TEXT NOT NULL
        );
        CREATE TABLE edges (
          source TEXT NOT NULL,
          target TEXT NOT NULL,
          relation TEXT NOT NULL,
          provenance TEXT NOT NULL,
          authority TEXT NOT NULL,
          source_ref TEXT NOT NULL,
          extractor TEXT NOT NULL,
          confidence REAL NOT NULL,
          FOREIGN KEY(source) REFERENCES nodes(id),
          FOREIGN KEY(target) REFERENCES nodes(id)
        );
        CREATE INDEX idx_edges_source ON edges(source);
        CREATE INDEX idx_edges_target ON edges(target);
        """
    )


def write_snapshot(root: Path, config: dict, nodes: dict[str, Node], edges: Sequence[Edge]) -> dict:
    revision = current_revision(root)
    branch = current_branch(root)
    source_digest = source_state_digest(config, root)
    declarations = declaration_digest(config, root)
    fingerprint = snapshot_fingerprint(config, revision, source_digest, declarations)
    db = cache_path(root)
    conn = _connect(db)
    _initialize(conn)
    metadata = {
        "protocol": config["protocol"],
        "schema_version": str(config["schema_version"]),
        "extractor_version": str(config["extractor_version"]),
        "source_revision": revision,
        "source_state_digest": source_digest,
        "declaration_digest": declarations,
        "branch": branch,
        "worktree_git_dir": str(worktree_git_dir(root)),
        "fingerprint": fingerprint,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    conn.executemany("INSERT INTO metadata(key,value) VALUES (?,?)", metadata.items())
    conn.executemany(
        "INSERT INTO nodes(id,kind,label,path,authority,metadata_json) VALUES (?,?,?,?,?,?)",
        [
            (
                node.id,
                node.kind,
                node.label,
                node.path,
                node.authority,
                json.dumps(node.metadata, sort_keys=True),
            )
            for node in nodes.values()
        ],
    )
    conn.executemany(
        "INSERT INTO edges(source,target,relation,provenance,authority,source_ref,extractor,confidence) VALUES (?,?,?,?,?,?,?,?)",
        [
            (
                edge.source,
                edge.target,
                edge.relation,
                edge.provenance,
                edge.authority,
                edge.source_ref,
                edge.extractor,
                edge.confidence,
            )
            for edge in edges
        ],
    )
    conn.commit()
    conn.close()
    return {
        **metadata,
        "cache": str(db),
        "nodes": len(nodes),
        "edges": len(edges),
    }


def read_snapshot(root: Path = ROOT) -> tuple[dict[str, Node], list[Edge], dict[str, str]]:
    db = cache_path(root)
    if not db.exists():
        raise FileNotFoundError(f"graph cache does not exist: {db}")
    conn = _connect(db)
    metadata = {row["key"]: row["value"] for row in conn.execute("SELECT key,value FROM metadata")}
    nodes = {
        row["id"]: Node(
            row["id"],
            row["kind"],
            row["label"],
            row["path"],
            row["authority"],
            json.loads(row["metadata_json"]),
        )
        for row in conn.execute("SELECT * FROM nodes")
    }
    edges = [
        Edge(
            row["source"],
            row["target"],
            row["relation"],
            row["provenance"],
            row["authority"],
            row["source_ref"],
            row["extractor"],
            float(row["confidence"]),
        )
        for row in conn.execute("SELECT * FROM edges")
    ]
    conn.close()
    return nodes, edges, metadata


def status(root: Path, config: dict) -> dict:
    db = cache_path(root)
    current = {
        "source_revision": current_revision(root),
        "source_state_digest": source_state_digest(config, root),
        "declaration_digest": declaration_digest(config, root),
        "branch": current_branch(root),
        "cache": str(db),
    }
    current["fingerprint"] = snapshot_fingerprint(
        config,
        current["source_revision"],
        current["source_state_digest"],
        current["declaration_digest"],
    )
    if not db.exists():
        return {**current, "fresh": False, "reason": "cache-missing"}
    _, _, metadata = read_snapshot(root)
    checks = {
        key: metadata.get(key) == current[key]
        for key in (
            "source_revision",
            "source_state_digest",
            "declaration_digest",
            "fingerprint",
        )
    }
    fresh = all(checks.values())
    return {
        **current,
        "fresh": fresh,
        "reason": "fresh" if fresh else "fingerprint-mismatch",
        "checks": checks,
        "snapshot": metadata,
    }


def require_fresh(root: Path, config: dict) -> tuple[dict[str, Node], list[Edge], dict[str, str]]:
    info = status(root, config)
    if not info["fresh"]:
        raise RuntimeError(f"graph snapshot is stale: {info['reason']}; run build")
    return read_snapshot(root)


def resolve_seeds(nodes: dict[str, Node], seeds: Sequence[str]) -> dict:
    resolved: list[str] = []
    unresolved: list[str] = []
    ambiguous: dict[str, list[str]] = {}
    for seed in seeds:
        if seed in nodes:
            resolved.append(seed)
            continue
        normalized = seed.strip().lower()
        matches: set[str] = set()
        for node in nodes.values():
            if node.path and node.path.lower() == normalized:
                matches.add(node.id)
            if node.label.lower() == normalized:
                matches.add(node.id)
            for alias in node.metadata.get("aliases", []):
                if str(alias).lower() == normalized:
                    matches.add(node.id)
        if len(matches) == 1:
            resolved.append(next(iter(matches)))
        elif len(matches) > 1:
            ambiguous[seed] = sorted(matches)
        else:
            unresolved.append(seed)
    return {
        "resolved": list(dict.fromkeys(resolved)),
        "unresolved": unresolved,
        "ambiguous": ambiguous,
    }


def _adjacency(edges: Sequence[Edge], undirected: bool) -> dict[str, list[tuple[str, Edge]]]:
    result: dict[str, list[tuple[str, Edge]]] = {}
    for edge in edges:
        result.setdefault(edge.source, []).append((edge.target, edge))
        if undirected:
            result.setdefault(edge.target, []).append((edge.source, edge))
    return result


def bounded_context(
    nodes: dict[str, Node],
    edges: Sequence[Edge],
    seed_ids: Sequence[str],
    *,
    max_nodes: int,
    max_depth: int,
    max_chars: int,
) -> dict:
    adjacency = _adjacency(edges, undirected=True)
    queue = deque((seed, 0) for seed in seed_ids)
    seen: dict[str, int] = {}
    truncated = False
    while queue:
        node_id, depth = queue.popleft()
        if node_id in seen:
            continue
        if len(seen) >= max_nodes:
            truncated = True
            break
        seen[node_id] = depth
        if depth >= max_depth:
            continue
        for neighbor, _ in adjacency.get(node_id, []):
            if neighbor not in seen:
                queue.append((neighbor, depth + 1))
    selected = [nodes[node_id] for node_id in sorted(seen)]
    selected_ids = set(seen)
    selected_edges = [
        edge for edge in edges if edge.source in selected_ids and edge.target in selected_ids
    ]
    payload = {
        "nodes": [asdict(node) | {"depth": seen[node.id]} for node in selected],
        "edges": [asdict(edge) for edge in selected_edges],
        "truncated": truncated,
    }
    encoded = json.dumps(payload, sort_keys=True)
    if len(encoded) > max_chars:
        keep = list(payload["nodes"])
        while keep and len(json.dumps({**payload, "nodes": keep, "edges": []}, sort_keys=True)) > max_chars:
            keep.pop()
        keep_ids = {item["id"] for item in keep}
        payload["nodes"] = keep
        payload["edges"] = [
            item
            for item in payload["edges"]
            if item["source"] in keep_ids and item["target"] in keep_ids
        ]
        payload["truncated"] = True
    payload["node_count"] = len(payload["nodes"])
    payload["edge_count"] = len(payload["edges"])
    return payload


def impact_slice(
    nodes: dict[str, Node],
    edges: Sequence[Edge],
    seed_ids: Sequence[str],
    *,
    max_nodes: int,
    max_depth: int,
) -> dict:
    downstream: dict[str, list[tuple[str, Edge]]] = {}
    for edge in edges:
        if edge.relation in {"DEPENDS_ON", "GENERATED_FROM", "BUILT_BY"}:
            downstream.setdefault(edge.target, []).append((edge.source, edge))
        elif edge.relation in {"VALIDATED_BY", "TESTED_BY", "PRESENTS", "RELEASES_TO", "OBSERVED_IN"}:
            downstream.setdefault(edge.source, []).append((edge.target, edge))
        elif edge.relation == "DECLARES_DIVERGENCE_FROM":
            downstream.setdefault(edge.target, []).append((edge.source, edge))
    queue = deque((seed, 0) for seed in seed_ids)
    seen: dict[str, int] = {}
    traversed: list[Edge] = []
    truncated = False
    while queue:
        current, depth = queue.popleft()
        if current in seen:
            continue
        if len(seen) >= max_nodes:
            truncated = True
            break
        seen[current] = depth
        if depth >= max_depth:
            continue
        for neighbor, edge in downstream.get(current, []):
            traversed.append(edge)
            if neighbor not in seen:
                queue.append((neighbor, depth + 1))
    ids = set(seen)
    return {
        "nodes": [asdict(nodes[node_id]) | {"depth": seen[node_id]} for node_id in sorted(ids)],
        "edges": [asdict(edge) for edge in traversed if edge.source in ids and edge.target in ids],
        "truncated": truncated,
        "node_count": len(ids),
    }


def verification_frontier(nodes: Iterable[Node], config: dict, *, uncertain: bool = False) -> dict:
    nodes = list(nodes)
    level = "presentation"
    paths = [node.path or "" for node in nodes]
    if any(node.authority == "canonical" or node.kind == "canonical_fixture" for node in nodes):
        level = "canonical_fixture"
    elif any(node.authority == "controlled" for node in nodes):
        level = "controlled_engineering"
    elif any(
        any(token in path for token in ("manufacturing/", "compliance/", "installation/", "interchange/"))
        for path in paths
    ):
        level = "release_facing"
    elif any(node.kind in {"public_surface", "derived_output_group"} and (node.path or "").startswith("_site") for node in nodes):
        level = "public_surface"
    commands = list(config["validation_frontiers"][level])
    if uncertain and level in {"presentation", "public_surface"}:
        level = "controlled_engineering"
        commands = list(config["validation_frontiers"][level])
    return {"level": level, "commands": commands, "uncertainty_escalated": uncertain}


def preflight_packet(
    nodes: dict[str, Node],
    edges: Sequence[Edge],
    seed_resolution: dict,
    config: dict,
) -> dict:
    budgets = config["budgets"]
    seeds = seed_resolution["resolved"]
    context = bounded_context(
        nodes,
        edges,
        seeds,
        max_nodes=int(budgets["max_nodes"]),
        max_depth=int(budgets["max_depth"]),
        max_chars=int(budgets["max_context_chars"]),
    )
    impact = impact_slice(
        nodes,
        edges,
        seeds,
        max_nodes=int(budgets["max_nodes"]),
        max_depth=int(budgets["max_depth"]),
    )
    packet_nodes = [nodes[item["id"]] for item in impact["nodes"]]
    combined_ids = {item["id"] for item in context["nodes"]} | {item["id"] for item in impact["nodes"]}
    combined = [nodes[node_id] for node_id in combined_ids]
    unknown_evidence = [
        asdict(node)
        for node in combined
        if node.authority == "unknown"
        or (
            node.kind == "photometry_reference"
            and node.metadata.get("evidence_state") == "conceptual"
        )
    ]
    uncertain = bool(seed_resolution["unresolved"] or seed_resolution["ambiguous"] or impact["truncated"])
    return {
        "seeds": seed_resolution,
        "canonical_inputs": [asdict(node) for node in combined if node.authority in {"canonical", "controlled"}],
        "derived_outputs": [asdict(node) for node in combined if node.authority == "derived"],
        "validators_and_tests": [asdict(node) for node in combined if node.kind in {"validator", "test"}],
        "unknown_or_conceptual_evidence": unknown_evidence,
        "public_or_release_surfaces": [
            asdict(node)
            for node in combined
            if node.kind in {"public_surface", "derived_output_group"}
            or any(token in (node.path or "") for token in ("manufacturing/", "compliance/", "installation/", "interchange/"))
        ],
        "context": context,
        "impact": impact,
        "verification": verification_frontier(packet_nodes or combined, config, uncertain=uncertain),
        "uncertainty": uncertain,
    }


def _parse_name_status(text: str) -> list[dict]:
    changes: list[dict] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        status_code = parts[0]
        kind = status_code[0]
        if kind in {"R", "C"} and len(parts) >= 3:
            changes.append({"status": kind, "old_path": parts[1], "path": parts[2]})
        elif len(parts) >= 2:
            changes.append({"status": kind, "path": parts[1]})
    return changes


def diff_changes(root: Path, base: str) -> list[dict]:
    committed = _parse_name_status(run_git("diff", "--name-status", f"{base}...HEAD", root=root))
    working = _parse_name_status(run_git("diff", "--name-status", root=root))
    untracked = run_git("ls-files", "--others", "--exclude-standard", root=root).splitlines()
    result = [*committed, *working, *({"status": "A", "path": p} for p in untracked if p)]
    unique: dict[tuple, dict] = {}
    for item in result:
        key = (item.get("status"), item.get("old_path"), item.get("path"))
        unique[key] = item
    return list(unique.values())


def diff_impact_packet(
    root: Path,
    nodes: dict[str, Node],
    edges: Sequence[Edge],
    config: dict,
    base: str,
    expected_prefixes: Sequence[str],
) -> dict:
    changes = diff_changes(root, base)
    seeds: list[str] = []
    unresolved: list[str] = []
    for change in changes:
        for key in ("old_path", "path"):
            path = change.get(key)
            if not path:
                continue
            node_id = file_id(path)
            if node_id in nodes:
                seeds.append(node_id)
            else:
                unresolved.append(path)
    budgets = config["budgets"]
    impact = impact_slice(
        nodes,
        edges,
        list(dict.fromkeys(seeds)),
        max_nodes=int(budgets["max_nodes"]),
        max_depth=int(budgets["max_depth"]),
    )
    impacted_nodes = [nodes[item["id"]] for item in impact["nodes"]]
    out_of_scope = []
    if expected_prefixes:
        for change in changes:
            path = change.get("path", "")
            if not any(path == prefix.rstrip("/") or path.startswith(prefix.rstrip("/") + "/") for prefix in expected_prefixes):
                out_of_scope.append(path)
    uncertain = bool(unresolved or impact["truncated"] or out_of_scope)
    return {
        "base": base,
        "changes": changes,
        "resolved_seed_ids": list(dict.fromkeys(seeds)),
        "unresolved_changes": sorted(set(unresolved)),
        "impact": impact,
        "scope_escalated": bool(out_of_scope),
        "out_of_expected_scope": sorted(set(out_of_scope)),
        "verification": verification_frontier(impacted_nodes, config, uncertain=uncertain),
        "uncertainty": uncertain,
    }


def _emit(payload: dict, json_mode: bool, title: str) -> None:
    if json_mode:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(title)
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            print(f"{key}: {value}")
        elif isinstance(value, list):
            print(f"{key}: {len(value)} item(s)")
        elif isinstance(value, dict):
            print(f"{key}: {json.dumps(value, sort_keys=True)}")


def _default_base(root: Path) -> str:
    if run_git("rev-parse", "--verify", "HEAD^", root=root, check=False):
        return "HEAD^"
    return "HEAD"


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    json_mode = "--json" in argv
    argv = [arg for arg in argv if arg != "--json"]
    parser = argparse.ArgumentParser(description="AETHERIA authority-aware repository graph")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build")
    sub.add_parser("status")
    for name in ("context", "impact", "preflight"):
        command = sub.add_parser(name)
        command.add_argument("seeds", nargs="+")
    diff_parser = sub.add_parser("diff-impact")
    diff_parser.add_argument("--base", default=None)
    diff_parser.add_argument("--expected-prefix", action="append", default=[])
    args = parser.parse_args(argv)
    config = load_config(ROOT / ".aether" / "repository-graph.json")

    if args.command == "build":
        nodes, edges = build_graph(ROOT, config)
        result = write_snapshot(ROOT, config, nodes, edges)
        _emit(result, json_mode, "AETHERIA repository graph built")
        return 0
    if args.command == "status":
        result = status(ROOT, config)
        _emit(result, json_mode, "AETHERIA repository graph status")
        return 0 if result["fresh"] else 2

    nodes, edges, metadata = require_fresh(ROOT, config)
    if args.command in {"context", "impact", "preflight"}:
        resolution = resolve_seeds(nodes, args.seeds)
        if args.command == "context":
            budgets = config["budgets"]
            result = {
                "snapshot": metadata,
                "seeds": resolution,
                "context": bounded_context(
                    nodes,
                    edges,
                    resolution["resolved"],
                    max_nodes=int(budgets["max_nodes"]),
                    max_depth=int(budgets["max_depth"]),
                    max_chars=int(budgets["max_context_chars"]),
                ),
            }
        elif args.command == "impact":
            budgets = config["budgets"]
            impact = impact_slice(
                nodes,
                edges,
                resolution["resolved"],
                max_nodes=int(budgets["max_nodes"]),
                max_depth=int(budgets["max_depth"]),
            )
            result = {
                "snapshot": metadata,
                "seeds": resolution,
                "impact": impact,
                "verification": verification_frontier(
                    [nodes[item["id"]] for item in impact["nodes"]],
                    config,
                    uncertain=bool(resolution["unresolved"] or resolution["ambiguous"] or impact["truncated"]),
                ),
            }
        else:
            result = {
                "snapshot": metadata,
                **preflight_packet(nodes, edges, resolution, config),
            }
        _emit(result, json_mode, f"AETHERIA repository graph {args.command}")
        return 3 if resolution["ambiguous"] else 0
    if args.command == "diff-impact":
        base = args.base or _default_base(ROOT)
        result = {
            "snapshot": metadata,
            **diff_impact_packet(
                ROOT,
                nodes,
                edges,
                config,
                base,
                args.expected_prefix,
            ),
        }
        _emit(result, json_mode, "AETHERIA repository graph diff impact")
        return 0
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"repository-intelligence error: {exc}", file=sys.stderr)
        raise SystemExit(2)
