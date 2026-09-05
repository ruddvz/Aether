# Product pipeline

```text
controlled engineering data
        +
fixture.json
        +
presentation / photometry study
        +
project + collection registry
        |
        +--> schema + invariant validation
        +--> project/fixture identity + collection cross-check
        +--> STEP/DXF geometry QA
        +--> source + optimized coordination GLB
        +--> deterministic presentation data
        +--> generated HTML viewer
        +--> IFC coordination adapter + loss report
        +--> GDTF / MVR loss reports while blocked
        +--> generated collection + product catalog + GitHub Pages
        +--> browser-local JSON-Schema fixture proposal editor
```

## Rules

1. Viewer HTML never defines manufacturing authority.
2. Presentation changes that alter size, position, pose, material, lighting or motion must declare whether they diverge from engineering.
3. Conceptual WebGL light intensity is never described as tested photometry.
4. Every controlled asset is hashed in the fixture manifest.
5. A release must be reproducible from the exact Git commit and applicable physical evidence.
6. IFC, GDTF, MVR and other interchange formats are adapters from canonical data, not canonical data themselves.
7. The fixture editor creates local proposals only. Schema validity and a proposal SHA-256 do not approve a product change or write it to the repository.
8. A browser-side schema validator must fail closed when the published schema introduces unsupported validation semantics.
9. GDTF and MVR remain blocked until the exact controlled head/control/aiming dependencies identified by the interchange loss policy are released.
10. Collection membership comes from canonical fixture `identity.collection`; `project.json` registers allowed collection identities and presentation metadata but does not duplicate product membership.
11. Empty planned collections remain empty. The catalog must not invent products, SKUs or release claims to populate them.
12. A collection becomes active only when at least one registered canonical fixture belongs to it; repository validation enforces this state relationship.
