# Luisa — 24 Heures de la Passion

Version: `v101.24`

Notes: search — added a "Réflexions" filter, positioned between "Heures" and "Prières", so you can search within Réflexions et pratiques text specifically instead of only "Tout" or "Heures" (which previously included reflections too). No corpus/speech change. Carries all prior v101.x fixes (v101.2 through v101.23, including the v101.23 search debounce, offline-cache bound, and keyboard/screen-reader focus fixes). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `luisa-24h-state_1.md`'s "Android Play Protect note" for detail.