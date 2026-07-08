# Luisa — 24 Heures de la Passion

Version: `v101.9`

Notes: robustness fix — background convenience features (remembering scroll position, checking for app updates) that fire exactly when iOS's Share/Add-to-Home-Screen triggers a visibilitychange/pageshow event are now wrapped so a failure inside them can never crash the whole app. This responds to a reported iPad Safari crash that showed the browser's own sanitized "Script error." with no further detail obtainable — a known WebKit behaviour in that context, not something fixable by improving our own error display. No corpus, speech-attribution, or reading-behaviour change. Carries all prior v101.x fixes (v101.2 through v101.8). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `REAL_DEVICE_QA_CHECKLIST.md`.