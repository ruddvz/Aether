from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures/vx4800"
BUILD = ROOT / "build/vx4800"
AUTH_PATH = ROOT / "releases/vx4800/5.2.0/authority.json"
BUILD.mkdir(parents=True, exist_ok=True)

FINAL_NAME = "AETHERIA_VORTEX_v5.2.0.zip"
FINAL_OUT = BUILD / FINAL_NAME
CANDIDATE_OUT = BUILD / "AETHERIA_VORTEX_v5.2.0.rebuilt.zip"
STAMP = (2026, 9, 3, 0, 0, 0)

README = """# AETHERIA VORTEX

Product: VX4800-BF-01
Engineering revision: 1.3.0
Presentation revision: 5.2.0

The engineering schedule is controlled v1.3.0 data. Manufacturing STEP/DXF hashes are preserved in geometry-manifest-v1.3.0.json; repository-generated CAD in this ZIP is coordination authority only. V5.2 presentation size allocation, poses, lighting and motion are presentation studies only.

The HTML is a single product file but requires internet access for pinned Three.js modules from jsDelivr.

Lighting remains conceptual until controlled supplier/test IES data exists. This package is not a construction release.
"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def authority() -> dict:
    return json.loads(AUTH_PATH.read_text())


def generate_current_sources() -> list[tuple[str, Path]]:
    subprocess.run([sys.executable, str(ROOT / "scripts/build_viewer.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/generate_geometry.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/generate_web_geometry.py")], check=True)

    viewer = BUILD / "VX4800_VORTEX_Viewer_v5.2.0.html"
    return [
        ("viewer/index.html", viewer),
        ("product/fixture.json", FIX / "fixture.json"),
        ("product/engineering-v1.3.0.csv", FIX / "composition/engineering-v1.3.0.csv"),
        ("product/presentation-study-v5.2.0.json", FIX / "presentation/v5.2.0/study.json"),
        ("product/photometry-concept-v5.2.0.json", FIX / "photometry/concept-v5.2.0.json"),
        ("engineering/geometry-manifest-v1.3.0.json", FIX / "geometry/manifest.json"),
        ("coordination/canopy-coordination-v1.3.0.step", BUILD / "geometry/canopy-coordination-v1.3.0.step"),
        ("coordination/rotating-carrier-coordination-v1.3.0.step", BUILD / "geometry/rotating-carrier-coordination-v1.3.0.step"),
        ("coordination/butterfly-s-coordination-v1.3.0.step", BUILD / "geometry/butterfly-s-coordination-v1.3.0.step"),
        ("coordination/butterfly-m-coordination-v1.3.0.step", BUILD / "geometry/butterfly-m-coordination-v1.3.0.step"),
        ("coordination/butterfly-l-coordination-v1.3.0.step", BUILD / "geometry/butterfly-l-coordination-v1.3.0.step"),
        ("coordination/setout-coordination-v1.3.0.dxf", BUILD / "geometry/setout-coordination-v1.3.0.dxf"),
        ("coordination/vx4800-coordination-v1.3.0.glb", BUILD / "web/vx4800-coordination-v1.3.0.glb"),
        ("coordination/web-geometry-manifest.json", BUILD / "web/manifest.json"),
    ]


def historical_member_bytes(archive_name: str, source_path: Path) -> bytes:
    data = source_path.read_bytes()
    if archive_name == "product/fixture.json":
        # The recovered repository compacted this JSON after V5.2 was released.
        # The historical release used the same parsed object serialized with
        # two-space indentation and one trailing newline. Reproduce that exact
        # serialization without making formatting part of live product authority.
        data = (json.dumps(json.loads(data), indent=2) + "\n").encode("utf-8")
    return data


def write_member(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, STAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, data)


def build_candidate() -> Path:
    sources = generate_current_sources()
    hashes: list[str] = []
    with zipfile.ZipFile(CANDIDATE_OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=7) as zf:
        write_member(zf, "README.md", README.encode("utf-8"))
        for archive_name, source_path in sources:
            data = historical_member_bytes(archive_name, source_path)
            hashes.append(f"{sha256_bytes(data)}  {archive_name}")
            write_member(zf, archive_name, data)
        write_member(zf, "SHA256SUMS.txt", ("\n".join(hashes) + "\n").encode("utf-8"))
    return CANDIDATE_OUT


def verify_member_bytes(zip_path: Path, auth: dict, label: str) -> None:
    errors: list[str] = []
    expected_order = auth["memberOrder"]
    expected_members = auth["members"]
    with zipfile.ZipFile(zip_path) as zf:
        actual_order = zf.namelist()
        if actual_order != expected_order:
            errors.append(f"{label}: ZIP member order differs from authority")
        for name in expected_order:
            if name not in actual_order:
                errors.append(f"{label}: missing member {name}")
                continue
            data = zf.read(name)
            expected = expected_members[name]
            if len(data) != expected["byteLength"]:
                errors.append(f"{label}: {name} byte length {len(data)} != {expected['byteLength']}")
            digest = sha256_bytes(data)
            if digest != expected["sha256"]:
                errors.append(f"{label}: {name} sha256 {digest} != {expected['sha256']}")
    if errors:
        print("V5.2 RELEASE MEMBER VERIFICATION FAILED")
        for error in errors:
            print("-", error)
        raise SystemExit(1)


def build() -> Path:
    auth = authority()
    candidate = build_candidate()
    verify_member_bytes(candidate, auth, "rebuilt candidate")

    expected_sha = auth["release"]["sha256"]
    candidate_sha = sha256(candidate)
    if candidate_sha != expected_sha:
        raise SystemExit(
            f"Rebuilt V5.2 archive sha256 {candidate_sha} != immutable authority {expected_sha}"
        )

    shutil.copyfile(candidate, FINAL_OUT)
    if FINAL_OUT.stat().st_size != auth["release"]["byteLength"]:
        raise SystemExit("Final V5.2 release byte length differs from immutable authority")
    verify_member_bytes(FINAL_OUT, auth, "final release")

    print(candidate)
    print(f"rebuilt candidate sha256: {candidate_sha}")
    print(FINAL_OUT)
    print(f"immutable release sha256: {sha256(FINAL_OUT)}")
    return FINAL_OUT


if __name__ == "__main__":
    build()
