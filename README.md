# Luisa — 24 Heures de la Passion

Version: `v101.11`

Notes: UI cleanup — removed the paragraph-count badges next to the "Méditation" and "Réflexions et pratiques" tab labels in the reader (e.g. "Méditation (26)"). These were implementation detail with no value to someone deciding what to read; the tabs now show clean labels only. Reflections tabs with zero entries were already hidden entirely (unchanged). No corpus, speech-attribution, or reading-behaviour change. Carries all prior v101.x fixes (v101.2 through v101.10, including the v101.10 iPad Share/Add-to-Home-Screen crash fix, device-confirmed and live in production). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `REAL_DEVICE_QA_CHECKLIST.md`.