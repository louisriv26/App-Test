# Luisa — 24 Heures de la Passion

Version: `v101.20`

Notes: home-screen fix — completing meditation for Hours 5, 6, or 7 (the Gethsemani hours) always placed the checkmark correctly, but the card's outer border never changed colour to show completion the way every other hour's does. Fixed: the completed border is now thicker and a deeper purple, keeping the Gethsemani identity while clearly showing it's done. No corpus/speech change. Carries all prior v101.x fixes (v101.2 through v101.19). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `luisa-24h-state_1.md`'s "Android Play Protect note" for detail.