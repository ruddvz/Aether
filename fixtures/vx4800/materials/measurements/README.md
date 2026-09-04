# VX4800 physical mass measurement records

This directory is reserved for measured production-intent butterfly suspended-assembly mass records.

Do not add estimated masses here.

Each record must validate against:

`schemas/aether-butterfly-mass-measurement.schema.json`

## Measurement boundary

For each S, M and L sample, record four masses separately:

1. butterfly only;
2. butterfly-local attachment hardware;
3. lower bridle/yoke and terminals;
4. complete suspended assembly below the main suspension cable.

The fourth value is the primary physical input for line-load calculations. Do not substitute a CAD bounding-box estimate.

## Minimum provenance

Each record must identify:

- sample ID;
- tier: ARC, LUX or ART;
- size family: S, M or L;
- exact material supplier and grade/composition;
- material batch/lot;
- manufacturing process revision;
- attachment revision where fitted;
- scale ID;
- scale resolution;
- scale calibration status;
- measurement date/time;
- operator;
- at least one photo or controlled measurement-record reference.

## Center of gravity

Center-of-gravity measurement is optional at early prototype stage but becomes required where the attachment or asymmetrical sculptural form materially changes hanging orientation or kinetic balance.

When recorded, state the measurement method, datum/reference and XYZ offset in millimetres.

## Status progression

`prototype-measurement`

Use for early samples that are informative but not production-intent.

`production-intent-measurement`

Use only when material, process and attachment are representative of intended production.

`controlled`

Use only after engineering review accepts the sample, measurement method and evidence as an input to suspension/kinetic calculations.

A controlled record does not by itself release the cable, gripper, rotating carrier or product for construction.
