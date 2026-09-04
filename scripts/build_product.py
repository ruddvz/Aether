from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build/vx4800"


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True)


def build() -> Path:
    """Build repository product artifacts without creating an archive package.

    Outputs remain ordinary repository/build artifacts:
    - V5.2 presentation viewer HTML
    - coordination STEP/DXF geometry
    - source coordination GLB
    - derived Meshopt coordination GLB and provenance manifest

    Manufacturing authority is not changed by this build.
    """
    BUILD.mkdir(parents=True, exist_ok=True)
    run("build_viewer.py")
    run("generate_geometry.py")
    run("optimize_web_geometry.py")
    print(BUILD)
    return BUILD


if __name__ == "__main__":
    build()
