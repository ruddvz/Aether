# Decision summary

The research branch established five decisions:

1. AETHERIA owns a versioned canonical fixture schema.
2. Open Fixture Library is the primary architecture reference for fixture-data governance, not the AETHERIA source format.
3. Real photometric assets are first-class product data. Conceptual WebGL lighting must remain explicitly labeled as conceptual.
4. CAD, web, BIM and control outputs are generated through adapters from the canonical fixture model.
5. Direct integration prefers permissive dependencies; GPL projects remain external/reference tools by default.

Implementation update: the original first engineering step is complete. VORTEX now uses the canonical fixture schema and the repository generates downstream product data from controlled sources. IFC coordination export also exists. GDTF/MVR and other interchange work remain separate follow-on capabilities, and conceptual browser illumination still cannot be treated as controlled photometric evidence.
