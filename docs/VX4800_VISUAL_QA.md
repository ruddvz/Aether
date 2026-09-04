# VX4800 Blender visual QA

This document records visualization QA for the AETHERIA VORTEX VX4800-BF-01 Blender master. It is not engineering, manufacturing, measured-photometry or construction authority.

## Controlled baseline

All approved visualization revisions preserve the controlled engineering mapping:

- 240 butterfly instances;
- 66 S / 144 M / 30 L;
- 240 main suspension splines;
- 720 visual yoke/lead splines;
- 14 fixed LED-head positions;
- engineering revision 1.3.0;
- presentation revision 5.2.0.

## Early baseline findings

The first Blender-native Cycles baseline from workflow run `33891009803` was technically valid but visually weak. The fixture was washed out against an ivory stage, the canopy and lower tail were clipped, suspension dominated the image, the butterflies read as pale shards, optical transmission was unclear and the photographic-light hierarchy was flat.

Revisions 0.2 and 0.3 established the dark premium studio direction, contained the full fixture, suppressed conceptual fixture beams in clean product photography, removed the distracting stage horizon and replaced the first glitter-like radial facets with broader optical faces.

## Optical-detail review

Revision 0.4 introduced a macro camera aimed at controlled instance `VX-001` without moving the instance. That close view proved that the then-current material/body balance still read too dark and mirror-like, and that the sculptural centre was oversized relative to the wings.

Later lookdev reduced suspension prominence, introduced an isolated neutral macro context and improved wing shaping and lighting. Revision 0.11 reduced visualization-only volume absorption to 3.5 and reduced the sculptural centre while deliberately keeping thin-film/rainbow effects disabled because no controlled coating specification supports them.

## Architectural review

The architectural library was developed after the studio/product baseline became stable. The final library contains four visualization-only installed contexts:

1. double-height residential;
2. staircase void;
3. hospitality lobby;
4. gallery atrium.

The dark studio remains a product-photography context rather than a fifth architectural environment.

Architectural QA focused on keeping the fixture dominant, providing plausible scale, preserving a useful contrast field behind transparent butterflies, avoiding decorative competition and keeping every room object/light explicitly outside engineering authority.

The residential wide, staircase, hospitality, atrium and vertical-marketing compositions passed the final visual review. The residential-medium camera required one last framing correction because revision 0.12 clipped the canopy too tightly.

## Finish studies

The final render-time appearance studies are:

- dark champagne;
- black titanium;
- brushed brass;
- satin nickel.

All four are visually distinguishable in the canopy/detail review. They are presentation overrides only and do not approve PVD chemistry, substrate, brushing process, colour tolerance, durability or supplier.

## Final revision 0.13.0 review

Final source commit `700949ac60e81ebd5742911841a9db0a3590e594` was exercised by Blender workflow run `33918998474` and ordinary repository validation run `33918998481`.

The Blender run completed successfully with:

- Blender 5.2.1 LTS master generation;
- Blender-native scene validation;
- repeated master-refinement idempotence checks;
- sequential finish-switch checks in one Blender session;
- all 12 targeted parallel Cycles QA renders;
- combined validation/render artifact generation.

The ordinary repository run also completed successfully, covering canonical product data, Blender source policy, engineering geometry, optimized web geometry, regression tests, product artifacts, Pages assembly and public entry points.

Final visual findings:

- product hero: approved as the clean dark-studio baseline;
- full elevation: approved with full fixture contained;
- butterfly macro: approved after recentering and tightening; transparent/faceted optical response is legible without unsupported fantasy dispersion;
- residential wide: approved;
- residential medium: approved after the 0.13 camera correction restored ceiling/canopy breathing room;
- vertical marketing: approved;
- staircase void: approved;
- hospitality lobby: approved;
- gallery atrium: approved;
- black titanium, brushed brass and satin nickel comparison renders: approved as distinct visualization studies.

The final Blender visualization baseline is therefore accepted for repository integration. This acceptance does not qualify the physical butterfly material, attachment, suspension hardware, kinetic system, photometric supplier data, structural interface or certification evidence.

## Rendering basis

Cycles remains the production renderer. The optical material uses transmission, IOR-based dielectric response, low micro-roughness and restrained visualization-only edge absorption. Refractive/caustic behaviour is treated as rendering lookdev, not measured fixture output. Exact supplier IES/LDT and physical optical qualification remain separate upstream evidence domains.
