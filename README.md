# Luisa — 24 Heures de la Passion

Version: `v101.25`

Notes: Help content update — the "Aide et À propos" search section previously only described the "Paroles directes" speaker filter and never mentioned the basic filter row at all. It now lists the full filter set (Tout · Heures · Réflexions · Prières · Compléments · Paroles directes) before the existing detail. No corpus/speech/behaviour change. Carries all prior v101.x fixes (v101.2 through v101.24, including the v101.24 Reflexions search filter and the v101.23 search debounce/offline-cache bound/keyboard-screen-reader focus fixes). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `luisa-24h-state_1.md`'s "Android Play Protect note" for detail.