# Luisa — 24 Heures de la Passion

Version: `v101.23`

Notes: three backlog fixes from the full app audit — (1) search now waits briefly (140ms) after you stop typing before scanning, instead of re-scanning the whole app on every keystroke; (2) the offline cache no longer grows without limit — it keeps the 40 most recent files and drops the oldest automatically; (3) moving between screens (Accueil, Heures, Approfondir, Mon Espace, and opening an Hour) now correctly hands focus to the new screen for anyone navigating by keyboard or screen reader, instead of silently losing it. No corpus/speech change. Carries all prior v101.x fixes (v101.2 through v101.22). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `luisa-24h-state_1.md`'s "Android Play Protect note" for detail.