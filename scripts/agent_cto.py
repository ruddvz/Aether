#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / ".aether" / "agent-cto.json"

RISK = ["low", "moderate", "high", "critical"]
BLAST = ["local", "feature", "product", "generated-formats", "public", "release"]
REVERSIBILITY = ["reversible", "compensable", "hard-to-reverse"]
EVIDENCE = ["known", "resolvable", "missing-controlled-evidence", "blocked"]
DELIVERY = ["answer", "plan", "local-change", "pull-request", "merge", "release-verification"]


@dataclass(frozen=True)
class Classification:
    mode: str
    authority_surface: str
    risk: str
    blast_radius: str
    reversibility: str
    evidence_state: str
    delivery_stop: str


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _validate_choice(name: str, value: str, allowed: list[str]) -> None:
    if value not in allowed:
        raise ValueError(f"Unknown {name}: {value}; expected one of {', '.join(allowed)}")


def select_tier(classification: Classification, config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or load_config()
    _validate_choice("authority surface", classification.authority_surface, config["authority_surfaces"])
    _validate_choice("risk", classification.risk, RISK)
    _validate_choice("blast radius", classification.blast_radius, BLAST)
    _validate_choice("reversibility", classification.reversibility, REVERSIBILITY)
    _validate_choice("evidence state", classification.evidence_state, EVIDENCE)
    _validate_choice("delivery stop", classification.delivery_stop, DELIVERY)

    tier = "fast"
    reasons: list[str] = []

    if classification.authority_surface in {"public-inspector", "builder-validator"}:
        tier = "standard"
    if classification.risk == "moderate" or classification.blast_radius in {"feature", "generated-formats"}:
        tier = "standard"

    if classification.authority_surface in {"canonical-fixture", "schema", "source-geometry"}:
        tier = "deep"
    if classification.risk == "high" or classification.blast_radius in {"product", "public"}:
        tier = "deep"
    if classification.reversibility == "compensable" or classification.evidence_state == "missing-controlled-evidence":
        tier = "deep"

    if classification.authority_surface in {"photometry-evidence", "release-manufacturing"}:
        tier = "critical"
    if classification.risk == "critical" or classification.blast_radius == "release":
        tier = "critical"
    if classification.reversibility == "hard-to-reverse" or classification.delivery_stop == "release-verification":
        tier = "critical"

    if classification.authority_surface != "documentation":
        reasons.append(f"authority surface: {classification.authority_surface}")
    if classification.risk != "low":
        reasons.append(f"risk: {classification.risk}")
    if classification.blast_radius != "local":
        reasons.append(f"blast radius: {classification.blast_radius}")
    if classification.reversibility != "reversible":
        reasons.append(f"reversibility: {classification.reversibility}")
    if classification.evidence_state != "known":
        reasons.append(f"evidence state: {classification.evidence_state}")
    if classification.delivery_stop not in {"answer", "plan", "local-change"}:
        reasons.append(f"delivery stop: {classification.delivery_stop}")
    if not reasons:
        reasons.append("bounded local work with focused proof")

    return {
        "tier": tier,
        "budget": config["tiers"][tier],
        "budget_is_ceiling_not_target": True,
        "mutation_allowed": classification.delivery_stop not in {"answer", "plan"},
        "reasons": reasons,
        "verification_frontier": verification_frontier(classification, tier),
    }


def verification_frontier(classification: Classification, tier: str) -> list[str]:
    surface = classification.authority_surface
    checks = ["focused"]

    if surface == "presentation":
        checks += ["build-site", "browser-visual-when-acceptance-is-visual"]
    elif surface == "public-inspector":
        checks += ["pytest", "qa-web-geometry", "build-site", "browser-visual-when-acceptance-is-visual"]
    elif surface == "builder-validator":
        checks += ["validate-repository", "pytest"]
    elif surface in {"canonical-fixture", "schema"}:
        checks += [
            "validate-repository",
            "qa-geometry",
            "qa-web-geometry",
            "qa-optimized-web-geometry",
            "pytest",
            "build-site",
        ]
    elif surface == "source-geometry":
        checks += [
            "validate-repository",
            "qa-geometry",
            "qa-web-geometry",
            "qa-optimized-web-geometry",
            "pytest",
            "build-site",
            "independent-engineering-review",
        ]
    elif surface == "photometry-evidence":
        checks += ["validate-repository", "pytest", "qualified-photometry-evidence-review"]
    elif surface == "release-manufacturing":
        checks += [
            "validate-repository",
            "qa-geometry",
            "qa-web-geometry",
            "qa-optimized-web-geometry",
            "pytest",
            "build-site",
            "owner-release-review",
        ]

    if tier in {"deep", "critical"} and "independent-engineering-review" not in checks and surface not in {"photometry-evidence", "release-manufacturing"}:
        checks.append("independent-engineering-review")
    if classification.delivery_stop == "release-verification":
        checks.append("release-current-head-verification")
    return list(dict.fromkeys(checks))


def advise_expansion(
    *, tier: str, category: str, used: int, expected_decision_value: bool, protected_proof: bool = False, config: dict[str, Any] | None = None
) -> dict[str, Any]:
    config = config or load_config()
    if tier not in config["tiers"]:
        raise ValueError(f"Unknown tier: {tier}")
    budget = config["tiers"][tier]
    if category not in budget or not isinstance(budget[category], int):
        raise ValueError(f"Unknown finite budget category for {tier}: {category}")
    ceiling = budget[category]
    if used < 0:
        raise ValueError("used must be non-negative")

    if protected_proof:
        return {
            "allowed": True,
            "reevaluate": used >= ceiling,
            "reason_required": used >= ceiling,
            "reason": "protected engineering proof may exceed the ordinary ceiling, but the expansion reason must be recorded"
            if used >= ceiling
            else "protected engineering proof remains inside the ordinary ceiling",
        }

    if not expected_decision_value:
        return {
            "allowed": False,
            "reevaluate": used >= ceiling,
            "reason_required": False,
            "reason": "stop: additional work has no expected authority, engineering-evidence or release decision value",
        }

    if used >= ceiling:
        return {
            "allowed": False,
            "reevaluate": True,
            "reason_required": True,
            "reason": "ceiling reached: re-evaluate tier and evidence need before consuming more work",
        }

    return {
        "allowed": True,
        "reevaluate": False,
        "reason_required": False,
        "reason": "positive expected decision value and below the tier ceiling",
    }


def validate_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or load_config()
    errors: list[str] = []
    if config.get("value_of_information", {}).get("required_before_expansion") is not True:
        errors.append("value-of-information gate must be required before expansion")
    if config.get("telemetry", {}).get("raw_prompt") is not False:
        errors.append("telemetry must not retain raw prompts")
    if config.get("telemetry", {}).get("hidden_reasoning") is not False:
        errors.append("telemetry must not retain hidden reasoning")
    if config.get("telemetry", {}).get("private_data") is not False:
        errors.append("telemetry must not retain private data")

    for tier, budget in config.get("tiers", {}).items():
        if budget.get("parallel_mutation_lanes") != 1:
            errors.append(f"{tier}.parallel_mutation_lanes must remain 1")
        for key in ("max_sources", "tool_calls_before_reevaluation", "parallel_read_only_agents", "parallel_mutation_lanes", "repair_rounds"):
            value = budget.get(key)
            if not isinstance(value, int) or value < 0:
                errors.append(f"{tier}.{key} must be a non-negative integer ceiling")

    return {"ok": not errors, "errors": errors}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AETHERIA adaptive agent CTO governor")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--mode", default="edit")
    parser.add_argument("--authority-surface", default="documentation")
    parser.add_argument("--risk", default="low")
    parser.add_argument("--blast", default="local")
    parser.add_argument("--reversibility", default="reversible")
    parser.add_argument("--evidence", default="known")
    parser.add_argument("--delivery-stop", default="local-change")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.validate:
        result = validate_config()
        print(json.dumps(result, indent=2) if args.json else ("AETHERIA agent CTO config: PASS" if result["ok"] else "AETHERIA agent CTO config: FAIL\n" + "\n".join(f"- {item}" for item in result["errors"])))
        return 0 if result["ok"] else 1

    classification = Classification(
        mode=args.mode,
        authority_surface=args.authority_surface,
        risk=args.risk,
        blast_radius=args.blast,
        reversibility=args.reversibility,
        evidence_state=args.evidence,
        delivery_stop=args.delivery_stop,
    )
    result = {"classification": asdict(classification), **select_tier(classification)}
    print(json.dumps(result, indent=2) if args.json else f"AETHERIA tier: {result['tier']}\nMutation allowed: {'yes' if result['mutation_allowed'] else 'no'}\nReasons: {'; '.join(result['reasons'])}\nVerification: {', '.join(result['verification_frontier'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
