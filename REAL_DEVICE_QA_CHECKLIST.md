# 24H-G repair / v101.62 — physical device, installed-PWA and live-origin checklist

Use the exact v101.62 candidate bytes. Record PASS/FAIL/NOT_TESTED for every row.


## Owner-reported reader-continuity regression — release-critical retest
- On iPhone, open an Hour and scroll to a clearly identifiable paragraph around the middle of the meditation.
- Tap **Mon Espace**, then **Retour**.
- PASS only if the same reader tab and the same paragraph/reading position are restored (not the beginning of the Hour).
- Confirm the thin reading-progress strip at the top is visible immediately after Retour and reflects approximately the restored position.
- Scroll further and confirm the strip continues to update normally.

## iPhone Safari / installed PWA
- 16 / 19 / 22 / 26 px reader sizes; no clipping.
- Automatique / Clair / Sombre.
- Exact selected-text Surligner, Copier, Lien and Note.
- Existing-highlight colour picker remains fully on-screen.
- Note textarea does not trigger focus zoom; keyboard dismissal is usable.
- Repères OFF/ON preserves passage and actions.
- Portrait ↔ landscape rotation preserves a usable reader.
- With a non-empty unsaved Note open, an available-update Actualiser action must NOT reload; the draft must remain and receive focus.
- Existing installed build → v101.62 update preserves personal data.
- Offline reopen after one successful online load works.
- A copied deep link opens the expected Hour/paragraph.

## iPad Safari portrait / landscape
- Reader width, bottom navigation, exact selection and long-scroll remain usable.
- Repères, 26 px, Mon Espace, rotation/split-view.
- Installed-PWA update and offline reopen.

## Samsung / Android Chrome
- Paragraphe mode only; no expectation of native word selection.
- Whole-paragraph Surligner, Note and Copier.
- Reload persistence, installed update and offline reopen.
- No Google Translate/Search overlay from the app highlighting workflow.

## Desktop keyboard / accessibility smoke
- Tab order reaches primary navigation and reader actions.
- Visible focus indication on controls.
- Dialogs/sheets trap Tab/Shift+Tab, Escape closes, focus returns to trigger.
- 200% browser zoom: no essential horizontal scrolling.
- Reduced-motion OS preference removes non-essential animation.

## Live GitHub Pages
- Visible version v101.62.
- Service worker controls the page after activation.
- Cache generation is luisa-24h-v101-62.
- Existing install updates to v101.62 without personal-data loss.
- Offline reopen succeeds after successful online load.
- Old app cache generations are removed only within the luisa-24h- namespace.
- Root/deploy bytes correspond to the audited candidate.
