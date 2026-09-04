#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "fixtures/vx4800/fixture.json"
DEFAULT_PROFILE = ROOT / "fixtures/vx4800/interchange/export-profile-v1.json"
TARGETS = ("ifc", "gdtf", "mvr")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_source_contract(fixture: dict[str, Any], profile: dict[str, Any]) -> None:
    identity = fixture["identity"]
    if identity["fixtureId"] != profile["fixtureId"]:
        raise ValueError("fixtureId does not match interchange profile")
    if identity["designRevision"] != profile["designRevision"]:
        raise ValueError("design revision does not match interchange profile")

    invariants = profile["invariants"]
    family_counts = {family["id"]: family["count"] for family in fixture["composition"]["families"]}
    actual = {
        "elementCount": fixture["composition"]["elementCount"],
        "familyCounts": family_counts,
        "suspensionLineCount": fixture["composition"]["suspension"]["lineCount"],
        "fixedHeadCount": sum(emitter["quantity"] for emitter in fixture["optical"]["emitters"]),
    }
    for key, expected in invariants.items():
        if actual[key] != expected:
            raise ValueError(f"controlled interchange invariant changed for {key}: expected {expected!r}, got {actual[key]!r}")

    boundary = profile["authorityBoundary"]
    if any(boundary.values()):
        raise ValueError("interchange profile may not claim engineering or release authority")


def source_facts(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "productCode": fixture["identity"]["productCode"],
        "envelopeMm": fixture["physical"]["envelopeMm"],
        "elementCount": fixture["composition"]["elementCount"],
        "familyCounts": {family["id"]: family["count"] for family in fixture["composition"]["families"]},
        "suspensionLineCount": fixture["composition"]["suspension"]["lineCount"],
        "fixedHeadCount": sum(emitter["quantity"] for emitter in fixture["optical"]["emitters"]),
        "motionStatus": fixture["kinematics"]["status"],
        "opticalStatus": fixture["optical"]["status"],
        "massStatus": fixture["physical"]["massKg"]["status"],
    }


def build_report(fixture_path: Path, profile_path: Path, target: str) -> dict[str, Any]:
    if target not in TARGETS:
        raise ValueError(f"unsupported interchange target: {target}")

    fixture = load_json(fixture_path)
    profile = load_json(profile_path)
    validate_source_contract(fixture, profile)

    target_policy = profile["targets"][target]
    mappings = target_policy["mappings"]
    losses = target_policy["losses"]
    disposition_counts = {
        disposition: sum(1 for item in mappings if item["disposition"] == disposition)
        for disposition in ("preserved", "approximated", "omitted", "external-reference")
    }
    blocking_losses = sum(1 for item in losses if item["severity"] == "blocking")
    export_authority = target_policy["exportAuthority"]
    export_eligible = export_authority == "coordination-only" and blocking_losses == 0

    return {
        "$schema": "schemas/aether-interchange-loss-report.schema.json",
        "schemaVersion": "1.0.0",
        "fixtureId": fixture["identity"]["fixtureId"],
        "designRevision": fixture["identity"]["designRevision"],
        "authority": "derived-interchange-review",
        "target": target,
        "source": {
            "fixturePath": str(fixture_path.relative_to(ROOT)).replace("\\", "/"),
            "fixtureSha256": sha256(fixture_path),
        },
        "sourceFacts": source_facts(fixture),
        "mappings": mappings,
        "losses": losses,
        "summary": {
            "preserved": disposition_counts["preserved"],
            "approximated": disposition_counts["approximated"],
            "omitted": disposition_counts["omitted"],
            "externalReferences": disposition_counts["external-reference"],
            "blockingLosses": blocking_losses,
            "exportEligible": export_eligible,
            "exportAuthority": export_authority,
        },
        "authorityBoundary": profile["authorityBoundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic VX4800 interchange loss report")
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    fixture_path = args.fixture.resolve()
    profile_path = args.profile.resolve()
    report = build_report(fixture_path, profile_path, args.target)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")
    return 0 if report["summary"]["exportEligible"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
