# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import runpy
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

runpy.run_path(str(HERE / "build_scene.py"), run_name="__main__")

# Preserve the complete finish-study material library in the generated master,
# including variants that are intentionally not assigned in the default scene.
for material in bpy.data.materials:
    if material.name.startswith("MAT_"):
        material.use_fake_user = True

if bpy.data.filepath:
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
