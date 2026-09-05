#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "fixtures/platform/web-quality-v1.json"
CATEGORIES = ("performance", "accessibility", "best-practices", "seo")
MODES = ("mobile", "desktop")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def enforce(report_dir: Path, config_path: Path) -> dict:
    config = load_json(config_path)
    errors: list[str] = []
    rows: list[dict] = []
    expected_version = config["toolchain"]["lighthouse"]

    for route in config["routes"]:
        for mode in MODES:
            report_path = report_dir / f"{route['id']}-{mode}.report.json"
            if not report_path.is_file():
                errors.append(f"missing Lighthouse report: {report_path.name}")
                continue
            report = load_json(report_path)
            actual_version = str(report.get("lighthouseVersion", ""))
            if actual_version != expected_version:
                errors.append(
                    f"{route['id']} {mode}: Lighthouse {actual_version or 'unknown'} != pinned {expected_version}"
                )
            scores: dict[str, float] = {}
            for category in CATEGORIES:
                category_data = report.get("categories", {}).get(category)
                score = None if category_data is None else category_data.get("score")
                if not isinstance(score, (int, float)):
                    errors.append(f"{route['id']} {mode}: missing numeric {category} score")
                    continue
                score = float(score)
                scores[category] = score
                minimum = float(route["lighthouseMinimum"][category])
                if score + 1e-12 < minimum:
                    errors.append(
                        f"{route['id']} {mode}: {category} score {score:.3f} below {minimum:.3f}"
                    )
            rows.append(
                {
                    "routeId": route["id"],
                    "mode": mode,
                    "finalUrl": report.get("finalDisplayedUrl") or report.get("finalUrl"),
                    "lighthouseVersion": actual_version,
                    "scores": scores,
                }
            )

    return {
        "schemaVersion": "1.0.0",
        "status": "pass" if not errors else "fail",
        "authority": "repository-software-qa",
        "runs": rows,
        "errors": errors,
        "notes": [
            "Lighthouse floors are software regression budgets, not product-performance or engineering claims.",
            "A passing emulated mobile audit is not evidence that every physical phone/browser combination has been tested."
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce AETHERIA Lighthouse category score budgets")
    parser.add_argument("report_dir", type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    summary = enforce(args.report_dir.resolve(), args.config.resolve())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
