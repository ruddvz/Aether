# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

runpy.run_path(str(HERE / "build_scene.py"), run_name="__main__")
