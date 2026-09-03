# Decision summary

The research branch proposes five decisions:

1. AETHERIA owns a versioned canonical fixture schema.
2. Open Fixture Library is the primary architecture reference for fixture-data governance, not the AETHERIA source format.
3. Real photometric assets are first-class product data. Conceptual WebGL lighting must remain explicitly labeled as conceptual.
4. CAD, web, BIM and control outputs are generated through adapters from the canonical fixture model.
5. Direct integration prefers permissive dependencies; GPL projects remain external/reference tools by default.

The first engineering implementation should migrate VORTEX into the canonical schema and make the viewer consume generated fixture data. Interchange formats and control protocols come after that foundation is stable.