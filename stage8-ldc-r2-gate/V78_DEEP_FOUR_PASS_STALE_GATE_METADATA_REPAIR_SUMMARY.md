# LDC v2.19.78-R1B — Deep Four-Pass Stale-Gate Metadata Repair Summary

**Date:** 2026-09-09  
**Direct predecessor:** immutable `v2.19.77-R1B` / `69c1d171adae77aa2c7dc9a38df7f33fba95565da7834059fd7cd22dcee1cfda`  
**Trigger:** deep Pass 4 stale-current audit  
**Public deployment:** **NOT AUTHORIZED BY THIS PACKAGE**

## Corrective scope

The v77 package was functionally correct, but three current metadata fields (`physical_ipad_gate`, `physical_iphone_gate`, `physical_samsung_android_gate`) still contained obsolete predecessor-candidate wording. They did not assert PASS, but under a strict current-evidence audit their current-candidate designation was stale. v78 changes those fields to explicit external-open wording: v78 is not physically certified; v73 is retained only as the last carried candidate reference.

No canonical/devotional text, stable ID/order, speaker semantic authority, display/flow authority payload, SEARCH-V2 payload/ranking semantics, user-state schema/migration algorithm or renderer behavior is changed. `speech_model.js` remains `3bd067956a5275e0be7231add3b425c124fb17f3d0be548080eee10c649134f6`.

Exact final ZIP identity is certified only by the external post-freeze receipt.
