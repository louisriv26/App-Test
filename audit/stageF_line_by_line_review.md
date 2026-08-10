# 24H-F exact-change review

- Bottom navigation: `bnLibrary` primary slot replaced by `bnSearch`; fourth slot renamed to exact `Mon Espace`.
- `setBottomNav`: primary mapping is now Home/Hours/Search/Mon Espace; secondary Approfondir intentionally has no primary active state.
- Search view: activates `bnSearch`.
- Heures view: adds one direct `Approfondir la Passion` secondary chip.
- Home: existing Approfondir/Livre du Ciel card preserved unchanged.
- Reader: existing Textes liés / Approfondir pathways preserved unchanged.
- Settings/sidebar: Approfondir preserved unchanged.
- Back restoration: Home restore now restores Home navigation state and focus; this was found by the first Stage-F browser gate and corrected (`redo_count = 1`).
- Help: navigation grammar updated to Accueil · Heures · Recherche · Mon Espace; Approfondir explicitly described as secondary, not deleted.
- Version/SW/manifest/checklist: advanced to v101.60.
- Protected declarations: byte-identical to v101.59.

No corpus, storage schema, Repères, contextual-action, deep-link or platform-highlight policy change is present.
