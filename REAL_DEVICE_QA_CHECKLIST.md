# Real-device QA checklist — v101.54 / 24H-A

Target candidate HTML SHA-256: `c6ba8f15c052ac86b5227ac0a4a22e21200ec926d24b86c861a2f7dc61cccbb2`

Status at package creation: **NOT TESTED — PHYSICAL DEVICE GATE PENDING**.

This checklist certifies only the 24H-A display-settings changes. Historical v101.53 device evidence does not certify this candidate.

## Release-critical affected-device smoke

Test on **real iPhone Safari / installed PWA** and **real iPad Safari / installed PWA** (iPad portrait and landscape):

1. Open Taille du texte and confirm the visible choices are exactly **Petit 16 px · Normal 19 px · Grand 22 px · Très grand 26 px**.
2. Confirm the live preview changes immediately and matches the reader size/rhythm.
3. On a fresh profile, confirm **Normal 19 px** is selected by default.
4. Select each size in turn; confirm the reader changes but header, bottom navigation and tool chrome do not grow with the reader text.
5. At **Très grand 26 px**, read/scroll a long Hour and confirm there is no clipped text, horizontal page scroll, inaccessible bottom navigation or blocked end-of-view content.
6. On iPad, repeat 26 px in portrait and landscape.
7. Where native text selection permits, select text, change size, and confirm the same passage remains selected/visible; if Safari clears the native selection, record that exact device behavior rather than marking PASS by assumption.
8. Confirm existing Note / Surligner / Copier behavior still works after changing size.
9. Confirm **Automatique · Clair · Sombre**. In Automatique, change the OS appearance and confirm the app follows it; in Clair/Sombre, the app must not follow the OS change.
10. Reload the app and confirm the chosen text size and theme persist.
11. Confirm no iOS focus auto-zoom is introduced in editable fields (note textarea/search remain at least 16 CSS px).
12. For installed PWA, close/reopen and confirm the same settings persist and the app starts normally.

## Optional Android/Samsung smoke for this stage

Confirm all four reader sizes, preview, fixed chrome size, theme persistence and existing Samsung whole-paragraph highlighting still work. This is regression evidence, not a replacement for the iPhone/iPad release-critical gate above.

Record device, OS, browser/install mode, candidate SHA, test result, evidence and defect reference in `REAL_DEVICE_QA_RESULTS_TEMPLATE.csv`.
