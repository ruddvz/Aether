# VX4800 butterfly material and attachment qualification

Date: 2026-09-04

Status: RFQ / prototype qualification input, not construction release.

This package establishes separate material and attachment-development paths for the ARC, LUX and ART commercial tiers. It does not approve a final butterfly material, thickness or attachment.

## Why this work comes before final suspension sizing

The current fixture definition correctly records actual product mass and center of gravity as unknown. The suspension shortlist therefore cannot be promoted from supplier research to final hardware until production-intent S, M and L butterflies and their complete lower attachment assemblies are physically weighed.

The current geometry parameters use nominal butterfly thicknesses of 5 mm for S, 6 mm for M and 7 mm for L. Those values remain RFQ/prototype design inputs. They are not automatically valid for every material tier and are not released finished-part thicknesses.

Likewise, the repository's lightweight coordination geometry must not be used to derive a final mass from its bounding box or simplified volume.

## Commercial tier architecture

### ARC - cast PMMA

Current reference candidate: PLEXIGLAS GS Clear or approved cast-PMMA equivalent.

Manufacturer technical information publishes typical density of 1.19 g/cm³, tensile strength of 80 MPa and short-term elastic modulus of 3300 MPa for PLEXIGLAS GS clear. Clear PLEXIGLAS products can reach up to 92 percent visible light transmission.

These are base-material reference values, not finished VX4800 part allowables.

Why ARC is useful:

- substantially lower density than the current glass references;
- mature casting, machining and forming routes;
- transparent, repeatable commercial material;
- suitable for rapid physical prototypes and a more cost-controlled product tier.

Primary attachment direction to prototype:

A mechanically captured three-point attachment using carefully machined features and compliant local hardware is the first ARC direction. The detail must address PMMA creep, local stress around holes/features, surface damage and fatigue. An edge/yoke capture remains an alternate where the geometry allows it.

ARC may not be released on generic PMMA values. Production-equivalent attachment testing remains mandatory.

References:

- https://www.plexiglas.de/en/products/plexiglas/plexiglas-gs-xt
- https://www.plexiglas.de/files/plexiglas-content/pdf/technische-informationen/211-1-PLEXIGLAS-GS-XT-EN.pdf
- https://www.plexiglas.de/en/service/product-info/light-transmission

## LUX - engineered premium glass

Current data-reference candidate: SCHOTT BOROFLOAT 33.

SCHOTT publishes the following reference properties for BOROFLOAT 33:

- density: 2.23 g/cm³ at 25 °C;
- Young's modulus: 64 kN/mm²;
- Poisson ratio: 0.2;
- refractive index nd: 1.47140;
- Abbe number: 65.41.

SCHOTT also publishes thickness ranges that include values relevant to the present RFQ studies.

Most importantly for the attachment design, SCHOTT explicitly states that impact resistance depends on how the glass is fitted, panel size and thickness, the presence of drill holes and their arrangement, among other factors. This is exactly why published base-glass strength cannot be used as proof of a finished three-hole butterfly.

Preferred first attachment direction:

Start with a mechanically captured edge clamp/cradle using a controlled compliant interface because it avoids immediately committing to holes in glass. A drilled three-point attachment may still be developed, but only with specialist control of hole geometry, edge distance, finishing and local bearing stresses, followed by proof and fatigue tests.

A bonded metal pad may be investigated for appearance, but it remains research-only. Adhesive creep, preparation, aging, thermal mismatch and hidden degradation make an adhesive-only primary overhead load path unacceptable without a dedicated durability program and independent retention.

References:

- https://www.schott.com/en-ca/products/borofloat-p1000314/technical-details
- https://media.schott.com/api/public/content/69b4abd8191246e3869c46c717f07b29?download=true&v=3b812f89

## LUX alternate - chemically strengthened aluminosilicate glass

Corning Gorilla Glass 3 is retained only as a research alternate demonstrating a thin chemically strengthened glass direction.

Its current product sheet publishes:

- standard thickness: 0.4 to 2.0 mm;
- density: 2.39 g/cm³;
- Young's modulus: 70 GPa;
- Poisson ratio: 0.22.

Its normal use is cover glass for electronic devices. That supply/process context is materially different from a sculptural suspended butterfly. No custom forming, strengthening, edge-finishing or attachment route has been qualified for VX4800.

Because its published standard thickness range does not map to the current 5/6/7 mm RFQ parameters, it must not silently replace BOROFLOAT or become the assumed LUX specification.

Reference:

- https://www.corning.com/microsites/csm/gorillaglass/PI_Sheets/2020/Gorilla_Glass_3_ProdSheet.pdf

## ART - artisan glass

The ART tier intentionally has no generic controlled density or strength value yet.

The selected artisan glassmaker must return:

- actual glass composition or controlled trade/process description;
- annealing process and acceptance;
- density or measured mass basis;
- achievable dimensional tolerance;
- optical/cosmetic variation standard;
- attachment-forming options;
- batch and spare reproducibility;
- proof-load and quality evidence.

