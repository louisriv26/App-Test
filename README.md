# Luisa — 24 Heures de la Passion

Version: `v101.13`

Notes: heading style consistency fix — Hour 24's two major headings ("La sépulture de Jésus" and "La Désolation de la Vierge Marie") were rendered with a bespoke plain-text divider style used nowhere else in the app, instead of the gold boxed-callout style every other Hour uses for its scene headings. Both now render identically to the rest of the app. No text, speech-attribution, or reading-behaviour change. Carries all prior v101.x fixes (v101.2 through v101.12, including the v101.10 iPad Share/Add-to-Home-Screen crash fix and the v101.12 Hour 24 Plan-sheet fix). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `REAL_DEVICE_QA_CHECKLIST.md`.