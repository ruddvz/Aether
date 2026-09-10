# Decision summary

Historical research decisions, with implementation status updated on 2026-09-10.

The research branch proposed five decisions:

1. AETHERIA owns a versioned canonical fixture schema.
2. Open Fixture Library is the primary architecture reference for fixture-data governance, not the AETHERIA source format.
3. Real photometric assets are first-class product data. Conceptual WebGL lighting must remain explicitly labelled as conceptual.
4. CAD, web, BIM and control outputs are generated through adapters from the canonical fixture model.
5. Direct integration prefers permissive dependencies; GPL projects remain external/reference tools by default.

The original first implementation step, migrating VORTEX into the canonical schema and generating viewer data from controlled fixture sources, is complete. The repository now also includes a derived IFC coordination adapter with explicit authority boundaries.

Remaining interchange work must build on that canonical foundation. GDTF/MVR output stays blocked where controlled head, control or aiming inputs are unresolved, and real product photometry remains evidence-gated rather than inferred from presentation lighting.

Use `ROADMAP.md` and the current open issues for the live implementation sequence. This file records the research decision lineage rather than the active backlog.
