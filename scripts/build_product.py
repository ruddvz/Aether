from pathlib import Path
import json
import subprocess
import sys

from build_interchange_loss_report import DEFAULT_FIXTURE, DEFAULT_PROFILE, TARGETS, build_report

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build/vx4800"


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True)


def build_interchange_reports() -> Path:
    """Emit review-only interchange loss reports for every planned target.

    Report generation is not the same as export eligibility. Blocked GDTF/MVR
    reports are expected artifacts and retain their blocking-loss status.
    """
    output_dir = BUILD / "interchange"
    output_dir.mkdir(parents=True, exist_ok=True)
    for target in TARGETS:
        report = build_report(DEFAULT_FIXTURE, DEFAULT_PROFILE, target)
        output = output_dir / f"{target}-loss-report.json"
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return output_dir


def build() -> Path:
    """Build repository product artifacts without creating an archive package.

    Outputs remain ordinary repository/build artifacts:
    - V5.2 presentation viewer HTML
    - coordination STEP/DXF geometry
    - source coordination GLB
    - derived Meshopt coordination GLB and provenance manifest
    - IFC/GDTF/MVR interchange loss reports

    Manufacturing authority is not changed by this build. GDTF/MVR loss
    reports may remain explicitly blocked while still being generated.
    """
    BUILD.mkdir(parents=True, exist_ok=True)
    run("build_viewer.py")
    run("generate_geometry.py")
    run("optimize_web_geometry.py")
    build_interchange_reports()
    print(BUILD)
    return BUILD


if __name__ == "__main__":
    build()
