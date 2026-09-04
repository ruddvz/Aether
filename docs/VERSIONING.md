# Versioning

AETHERIA separates three version domains.

## Design revision

Controls manufacturing/engineering intent. Example: `1.3.0`.

- patch: correction that does not change intended interfaces or geometry
- minor: compatible design/feature change
- major: breaking physical/interface architecture change

## Presentation revision

Controls viewer/UI/visualization. Example: `5.2.0`. A presentation revision can diverge visually from engineering only when the divergence is explicit and marked non-manufacturing.

## Schema version

Controls the AETHERIA data contract independently of any fixture.

Never infer a design revision from a viewer revision.
