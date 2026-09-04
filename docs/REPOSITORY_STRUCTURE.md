# Repository structure

AETHERIA uses one canonical product model and generated outputs.

```text
Aether/
├── schemas/                     # versioned data contracts
├── fixtures/
│   └── vx4800/
│       ├── fixture.json         # canonical product manifest
│       ├── composition/         # controlled suspension/element schedule
│       ├── geometry/            # controlled STEP/DXF assets
│       ├── photometry/          # measured/supplier/conceptual optical data
│       ├── presentation/        # presentation studies and viewer templates
│       └── documents/
├── scripts/                     # validation and deterministic builders
├── tests/                       # regression protection
├── site/static/                 # minimal public shell assets
├── docs/                        # architecture and process
└── project.json                 # product registry
```

`build/` and `_site/` are generated and are never source of truth.

The previous bootstrap `products/<slug>/viewer/...` structure has been retired. Public product paths are generated from `project.json` and `fixtures/`.
