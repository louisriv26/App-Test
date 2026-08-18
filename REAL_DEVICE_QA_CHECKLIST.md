# 24H interaction closure / v101.85 — physical device, installed-PWA and live-origin checklist

Use the exact v101.85 candidate bytes. Record PASS/FAIL/NOT_TESTED for every numbered scenario.

## iPhone Safari / installed PWA
1. Mid-Hour → Mon Espace → Retour restores the same reader tab, paragraph/reading position and visible/updating progress strip.
2. Change among 16 / 19 / 22 / 26 px while mid-Hour: the same visible passage/visual offset is preserved and no clipping appears.
3. Automatique / Clair / Sombre; each theme choice has a comfortable touch target.
4. Exact selected-text Surligner, Note, Copier and Fermer; then Réglages → Partager / Copier le lien.
5. Existing-highlight colour picker remains fully on-screen; all five colours and remove action are usable.
6. A visible paragraph note indicator is easy to tap and opens the expected note.
7. Plan button and Plan close control are easy to tap where Plan exists.
8. Prayer close control is easy to tap.
9. Note textarea does not trigger focus zoom; keyboard dismissal is usable.
10. Repères OFF/ON preserves passage and actions.
11. Portrait ↔ landscape rotation preserves a usable reader.
12. With a non-empty unsaved Note open, an available-update Actualiser action must NOT reload; the draft remains and receives focus.
13. Existing installed build → v101.85 update preserves notes, coloured highlights, reading position and progress; obsolete legacy ◈ marks may be discarded.
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
29. Dialogs/sheets trap Tab/Shift+Tab and Escape closes them; focus returns to the trigger, or to the stable reading region when a transient contextual Note/colour-picker trigger has already disappeared.
30. 200% browser zoom: no essential horizontal scrolling.
31. Reduced-motion OS preference removes non-essential animation.
32. On-demand controls (theme, Plan, prayer close, note indicator, Approfondir back/index) remain keyboard reachable and visibly focused.

## Live GitHub Pages / installed PWA
33. Visible version v101.85.
34. Service worker controls the page after activation.
35. Cache generation is luisa-24h-v101-84.
36. Existing install updates to v101.85 without loss of supported personal data; retired legacy ◈ marks are intentionally not preserved.
37. Offline reopen succeeds after successful online load.
38. Old app cache generations are removed only within the luisa-24h- namespace.
39. Root/deploy bytes correspond exactly to the audited GitHub payload.
40. Root and copied deep-link URLs reach the expected screen/target on the live origin.

## Downgrade / future-snapshot safety (machine fixture; device spot-check optional)
41. A canonical snapshot with `snapshot_version` greater than 4 remains byte-for-byte unchanged after boot, even when legacy mirrors and the R41 marker are absent.
42. While that future snapshot is present, Note or other durable writes must not replace it; user feedback must say the change was not saved / the newer snapshot is preserved.

43. A canonical snapshot at current `snapshot_version` but future `schema_version` remains byte-for-byte unchanged after boot and attempted writes.
44. While a future canonical snapshot/schema is present, machine JSON export is refused with an explicit newer-version preservation message rather than producing an incomplete backup.

## High-count personal-data completeness (machine fixture; device spot-check optional)
45. A seeded snapshot with 250 valid notes on one paragraph loads all 250; after an ordinary saved preference change all 250 remain in the canonical snapshot and machine export.
46. A seeded snapshot with 250 valid text-highlight records on one paragraph loads all 250; after an ordinary saved preference change all 250 remain in the canonical snapshot and machine export.
47. A v101.79 snapshot containing legacy `highlights` / `lp24_hl` upgrades to schema 8/snapshot 5 with the retired marks discarded while notes, coloured textHighlights, progress and positions remain intact.
48. Mon Espace may preview high-count notes/highlights only with the exact total and an explicit `Voir tout`; expansion makes every record reachable.

## Legacy whole-paragraph mark reachability
49. No `◈` paragraph-mark creation control exists on desktop, iPhone, iPad or Samsung.
50. Legacy `highlights` records from an older canonical snapshot are ignored/removed during migration and do not appear in Mon Espace or Passages à vérifier.
51. The retired `lp24_hl` mirror key is removed when supported state is successfully synchronised; failure to remove it is reported as a mirror failure rather than a false success.

## Legacy mark backup/journal completeness
52. Backup-reminder counts use supported coloured highlights and notes only; retired paragraph marks do not affect the count.
53. The human-readable journal contains supported coloured highlights only and contains no legacy paragraph-mark category.
54. New machine exports do not contain a `highlights` legacy paragraph-mark field.

