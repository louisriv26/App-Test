# v101.60 / 24H-F — staging and owner usability checklist

Test the exact packaged candidate. Do not rebuild it for staging.

## Navigation grammar
1. Confirm the bottom bar reads **Accueil · Heures · Recherche · Mon Espace**.
2. Confirm the top-header Search/loupe shortcut is still present.
3. Tap Recherche in the bottom bar; confirm Recherche is visibly active.
4. Search for a phrase, set a filter, open a result, then Retour; confirm query/filter/result scroll return.
5. Tap Mon Espace; confirm the label and destination are Mon Espace.

## Approfondir preservation
6. Accueil: confirm the Approfondir / Livre du Ciel card remains present and opens correctly.
7. Heures: confirm **Approfondir la Passion** is visible and opens Approfondir; Retour must return to Heures.
8. Reader: confirm linked texts / Approfondir remain available and Retour restores the Hour.
9. Réglages: confirm Approfondir remains available.

## Inherited open gates
10. Run the inherited Stage-E staging/live deep-link round trip if staging is available.
11. iPhone/iPad exact-selection and existing-highlight picker retest remain inherited.
12. Samsung/Android paragraph-mode validation remains inherited / NOT_TESTED if unavailable.

Owner/user acceptance of the navigation prototype is required before production or 24H-G.
