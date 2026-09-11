#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "fixtures/platform/web-quality-v1.json"
DEFAULT_LIGHTHOUSE = ROOT / "qa/node_modules/.bin/lighthouse"
MODES = ("mobile", "desktop")
CATEGORIES = ("performance", "accessibility", "best-practices", "seo")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_audit_jobs(config: dict, base_url: str) -> list[dict]:
    base = base_url.rstrip("/") + "/"
    jobs: list[dict] = []
    for route in config["routes"]:
        url = urljoin(base, route["path"].lstrip("/"))
        for mode in MODES:
            jobs.append({"routeId": route["id"], "mode": mode, "url": url})
    return jobs


def classify_failure(returncode: int | None, timed_out: bool, report_path: Path) -> str:
    if timed_out:
        return "audit-timeout"
    if returncode not in (None, 0):
        return "audit-transport-or-browser"
    if not report_path.is_file():
        return "missing-report"
    return "malformed-report"


def write_early_failure(summary_path: Path, jobs: list[dict], failure_type: str, message: str) -> dict:
    summary = {
        "schemaVersion": "1.0.0",
        "status": "fail",
        "authority": "repository-software-qa",
        "expectedReports": len(jobs),
        "producedReports": 0,
        "runs": [],
        "failures": [{"failureType": failure_type, "message": message}],
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def run_audits(
    *,
    config_path: Path,
    base_url: str,
    report_dir: Path,
    summary_path: Path,
    chrome_path: Path,
    lighthouse_cli: Path,
    attempts: int = 2,
    timeout_seconds: int = 120,
) -> dict:
    config = load_json(config_path)
    expected_version = str(config["toolchain"]["lighthouse"])
    report_dir.mkdir(parents=True, exist_ok=True)
    jobs = build_audit_jobs(config, base_url)

    if not chrome_path.is_file():
        return write_early_failure(
            summary_path,
            jobs,
            "chrome-executable-missing",
            f"Chromium executable does not exist: {chrome_path}",
        )
    if not lighthouse_cli.is_file():
        return write_early_failure(
            summary_path,
            jobs,
            "lighthouse-cli-missing",
            f"Lighthouse CLI does not exist: {lighthouse_cli}",
        )

    env = os.environ.copy()
    env["CHROME_PATH"] = str(chrome_path)
    runs: list[dict] = []
    failures: list[dict] = []

    for job in jobs:
        stem = f"{job['routeId']}-{job['mode']}"
        report_path = report_dir / f"{stem}.report.json"
        attempt_rows: list[dict] = []
        final_error: dict | None = None

        for attempt in range(1, attempts + 1):
            if report_path.exists():
                report_path.unlink()

            log_path = report_dir / f"{stem}.attempt-{attempt}.log.txt"
            command = [
                str(lighthouse_cli),
                job["url"],
                "--quiet",
                "--only-categories=" + ",".join(CATEGORIES),
                "--output=json",
                f"--output-path={report_path}",
                "--chrome-flags=--headless=new --no-sandbox --disable-dev-shm-usage",
                "--max-wait-for-load=45000",
            ]
            if job["mode"] == "desktop":
                command.append("--preset=desktop")

            timed_out = False
            returncode: int | None = None
            output = ""
            try:
                completed = subprocess.run(
                    command,
                    cwd=ROOT,
                    env=env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=timeout_seconds,
                    check=False,
                )
                returncode = completed.returncode
                output = completed.stdout or ""
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                stdout = exc.stdout or ""
                stderr = exc.stderr or ""
                if isinstance(stdout, bytes):
                    stdout = stdout.decode("utf-8", errors="replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode("utf-8", errors="replace")
                output = f"{stdout}\n{stderr}".strip()

            log_path.write_text(
                "\n".join(
                    [
                        f"route={job['routeId']}",
                        f"mode={job['mode']}",
                        f"url={job['url']}",
                        f"attempt={attempt}",
                        f"returncode={returncode}",
                        f"timedOut={str(timed_out).lower()}",
                        "",
                        output,
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            attempt_rows.append(
                {
                    "attempt": attempt,
                    "returnCode": returncode,
                    "timedOut": timed_out,
                    "log": log_path.name,
                }
            )

            if not timed_out and returncode == 0 and report_path.is_file():
                try:
                    report = load_json(report_path)
                except (json.JSONDecodeError, OSError) as exc:
                    final_error = {"failureType": "malformed-report", "message": str(exc)}
                    continue

                actual_version = str(report.get("lighthouseVersion", ""))
                categories = report.get("categories", {})
                missing_categories = [
                    category
                    for category in CATEGORIES
                    if not isinstance(categories.get(category, {}).get("score"), (int, float))
                ]
                if actual_version != expected_version:
                    final_error = {
                        "failureType": "report-version-mismatch",
                        "message": f"Lighthouse {actual_version or 'unknown'} != pinned {expected_version}",
                    }
                    continue
                if missing_categories:
                    final_error = {
                        "failureType": "malformed-report",
                        "message": "Missing numeric category scores: " + ", ".join(missing_categories),
                    }
                    continue

                runs.append(
                    {
                        "routeId": job["routeId"],
                        "mode": job["mode"],
                        "url": job["url"],
                        "status": "pass",
                        "report": report_path.name,
                        "attempts": attempt_rows,
                        "lighthouseVersion": actual_version,
                    }
                )
                final_error = None
                break

            final_error = {
                "failureType": classify_failure(returncode, timed_out, report_path),
                "message": f"Lighthouse report production failed for {stem} on attempt {attempt}",
            }

        if final_error is not None:
            failure = {
                "routeId": job["routeId"],
                "mode": job["mode"],
                "url": job["url"],
                "status": "fail",
                "attempts": attempt_rows,
                **final_error,
            }
            runs.append(failure)
            failures.append(failure)

    produced_reports = sum(1 for row in runs if row.get("status") == "pass")
    summary = {
        "schemaVersion": "1.0.0",
        "status": "pass" if not failures and produced_reports == len(jobs) else "fail",
        "authority": "repository-software-qa",
        "expectedReports": len(jobs),
        "producedReports": produced_reports,
        "runs": runs,
        "failures": failures,
        "notes": [
            "This summary covers Lighthouse report production only, not score-budget enforcement.",
            "Transport/browser-launch failures are separated from genuine score regressions.",
        ],
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Produce AETHERIA Lighthouse reports with route-specific diagnostics")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--base-url", default=os.environ.get("AETHERIA_QA_BASE_URL", "http://127.0.0.1:4173"))
    parser.add_argument("--report-dir", type=Path, default=ROOT / "qa/artifacts/lighthouse")
    parser.add_argument("--summary", type=Path, default=ROOT / "qa/artifacts/lighthouse-production-summary.json")
    parser.add_argument("--chrome-path", type=Path, default=Path(os.environ.get("CHROME_PATH", "")))
    parser.add_argument("--lighthouse-cli", type=Path, default=DEFAULT_LIGHTHOUSE)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args()

    summary = run_audits(
        config_path=args.config.resolve(),
        base_url=args.base_url,
        report_dir=args.report_dir.resolve(),
        summary_path=args.summary.resolve(),
        chrome_path=args.chrome_path.expanduser().resolve(),
        lighthouse_cli=args.lighthouse_cli.resolve(),
        attempts=max(1, args.attempts),
        timeout_seconds=max(30, args.timeout_seconds),
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "pass" else 3


if __name__ == "__main__":
    raise SystemExit(main())
