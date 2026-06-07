# Real-device QA checklist — Stage 5B

This checklist is the short operational version. The full test matrix is REAL_DEVICE_QA_MATRIX.md.

## Required real-device coverage

- [ ] iPhone Safari portrait
- [ ] iPhone installed PWA portrait
- [ ] iPad Safari portrait
- [ ] iPad Safari landscape
- [ ] iPad installed PWA
- [ ] Desktop browser smoke test

## Must-pass flows

- [ ] App launches from live GitHub Pages URL
- [ ] Installed PWA launches
- [ ] Offline app shell works after first online load
- [ ] Hours 1, 5, 13, 21, and 24 open correctly
- [ ] Explicit resume works; ordinary Hour opening opens top
- [ ] Psalm 129 return navigation works
- [ ] Highlighting works on iPhone and iPad without control overlap
- [ ] Mon Espace opens/closes correctly on iPad/desktop
- [ ] Library/Textes large items open and scroll
- [ ] Search works and result cap messaging is clear
- [ ] Personal-data export/import works for safe data and rejects malformed data
- [ ] Skip link/focus/keyboard checks pass where applicable

Record detailed results in REAL_DEVICE_QA_RESULTS_TEMPLATE.csv.
