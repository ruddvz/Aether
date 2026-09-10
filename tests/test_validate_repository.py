from pathlib import Path
import runpy
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate_repository.py"
FIXTURE = ROOT / "fixtures/vx4800/fixture.json"
VIEWER_TEMPLATE = ROOT / "fixtures/vx4800/presentation/v5.2.0/viewer.template.html"


def test_validate_repository_current_tree_passes():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "VALIDATION PASSED" in result.stdout


@pytest.mark.parametrize(
    ("target", "corrupt", "expected_error"),
    [
        (
            FIXTURE,
            lambda text: text.replace('"designRevision": "1.3.0"', '"designRevision": "9.9.9"', 1),
            "design revision mismatch",
        ),
        (
            VIEWER_TEMPLATE,
            lambda text: text.replace("__VIEWER_DATA__", "VIEWER_DATA_REMOVED", 1),
            "viewer data placeholder missing",
        ),
    ],
)
def test_validate_repository_fails_closed_on_corrupted_inputs(
    monkeypatch, capsys, target, corrupt, expected_error
):
    original_read_text = Path.read_text
    target = target.resolve()

    def corrupted_read_text(self, *args, **kwargs):
        text = original_read_text(self, *args, **kwargs)
        if self.resolve() == target:
            return corrupt(text)
        return text

    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    monkeypatch.setattr(Path, "read_text", corrupted_read_text)

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(SCRIPT), run_name="__main__")

    assert exc_info.value.code == 1
    output = capsys.readouterr().out
    assert "VALIDATION FAILED" in output
    assert expected_error in output
