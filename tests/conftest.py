from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def built_release():
    subprocess.run([sys.executable, str(ROOT / "scripts/build_release.py")], check=True)
    return ROOT / "build/vx4800/AETHERIA_VORTEX_v5.2.0.zip"


@pytest.fixture(scope="session")
def built_site():
    subprocess.run([sys.executable, str(ROOT / "scripts/build_site.py")], check=True)
    return ROOT / "_site"


@pytest.fixture(scope="session")
def built_web_geometry():
    subprocess.run([sys.executable, str(ROOT / "scripts/generate_web_geometry.py")], check=True)
    return ROOT / "build/vx4800/web/vx4800-coordination-v1.3.0.glb"
