# Product pipeline

```text
controlled engineering data
        +
fixture.json
        +
presentation / photometry study
        |
        +--> schema + invariant validation
        +--> STEP/DXF geometry QA
        +--> deterministic presentation data
        +--> generated HTML viewer
        +--> deterministic release ZIP + SHA256SUMS
        +--> generated product catalog + GitHub Pages
        +--> future IFC / GDTF / MVR / optimized glTF adapters
```

## Rules

1. Viewer HTML never defines manufacturing authority.
2. Presentation changes that alter size, position, pose, material, lighting or motion must declare whether they diverge from engineering.
3. Conceptual WebGL light intensity is never described as tested photometry.
4. Every controlled asset is hashed in the fixture manifest.
5. A release must be reproducible from the exact Git commit.
6. IFC, GDTF, MVR and other interchange formats are adapters from canonical data, not canonical data themselves.
