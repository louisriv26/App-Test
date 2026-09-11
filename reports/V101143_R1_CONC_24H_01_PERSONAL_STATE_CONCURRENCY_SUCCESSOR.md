# v101.143 R1 — CONC-24H-01 personal-state concurrency successor

- Immediate immutable predecessor: `v101.142 R1` / `5e94f3cbdff075b43dfb3c6278d30a81c94df2ccdebcabe942c5fa75b537b2c0`.
- Repair ID: `CONC-24H-01`.
- Full-support floor: owner-approved iOS/iPadOS 15.4+ and equivalent modern Android/Samsung; older best-effort.
- App-specific lock: `collection-luisa:24h:personal-state:v1`.
- Commit model: lock → fresh durable read → operation-level delta/merge → same-record conflict check → guarded verified canonical persist/rollback → coherent legacy mirrors → peer reconciliation.
- Covered writers: ordinary state changes, deletes/Undo, import/restore, startup migration/recovery/healing, lifecycle/resume preferences, recent-text/export/onboarding auxiliary personal keys and coalesced reading-position persistence.
- Schemas remain storage 8 / personal snapshot 5.
- Corpus/speaker/stable-ID/Search/typography/Repères/PWA identity/backup/Hub/unrelated SW behavior remain protected.
- `VER-LINEAGE-24H-01`: `SEPARATE_VERSION_SIMPLIFICATION_REQUIRED`; therefore this P0 repair remains on the historically coherent legacy line `v101.143 R1`.
- The exact ZIP must be externally reopened and SHA-bound; physical/live/PWA/offline/AT gates remain separate.
