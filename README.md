# Luisa — 24 Heures de la Passion

Version: `v101.12`

Notes: Plan-sheet fix — Hour 24's Plan (≡) was missing "La Désolation de la Vierge Marie" entirely, showing only "La sépulture de Jésus". Root cause: the Plan sheet only read a metadata table that indexes standalone heading-paragraphs; the Désolation heading is a subsection title, rendered directly by the reader but never registered there. The reader itself already showed both headings correctly — this fix only completes the Plan-sheet listing, and generalizes to any future Hour with subsections. No corpus, speech-attribution, or reading-behaviour change. Carries all prior v101.x fixes (v101.2 through v101.11, including the v101.10 iPad Share/Add-to-Home-Screen crash fix, device-confirmed and live in production). Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `REAL_DEVICE_QA_CHECKLIST.md`.