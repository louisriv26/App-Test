# v101.143 R1 — CONC-24H-01 frozen successor candidate

Current stage: `PERSONAL_STATE_CONCURRENCY_SUCCESSOR_R1`. Immediate immutable predecessor: `v101.142 R1` SHA-256 `5e94f3cbdff075b43dfb3c6278d30a81c94df2ccdebcabe942c5fa75b537b2c0`. This successor is limited to the confirmed 24H multi-context personal-state committed-change-loss repair. Full support floor approved by the owner: iOS/iPadOS 15.4+ and equivalent modern Android/Samsung; older engines are best-effort.

Repair invariant: serialize app-specific personal writes, read fresh durable state inside serialization, merge only the initiating operation, preserve newer same-record durable state on conflict, retain verified persistence/rollback and legacy mirrors, reconcile peer UI, and serialize import/startup/position write paths.

Protected: corpus text, speakers, stable IDs/order, Search semantics/cap, typography/contrast/Repères semantics, PWA identity-critical fields, backup schema, Hub architecture and unrelated Service Worker behavior.

This ZIP does not self-certify final bytes. Device candidacy requires an external SHA-bound reopened-package receipt. Physical/live-origin/PWA/offline/screen-reader gates remain `NOT TESTED`.
