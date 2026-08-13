# 24H-G extreme-deep recheck / v101.79 — physical device, installed-PWA and live-origin checklist

Use the exact v101.79 candidate bytes. Record PASS/FAIL/NOT_TESTED for every numbered scenario.

## iPhone Safari / installed PWA
1. Mid-Hour → Mon Espace → Retour restores the same reader tab, paragraph/reading position and visible/updating progress strip.
2. 16 / 19 / 22 / 26 px reader sizes; no clipping.
3. Automatique / Clair / Sombre; each theme choice has a comfortable touch target.
4. Exact selected-text Surligner, Copier, Lien and Note.
5. Existing-highlight colour picker remains fully on-screen; all five colours and remove action are usable.
6. A visible paragraph note indicator is easy to tap and opens the expected note.
7. Plan button and Plan close control are easy to tap where Plan exists.
8. Prayer close control is easy to tap.
9. Note textarea does not trigger focus zoom; keyboard dismissal is usable.
10. Repères OFF/ON preserves passage and actions.
11. Portrait ↔ landscape rotation preserves a usable reader.
12. With a non-empty unsaved Note open, an available-update Actualiser action must NOT reload; the draft remains and receives focus.
13. Existing installed build → v101.79 update preserves personal data.
14. Offline reopen after one successful online load works.
15. A copied deep link opens the expected Hour/paragraph.

## iPad Safari portrait / landscape
16. Reader width, bottom navigation, exact selection and long-scroll remain usable.
17. Mid-Hour → Mon Espace → Retour restores exact context and progress.
18. Repères, 26 px, Mon Espace, rotation/split-view.
19. Plan/theme/prayer/note and Approfondir navigation targets are comfortable to tap.
20. Installed-PWA update and offline reopen.

## Samsung / Android Chrome
21. Paragraphe mode only; no expectation of native word selection.
22. Whole-paragraph Surligner, Note and Copier.
23. Reader → Mon Espace → Retour restores the same paragraph context/progress.
24. Plan/theme/prayer/note and Approfondir navigation targets are comfortable to tap.
25. Reload persistence, installed update and offline reopen.
26. No Google Translate/Search overlay from the app highlighting workflow.

## Desktop keyboard / accessibility smoke
27. Tab order reaches primary navigation and reader actions; no hidden zero-size control receives focus.
28. Visible focus indication on controls.
29. Dialogs/sheets trap Tab/Shift+Tab, Escape closes, focus returns to trigger.
30. 200% browser zoom: no essential horizontal scrolling.
31. Reduced-motion OS preference removes non-essential animation.
32. On-demand controls (theme, Plan, prayer close, note indicator, Approfondir back/index) remain keyboard reachable and visibly focused.

## Live GitHub Pages / installed PWA
33. Visible version v101.79.
34. Service worker controls the page after activation.
35. Cache generation is luisa-24h-v101-79.
36. Existing install updates to v101.79 without personal-data loss.
37. Offline reopen succeeds after successful online load.
38. Old app cache generations are removed only within the luisa-24h- namespace.
39. Root/deploy bytes correspond exactly to the audited GitHub payload.
40. Root and copied deep-link URLs reach the expected screen/target on the live origin.

## Downgrade / future-snapshot safety (machine fixture; device spot-check optional)
41. A canonical snapshot with `snapshot_version` greater than 3 remains byte-for-byte unchanged after boot, even when legacy mirrors and the R41 marker are absent.
42. While that future snapshot is present, Note or other durable writes must not replace it; user feedback must say the change was not saved / the newer snapshot is preserved.

43. A canonical snapshot at current `snapshot_version` but future `schema_version` remains byte-for-byte unchanged after boot and attempted writes.
44. While a future canonical snapshot/schema is present, machine JSON export is refused with an explicit newer-version preservation message rather than producing an incomplete backup.

