# LDC 142.17 — Focused physical qualification protocol

**Only execute after explicit owner authorization, deployment of an exact candidate to App-Test, and SHA-256 / file-count binding.** No production authority.

## iPhone — Mon Espace targeting
Open `Mon Espace → Surlignages` and a highlighted paragraph near the middle of a long entry, then near its beginning and end. Verify the intended paragraph, a usable Reader top/back/header and bottom entry navigation, and **no root/document displacement or large blank gap**. Repeat from a linked note or collection. Check a Par les mots result and a Par le sens result. Repeat after switching documentary view.

## iPhone — rotation and short viewport
Open a long Tome entry in portrait. Read from halfway down and note the visible paragraph. Rotate to landscape with Safari chrome present. Confirm text is visible, scrolling works, and Retour plus previous/read/next are usable. In short height it is permissible for the four-tab global navigation to yield. Rotate back and verify it returns, with the same semantic passage preserved. Repeat five cycles, then in Très grand text and with a documentary-status bar. Repeat while rapidly switching passages.

## Interaction regression
- Open an entry and immediately navigate away; a late animation frame must not reset the destination's root scroll.
- Rapidly open two different highlight/search targets; final position must match last intended target and remain stable.
- Change text size; Reader stays on the same paragraph.
- Starting from Tome list, return to that list after Reader; preserve return position.
- Resume saved sequential position and navigate entries; do not corrupt prior reading state.
- During active selection/colour-picker/toast/update banner, rotate to short landscape; controls must not overlap or become inaccessible.

## iPad and installed PWA
On iPad repeat highlight, search target, rotation and Resume. Install the *exact candidate* to Home Screen and repeat target/rotation. Close/reopen; verify safe areas, persistent highlight, reading position and offline update as applicable.

## VoiceOver
Verify entering/exiting compact mode does not strand focus; Reader Retour remains reachable. Verify global nav returns to accessibility tree when compact mode exits. Recheck documentary modal and search-result label order.

## Mandatory device evidence
Record exact version, URL, device, iOS/iPadOS version, Safari vs PWA, display orientation, text size, source mode, expected vs observed result, evidence screenshot and PASS/FAIL. Preserve failures verbatim. If any runtime byte changes, repeat qualification on a new candidate.

**Production promotion remains prohibited until all applicable physical gates pass on the exact tested bytes.**
