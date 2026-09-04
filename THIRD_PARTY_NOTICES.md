# Third-party notices

This repository currently relies on or is designed to interoperate with permissively licensed tooling including Three.js (MIT), CadQuery (Apache-2.0), ezdxf (MIT), trimesh (MIT), jsonschema (MIT), pandas (BSD-3-Clause), NumPy (BSD-3-Clause), Pillow (HPND), pytest (MIT), glTF-Transform CLI 4.5.0 (MIT), and three-mesh-bvh 0.9.14 (MIT).

IfcOpenShell 0.8.5 is used by the dedicated IFC coordination-export workflow and is distributed under the GNU Lesser General Public License v3 or later (LGPLv3+). It is a build/validation dependency for IFC generation and parsing. The generated IFC coordination file remains a derived project deliverable and does not become manufacturing or construction authority by virtue of using IfcOpenShell.

The V5.2 presentation viewer loads pinned Three.js 0.185.1 modules from jsDelivr at runtime. The VX4800 technical inspector additionally loads pinned three-mesh-bvh 0.9.14 and Three.js GLTFLoader/MeshoptDecoder modules from jsDelivr. A future offline release should vendor reviewed pinned modules and include their license text.

glTF-Transform CLI 4.5.0 is used only to create a derived Meshopt-compressed coordination GLB for browser review. The original coordination GLB remains the source asset for coordination QA, and neither file is manufacturing authority.

The Blender visualization workflow targets Blender 5.2.1 LTS downloaded from the official Blender Foundation distribution and verified against the official SHA-256 manifest before execution. Blender is GNU GPL software. Published Python scripts that use Blender's Python API under `blender/` carry a GPL-3.0-or-later SPDX header. Generated `.blend` artwork and rendered imagery remain visualization deliverables and do not become engineering/manufacturing authority.

See `docs/architecture/THIRD_PARTY_POLICY.md`, `docs/BLENDER_PIPELINE.md`, `docs/IFC_COORDINATION_EXPORT.md`, and `docs/research/OPEN_SOURCE_LIGHTING_LANDSCAPE.md` for the broader integration policy.