## High-count personal-data completeness (machine fixture; device spot-check optional)
45. A seeded snapshot with 250 valid notes on one paragraph loads all 250; after an ordinary saved preference change all 250 remain in the canonical snapshot and machine export.
46. A seeded snapshot with 250 valid text-highlight records on one paragraph loads all 250; after an ordinary saved preference change all 250 remain in the canonical snapshot and machine export.
47. A seeded legacy list with 5,001 distinct valid highlight IDs is not silently truncated during sanitisation/load/save/export.
48. Mon Espace may preview high-count notes/highlights only with the exact total and an explicit `Voir tout`; expansion makes every record reachable.

## Legacy whole-paragraph mark reachability
49. A current valid `◈` whole-paragraph mark is listed in Mon Espace → Surlignages and opens the correct paragraph.
50. A stored `◈` mark whose paragraph no longer exists is listed in Passages à vérifier and can be removed there.
51. If persistence fails while removing a legacy mark, the mark remains in state/storage and no success message is shown.

## Legacy mark backup/journal completeness
52. Twelve whole-paragraph `◈` marks with no other annotations trigger the normal backup-reminder threshold.
53. The human-readable journal lists every whole-paragraph mark and never says `Aucun surlignage` while any such mark exists.
54. A missing-target whole-paragraph mark is represented in the journal as a passage to verify, without inventing replacement text.

## Wide/tablet annotation preview truth
55. With only a resolved whole-paragraph `◈` mark present, the wide Mon Espace preview shows that mark and does not say `Aucun surlignage`.
56. Stale/missing annotation records are disclosed in the wide preview as passages to verify, while full details/removal remain in Mon Espace.
57. With no text-highlight or whole-paragraph-mark records at all, the wide preview may correctly show `Aucun surlignage`.


## Extreme-deep backup / route fixtures
58. Exact app-generated JSON backup larger than 5 MiB but below 32 MiB is accepted by Restore and preserves every validated record after replace-import.
59. Malformed/prototype-key prayer deep links (`__proto__`, `constructor`, `toString`, markup payloads, overlong IDs) never throw or execute content; they fall back recoverably with `prière introuvable`.

60. Open an existing-highlight colour picker and tap immediately during its entrance motion: all five swatches and Remove retain >=44x44 CSS-px hit areas throughout the animation; none shrink because of a parent scale transform.

61. Storage partial-failure regression (developer/device harness where injectable): if a canonical write succeeds but its immediate verification read fails, the exact previous canonical snapshot must be restored; after reload no change may appear that the UI reported as not saved.
62. Storage pre-read failure regression (developer/device harness where injectable): if the existing canonical snapshot cannot be read before save, no canonical write is attempted and the current durable bytes remain untouched.

63. Restore wrong-file protection: an explicitly foreign/other-app JSON backup and an arbitrary schema-only JSON file are rejected without changing current notes/progression; a genuine historical v101.53 24H backup without the new format/app_id markers is still accepted.

64. Storage/import integrity: a simulated canonical post-write verification failure whose rollback also fails must never produce a false 'not saved' state; malformed backups containing invalid personal records must be rejected without replacing current data.

65. Auxiliary storage honesty: if recent-text or onboarding preference storage is unavailable, the UI must keep the stated choice/list effective for the current session and must not falsely claim session persistence.

66. Help completeness: open Aide and confirm the dedicated contextual-actions section explains Surligner, Copier, Lien, Note and Fermer; confirm Note explains Enregistrer/2 000 chars/multiple notes/delete/Mon Espace; confirm backup JSON vs journal Markdown and unsaved-note update protection are explained.

67. Help attribution-status honesty: open Aide → Recherche and À propos du corpus; confirm it does NOT say the direct-speech review is still pending, and states that the editorial review of the current attribution layer is already closed.

68. iPad paragraph-side controls: in Méditation and Réflexions, scroll/tap paragraphs in portrait and landscape. Confirm no half-hidden ◈/⎘/✎ side buttons appear at the right edge. Select exact text and confirm the contextual action bar remains available.
69. Desktop regression: on a fine-pointer desktop, hover a meditation/reflection paragraph and confirm the legacy paragraph-side actions remain fully available and clickable.
70. Samsung regression: confirm no legacy side rail appears; use Paragraphe mode and confirm the shared contextual action bar opens for the tapped whole paragraph.