Two attachment directions are worth developing with the glassmaker:

1. an integral formed loop/boss created during the glassmaking process and correctly annealed;
2. a mechanically captured cradle that avoids post-drilling the handcrafted form.

Neither is approved before samples exist.

## Attachment concept matrix

### Three-point drilled mechanical attachment

Potential tier fit: ARC first, LUX only with specialist glass engineering.

Advantages:

- positive mechanical load path;
- compact visual language;
- supports three-point orientation control.

Risks:

- stress concentration;
- edge-distance sensitivity;
- hole quality and finish sensitivity;
- local bearing/crushing;
- PMMA creep or cracking around the feature;
- glass fracture initiation.

Required controls include exact hole geometry, edge distance, finished edge quality, compliant sleeves/pads, preload control, proof load and fatigue testing.

### Edge clamp / cradle

Potential tier fit: LUX and ART.

Advantages:

- avoids drilled holes;
- can isolate brittle glass from cable terminals;
- replaceable.

Risks:

- local contact stress;
- slip;
- visual bulk;
- compliant-pad creep or aging;
- damage to polished edges.

The final design must control contact area, clamp force, pad material, anti-slip geometry and edge finish.

### Bonded metal pad

Potential tier fit: LUX research only.

Advantages:

- visually clean;
- can hide the transition to the three-point bridle.

Risks:

- adhesive creep;
- cure/process variability;
- surface-preparation sensitivity;
- aging and moisture;
- thermal-expansion mismatch;
- difficult visual inspection of degradation.

This route cannot become an unretained primary overhead load path on aesthetics alone.

### Integral artisan loop / boss

Potential tier fit: ART.

Advantages:

- can integrate the attachment into the sculpture;
- avoids drilling a finished handmade element;
- potentially clean visual result.

Risks:

- forming variation;
- annealing stress;
- local section variation;
- matched-spare reproducibility.

This must be developed and tested by the selected glassmaker.

## Physical mass control

The repository now defines a dedicated physical mass-record schema:

`schemas/aether-butterfly-mass-measurement.schema.json`

For every production-intent S, M and L sample that advances beyond research, separately measure:

1. butterfly only;
2. butterfly-local attachment hardware;
3. lower bridle/yoke and terminals;
4. complete suspended assembly below the main suspension cable.

Record the sample identity, exact material/batch, process revision, attachment revision, scale identity and resolution, calibration status, operator and evidence references.

The complete suspended-assembly mass is the important input to final suspension line design. A material-density calculation is useful for comparison, not a replacement for the controlled physical measurement.

## Production mass variation and kinetic balance

A kinetic field with 240 elements cannot be treated as 240 unrelated decorative pieces.

Once a material tier reaches production intent, establish a mass tolerance by size family and measure enough parts to understand production variation. The resulting distribution must feed rotating-carrier balance provisions and dynamic testing.

ART will likely require the strictest matching process because handmade geometry and glass mass can vary even when the visual family is intentionally consistent.

Do not define a numeric production mass tolerance until physical samples exist.

## Minimum sample qualification sequence

For each tier advanced beyond research:

1. manufacture representative S, M and L prototypes;
2. inspect geometry, thickness and edge/finish quality;
3. measure butterfly-only mass;
4. fit production-intent attachment hardware;
5. measure complete suspended assembly mass;
6. inspect hanging orientation and repeatability;
7. proof-load the complete attachment assembly;
8. inspect for permanent damage or slip;
9. cycle the attachment through the intended kinetic/fatigue program once that duty is controlled;
10. assess cosmetic/optical degradation;
11. establish replacement procedure;
12. freeze supplier process, inspection and traceability requirements only after successful testing.

## Relationship to Blender

The Blender visualization track may use physically plausible optical shaders and refined geometry to study appearance.

It may not approve:

- glass composition;
- PMMA grade;
- material thickness;
- attachment geometry;
- finished-part mass;
- attachment strength;
- fatigue life.

Any three-lead Blender yoke remains visualization-only until this engineering track freezes and validates a real lower attachment.

## Promotion gate

No material tier is a released VX4800 material/attachment system until all of these are closed:

- exact material grade/process selected;
- production-intent S/M/L samples manufactured;
- complete suspended-assembly masses controlled;
- attachment detail frozen;
- proof load passed;
- fatigue test passed;
- occupied-space failure/retention strategy resolved;
- optical/cosmetic acceptance standard frozen;
- production mass tolerance and spares/matching strategy frozen;
- supplier quality/traceability returns accepted.

## Explicit non-claims

This qualification does not claim:

- final material selection;
- final S/M/L thickness;
- final element mass;
- final center of gravity;
- final attachment strength;
- final suspension line load;
- occupied-space construction release;
- that BOROFLOAT 33, PLEXIGLAS GS or Gorilla Glass has been approved by its manufacturer for VX4800.
