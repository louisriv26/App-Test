# Les 24 Heures de la Passion — v101.102

Build date: 2026-08-22  
Cache: `luisa-24h-v101-102`

## LDC methodology authority

The exact Version 31 / RA19D package supplies the latest shipped LDC presentation implementation. Its `speech_model.js` and `display_map.js` are byte-identical to Version 29 / RA19B. RA19B remains the governing corpus-flow authority; RA19D did not alter speaker geometry/display transforms/flow decisions.

## This stage

Baseline: **v101.101**, SHA-256 `77f7577b20dc4bb06ba403bc97074e0f9326f7c37d6ed68a0b756018b2da476e`.

This successor replaces v101.101's ad-hoc quote suppression and split Android topology with one build-time frozen LDC-style presentation projection. It:

1. preserves meaningful nested/reported/non-divine/formula quotations;
2. suppresses only validated redundant outer divine wrappers in the reader;
3. separates divine speaking turns from narration/other turns using deterministic presentation boundaries;
4. makes Samsung `Paragraphe` consume the same visible-boundary model as rendering;
5. explicitly presents the two user-confirmed French-attribution cases as Luisa without modifying canonical `SPEECH_DATA`.

Canonical devotional text, paragraph IDs/order, RA19B flow actions, highlights/notes storage and raw speaker metadata are preserved.

Static/package candidate only until physical-device/live/offline gates are completed.

## Release-evidence lifecycle (RE1)

This ZIP intentionally contains only evidence that exists before immutable package freeze. `FINAL_REOPEN_AUDIT.md`, `INDEPENDENT_REOPEN_AUDIT.md`, and `FINAL_DECISION_LOCK.json` are intentionally **not embedded**: they are generated afterward as external companion evidence against the exact frozen ZIP. This prevents a circular claim in which the package asserts that its own future reopen audit has already passed.
