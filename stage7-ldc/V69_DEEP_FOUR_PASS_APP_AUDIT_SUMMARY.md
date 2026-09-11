# Livre du Ciel — v2.19.69-R1B / Public 69 — deep four-pass audit repair successor

Exact predecessor: certified v2.19.68-R1B SHA-256 `58e7eebd7c3a04db53e7a21ea144842aebd36c8e3dd8815f37c8e2f6edc3618d`.

Governing semantic authority: `d1a7450adf36368cc8609e21ccde3c51e0b3c90dc4f3c3305534cb40104d56f4` — unchanged.

Two defect families were proven by the independent deep audit and repaired:

1. user-visible onboarding paragraph count corrected to `74 346 paragraphes`, matching the actual backbone paragraph/search population; the stale predecessor value is not retained as an active current count;
2. supplement-speaker metadata reconciled to the 141 actual segments: SUP-T1 50 · SUP-T2 63 · SUP-T3 3 · SUP-T4 22 · SUP-T5 3.

No canonical/devotional text, paragraph identity/order, search semantics, speaker-segment content/offsets, display/flow semantics, supplement content, user-data schema or migration algorithm changed. Internal source mode `aflp` and technical `G036-AFLP-*` lineage remain unchanged.

Public deployment is not authorized by this package. External live/PWA/device/offline/accessibility gates remain separate.
