# Luisa — 24 Heures de la Passion

Version: `v101.22`

Notes: search fix — typing a search term without accents (e.g. "eglise") already found matching paragraphs containing the accented word ("église"), but nothing was visibly highlighted in the result. Fixed so the match is now always highlighted correctly, regardless of accents, capitalization, or "œ/æ" ligatures in either the search term or the corpus text. No corpus/speech change. Carries all prior v101.x fixes (v101.2 through v101.21). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `luisa-24h-state_1.md`'s "Android Play Protect note" for detail.