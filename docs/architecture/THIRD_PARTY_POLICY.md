# Third-party dependency and license policy

Status: proposed
Date: 2026-09-03

## Purpose

AETHERIA will use open-source software, standards and reference implementations, but the repository must retain clear ownership of its product data and avoid accidental license contamination.

## Rules

### 1. Prefer permissive dependencies

Default preference:

1. MIT
2. BSD-2-Clause / BSD-3-Clause
3. Apache-2.0

These can normally be used in commercial tooling when attribution/license obligations are preserved.

### 2. Review weak-copyleft libraries before integration

MPL and LGPL dependencies require a specific review of how they are linked, modified and distributed.

Use them behind a clean adapter or as an offline tool when possible.

Examples:

- web-ifc: MPL-2.0.
- IfcOpenShell libraries: LGPL-3.0-or-later, with some GPL components in the wider repository.
- OLA: client-facing libraries use LGPL while daemon/plugin code can be GPL.

### 3. GPL/AGPL is external-tool only by default

Do not copy GPL/AGPL implementation code into AETHERIA's viewer or core libraries unless the intended distribution/license model is deliberately changed and reviewed.

Study and interoperate with these projects instead.

Examples:

- BlenderDMX: GPL-3.0.
- GitBuilding: GPL-3.0.
- some IfcOpenShell ecosystem applications: GPL.

### 4. Standards are not code libraries

GDTF and MVR are industry standards. Implement their defined format through clean adapters.

Prefer permissively licensed parser/writer libraries such as pyGDTF and pyMVR where possible.

The C++ libMVRgdtf SDK uses a custom MVR SDK license with additional requirements. Do not adopt it automatically simply because it is an official reference implementation.

### 5. Do not fork a third-party internal schema as AETHERIA's source of truth

Open Fixture Library's own documentation warns consumers not to depend directly on its internal fixture JSON because the format may have breaking changes.

AETHERIA will own `aether-fixture.schema.json` and create explicit import/export adapters.

### 6. Preserve notices

When source code or substantial portions of permissively licensed code are reused:

- preserve the original license text.
- preserve required copyright notices.
- record upstream repository and version/commit.
- describe local modifications.
- add the dependency to the third-party manifest.

### 7. Pin dependencies

Production builds must pin versions or lock files. Do not rely on `latest` CDN URLs for released viewers.

For browser release artifacts, third-party version identifiers must be reproducible.

### 8. Do not vendor code without a reason

Use package dependencies where practical. Vendor only when:

- offline/single-file releases require it.
- upstream distribution does not fit the deployment model.
- a security/reproducibility requirement demands it.

Vendored code must retain its license header and source reference.

### 9. Fixture/product data is separate from third-party code

AETHERIA product definitions, original geometry, schedules, material specifications, images and manufacturing documentation are project assets. Their licensing does not automatically inherit the license of a tool used to generate or view them unless the tool's license explicitly says otherwise.

### 10. Every new dependency gets a review entry

Before merging a new dependency, record:

- repository/package.
- version or commit.
- purpose.
- license.
- runtime/build/dev scope.
- whether code is linked, executed externally, or studied only.
- attribution requirement.
- known security/maintenance concerns.

## Initial approved candidates

### Direct/core candidates

| Dependency | License | Proposed use |
| --- | --- | --- |
| three.js | MIT | Browser rendering |
| iesna | MIT | IES LM-63 parsing/sampling |
| three-mesh-bvh | MIT | Browser spatial queries |
| glTF-Transform | MIT | glTF optimization pipeline |
| CadQuery | Apache-2.0 | Parametric manufacturing CAD |
| trimesh | MIT | Mesh QA |
| Manifold | Apache-2.0 | Robust mesh geometry operations |
| ezdxf | MIT | DXF generation/validation |
| Colour | BSD-3-Clause | Spectral/color quality analysis |
| pyGDTF | MIT | GDTF adapter |
| pyMVR | MIT | MVR adapter |

### Adapter/external-tool candidates requiring isolation/review

| Dependency/tool | License | Proposed use |
| --- | --- | --- |
| IfcOpenShell | LGPL/GPL components | Offline IFC adapter |
| web-ifc | MPL-2.0 | Optional browser IFC |
| OLA | LGPL/GPL split | External control gateway |
| BlenderDMX | GPL-3.0 | External validation/previsualization |
| GitBuilding | GPL-3.0 | External assembly documentation generator |
| libMVRgdtf | custom MVR SDK | Reference only unless specifically approved |

## Release requirement

Before the first commercial software release, add a generated `THIRD_PARTY_NOTICES` artifact containing every distributed third-party component and the relevant license/notice text.