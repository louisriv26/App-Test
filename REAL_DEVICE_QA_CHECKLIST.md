# Real-device QA checklist — prototype-77

## Samsung / Android P0 check

- Confirm the Aide modal still scrolls and closes.
- Confirm Accueil scrolls vertically.
- Open a long Hour and confirm it scrolls to the bottom.
- Confirm Textes scrolls vertically.
- Confirm Mon Espace scrolls vertically.
- Confirm bottom navigation buttons remain tappable.

## iPhone / iPad regression check

- iPhone Safari: Accueil, Heure, Textes, Mon Espace, Aide.
- Installed iPhone PWA: same checks.
- iPad Safari portrait and landscape: same checks.

Static package status before real-device validation: LIMITED_PASS_STATIC.


## Stage 5I required checks

- iPhone portrait: bottom navigation remains visible, labels visible, and perceived band height reduced.
- iPhone landscape: bottom navigation labels Accueil / Heures / Textes / Espace are visible.
- iPhone Aide / À propos: content no longer passes behind the modal title/close area while scrolling/bouncing.
- Samsung/Android: Accueil, full Hour, Textes, Mon Espace still scroll.
- iPad: portrait and landscape regressions not detected.
