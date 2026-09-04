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

from animation_reference import apply_nominal_rotation_reference
from environment_library import build_environment_library
from environment_variants import build_additional_environments
from lookdev_modes import apply_master_lookdev
from lookdev_refinements import apply_master_refinements

apply_master_lookdev()
apply_nominal_rotation_reference()
build_environment_library()
build_additional_environments()
# Run the final lookdev refinement layer last so environment builders cannot
# overwrite the authoritative visualization revision metadata.
apply_master_refinements()

# Preserve the complete finish-study and environment material libraries in the
# generated master, including variants intentionally hidden in the default view.
for material in bpy.data.materials:
    if material.name.startswith("MAT_"):
        material.use_fake_user = True

if bpy.data.filepath:
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