## Wide/tablet annotation preview truth
55. With only a Samsung whole-paragraph coloured `textHighlights` record present, Mon Espace and the wide preview show it as an ordinary coloured surlignage.
56. Stale/missing supported textHighlights remain disclosed as passages to verify, while full details/removal remain in Mon Espace.
57. With no supported textHighlight records, the wide preview may correctly show `Aucun surlignage`.


## Extreme-deep backup / route fixtures
58. Exact app-generated JSON backup larger than 5 MiB but below 32 MiB is accepted by Restore and preserves every validated record after replace-import.
59. Malformed/prototype-key prayer deep links (`__proto__`, `constructor`, `toString`, markup payloads, overlong IDs) never throw or execute content; they fall back recoverably with `prière introuvable`.

60. Open an existing-highlight colour picker and tap immediately during its entrance motion: all five swatches and Remove retain >=44x44 CSS-px hit areas throughout the animation; none shrink because of a parent scale transform.

61. Storage partial-failure regression (developer/device harness where injectable): if a canonical write succeeds but its immediate verification read fails, the exact previous canonical snapshot must be restored; after reload no change may appear that the UI reported as not saved.
62. Storage pre-read failure regression (developer/device harness where injectable): if the existing canonical snapshot cannot be read before save, no canonical write is attempted and the current durable bytes remain untouched.

63. Restore wrong-file protection: an explicitly foreign/other-app JSON backup and an arbitrary schema-only JSON file are rejected without changing current notes/progression; a genuine historical v101.53 24H backup without the new format/app_id markers is still accepted.

64. Storage/import integrity: a simulated canonical post-write verification failure whose rollback also fails must never produce a false 'not saved' state; malformed backups containing invalid personal records must be rejected without replacing current data.

65. Auxiliary storage honesty: if recent-text or onboarding preference storage is unavailable, the UI must keep the stated choice/list effective for the current session and must not falsely claim session persistence.

66. Help completeness: open Aide and confirm the contextual-actions section explains Surligner, Note, Copier and Fermer; confirm a separate reference section explains Partager and Copier le lien plus privacy/cancellation semantics; confirm Note, backup JSON vs journal Markdown and unsaved-note update protection remain explained.

67. Help attribution-status honesty: open Aide → Recherche and À propos du corpus; confirm it does NOT say the direct-speech review is still pending, and states that the editorial review of the current attribution layer is already closed.

68. iPad paragraph-side controls: in Méditation and Réflexions, confirm no legacy paragraph-side rail appears. Select exact text and confirm Surligner · Note · Copier · Fermer; verify Réglages → Partager / Copier le lien.
69. Desktop regression: on a fine-pointer desktop, hover meditation/reflection paragraphs and confirm no legacy paragraph-side rail appears; exact text selection still opens Surligner · Note · Copier · Fermer.
70. Samsung regression: confirm no legacy side rail appears; use Paragraphe mode and confirm Surligner · Note · Copier · Fermer opens for the tapped whole paragraph and creates a normal coloured whole-paragraph highlight.

71. Mon Espace with at least one ordinary highlight and one note opens fully; highlights, notes, progression and backup controls are visible and no reader screen remains stuck underneath.
72. Delete one note, one normal highlight, one grouped highlight and one stale highlight individually; each successful deletion offers **Annuler**, and Undo restores only that annotation without overwriting a later edit.
73. Open **Note** from the temporary selection toolbar, then close immediately with Escape and with the close button; focus returns to the stable reading region after the toolbar disappears, never to `<body>`.
74. Export a backup containing a highlight, import it into the same v101.85 build, and confirm the highlight still carries valid `text_hash`, `para_hash` and `paragraph_fingerprint` integrity metadata and renders at the same passage.


## v101.85 user-feedback additions

75. 17e Heure: `... contiennent, et constitue-Moi ...` displays without a break inside `et`; direct-speech/narration visual separation remains after the closing guillemet.
76. 15e Heure: the visible continuation reads `... ton silence, il proclame devant tous que Tu es un fou.` while P014/P015 anchors remain usable.
77. Approfondir: mark a reading title in each of five colours; reload; confirm persistence and independent body highlights.
78. Mon Espace → Lectures marquées: open the mark and confirm the whole reading opens at its beginning.
79. Remove a title mark, use Annuler, and confirm exact restoration.
80. Export/import a v101.85 backup and confirm title marks survive; import an older schema-7/snapshot-4 backup and confirm existing data survives with no title marks invented.
