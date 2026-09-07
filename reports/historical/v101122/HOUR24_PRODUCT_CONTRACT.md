# Hour 24 end-of-cycle product contract — v101.122

## Hours 1–23
Preserve: Réflexion et pratique · Approfondir · Revenir au début · Prier l’Heure suivante.
No cycle-management buttons.

## Hour 24 — Hour-level actions
Always show: Réflexion et pratique · Approfondir · Revenir au début.

## Hour 24 — incomplete cycle
Condition: `getProgressSnapshot().complete === false`.
Show `VOTRE PARCOURS`, `X/24 Heures marquées comme méditées`, `Voir ma progression`, `Revoir les Heures méditées`.
No restart/reset button and no completion claim.

## Hour 24 — complete cycle
Condition: `getProgressSnapshot().complete === true`.
Show `LE CYCLE DES 24 HEURES EST ACCOMPLI`, `24/24 Heures marquées comme méditées`, `Recommencer depuis la 1re Heure`, `Voir ma progression`, `Revoir les Heures méditées`.

## Completion semantics
Being on Hour 24 is not cycle completion. Cycle completion is exactly 24/24 explicit Méditée states. No Hour is automatically marked Méditée.
