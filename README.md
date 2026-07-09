# Luisa — 24 Heures de la Passion

Version: `v101.14`

Notes: Plan-sheet scroll fix — tapping "La Désolation de la Vierge Marie" in Hour 24's Plan sheet scrolled one section too far, landing on the first paragraph below the heading instead of the heading itself. Fixed by jumping to the heading block directly. "La sépulture de Jésus" was already correct and is unaffected. No text, speech-attribution, or corpus change. Carries all prior v101.x fixes (v101.2 through v101.13, including the v101.10 iPad Share/Add-to-Home-Screen crash fix, the v101.12 Hour 24 Plan-sheet fix, and the v101.13 heading style consistency fix). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `REAL_DEVICE_QA_CHECKLIST.md`.