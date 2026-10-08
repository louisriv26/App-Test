# LDC v142.16 — Physical retest protocol

**Candidate:** 142.16 · `v2.19.142.16-R1B-READER-PHYSICAL-GATE-REPAIR`  
**Frozen runtime commit:** `15fb524cc8929c04d2e92f560374cdbe5404148c`  
**Direct predecessor:** v142.15 package SHA-256 `cca03c4a6e07cd7f25b4a6a8cc6caadaf912ede76354a0b71236c93d2dd728bc`  
**Status:** not production-authorized. Run only after exact-byte App-Test deployment/binding of v142.16.

## Purpose

This retest closes the two iPhone physical defects discovered on v142.15 without reopening unrelated corpus/search behavior:

1. paragraph-target navigation from **Mon Espace** must not move the document/root viewport;
2. the Reader must remain usefully readable when an iPhone moves between portrait and landscape, including Safari with browser chrome visible.

## A — iPhone: Mon Espace → paragraph target

1. Open App-Test and confirm **Version 142.16**.
2. Keep the iPhone in portrait.
3. Go to **Mon Espace → Surlignages**.
4. Open a highlight located around the middle of a long entry.
5. Confirm the highlighted paragraph is visible.
6. Confirm the normal Reader structure is intact: Reader top, **Retour**, text, **Entrée précédente / Lu / Entrée suivante** and the global navigation are in their normal places.
7. Confirm there is **no large blank gap** below the entry navigation and no Reader chrome stranded around mid-screen.
8. Repeat with a highlight near the beginning of an entry.
9. Repeat with a highlight near the end of an entry.
10. Repeat once from a paragraph-linked note or collection item if available.

**FAIL / blocker:** any displaced whole-page layout, missing Reader top, large artificial blank region, wrong paragraph target, blank Reader, or unexpected jump to entry start.

Optional Web Inspector evidence after each open:
- `window.scrollY === 0`
- `document.scrollingElement.scrollTop === 0`
- `document.documentElement.scrollTop === 0`
- `document.body.scrollTop === 0`

## B — iPhone: portrait ↔ landscape Reader

1. From **Tomes**, open a normal long entry in portrait.
2. Scroll into the middle and remember the first words currently visible.
3. Rotate to landscape **with Safari browser controls visible**.
4. Confirm actual Livre du Ciel text remains visible; the Reader must not collapse to an empty strip.
5. Confirm **Retour** and **Entrée précédente / Lu / Entrée suivante** remain usable.
6. If the screen is too short, it is acceptable and expected for the global **Accueil / Tomes / Recherche / Mon Espace** bar to disappear temporarily so that the text keeps usable height.
7. Rotate back to portrait.
8. Confirm the global bottom navigation returns automatically.
9. Confirm the Reader remains on approximately the same semantic paragraph rather than jumping to the beginning or another passage.
10. Repeat portrait → landscape → portrait **five times**.
11. Repeat once with text size **Très grand**.
12. Repeat once with **Corpus principal** or **Compléments** active so the documentary-status bar is present.

**FAIL / blocker:** text becomes blank/unreadable, the usable Reader height collapses near zero, the global nav fails to return in portrait, rotation causes an unrelated passage/start-of-entry jump, or controls become unusable.

## C — Search regression

1. Recherche → **Par les mots**; search for `Fiat`.
2. Open a result.
3. Confirm the result opens at the intended passage and the page/root is not displaced.
4. Return to Search.
5. Run one **Par le sens** query and open a result.
6. Repeat portrait ↔ landscape once while the result is open.

**PASS:** search target navigation remains correct and no root-scroll/layout defect appears.

## D — iPad regression

Repeat:
- one Mon Espace → Surlignage open;
- one normal Reader portrait ↔ landscape ↔ portrait cycle;
- one Search → Reader open.

The low-height compact mode should normally **not** activate on an iPad if the Reader has sufficient real height.

## E — installed PWA

If App-Test is installed to the Home Screen:

1. Launch the installed v142.16 PWA.
2. Repeat one Mon Espace → Surlignage test.
3. Repeat one portrait ↔ landscape ↔ portrait Reader cycle.
4. Confirm safe areas remain respected and no control is clipped by the home indicator/notch.
5. Confirm the app remains usable after a cold restart.

## F — VoiceOver delta check

Because compact mode can temporarily remove the global bottom navigation from the accessibility tree:

1. Turn on VoiceOver in the Reader.
2. Rotate into the low-height landscape state.
3. Confirm focus is not trapped or lost.
4. Confirm **Retour** remains reachable and understandable.
5. Rotate back to portrait and confirm the global navigation is available again.
6. Re-run the existing v142.15 documentary-modal VoiceOver gate if not already passed.

## Release rule

v142.16 remains **production blocked** until:
- exact App-Test candidate binding passes;
- sections A and B pass on a real iPhone;
- D passes on a real iPad;
- applicable PWA and VoiceOver gates pass or are explicitly adjudicated;
- no runtime byte changes are made after the frozen runtime commit. Any runtime change creates a successor candidate.
