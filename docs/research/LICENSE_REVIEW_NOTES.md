# License review notes

This is an engineering planning note, not legal advice.

## Low-friction candidates

The first integration wave should prefer permissive licenses:

- MIT: Open Fixture Library, Three.js, IESNA, glTF-Transform, three-mesh-bvh, trimesh, ezdxf, pyGDTF, pyMVR.
- Apache-2.0: CadQuery, Manifold, build123d, QLC+.
- BSD-3-Clause: Colour.

## Isolation/review candidates

- IfcOpenShell: core libraries and applications use different LGPL/GPL licensing across the project. Keep IFC generation in offline tooling and review the exact packages used.
- web-ifc: MPL-2.0. Treat as optional browser BIM module.
- OLA: licensing differs between client libraries and daemon/plugins. Prefer an external service boundary if adopted.
- libMVRgdtf: custom MVR SDK license. Prefer MIT pyGDTF/pyMVR unless the official C++ SDK becomes necessary.

## External-tool-only by default

- BlenderDMX: GPL-3.0.
- GitBuilding: GPL-3.0.

AETHERIA can execute, test against, study and interoperate with these tools without copying their implementation into the core viewer.

## Data-format note

Implementing a public specification is different from copying a library implementation. GDTF, MVR, IFC and IES support should be implemented through appropriately licensed adapters/libraries and verified against the specifications and reference tools.