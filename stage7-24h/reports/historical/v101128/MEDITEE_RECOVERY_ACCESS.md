# v101.128 Méditée Recovery Access / Single-State Synchronisation

- Predecessor: immutable `v101.127` / `d2614307d3335d4e76a3b9559cb4d8267549b9a5a4adf4ec616344f2b98664d6` / 440 members.
- User need: after forgetting the bottom `Méditée` action, reopening an Hour from the list currently starts at the top and otherwise requires scrolling through the complete Hour again.
- UX repair: activates the existing `buildMarkBar(hourNum)` slot below the Hour header as a discreet recovery/status control while preserving the existing bottom action.
- Single authority: `state.readHours`. Single state-changing action: `markMeditee(hourNum)`.
- The two visual controls are synchronized by `refreshMediteeControls(hourNum)`; no new progression state or storage key exists.
- Toggle refresh is DOM-only: `renderReader()` is not called by `markMeditee()`.
- Hour-24 completion remains exactly 24 explicit `Méditée` states via `getProgressSnapshot()`.
- Canonical/devotional text changes: **0**. Speaker/presentation/continuity data changes: **0**. Storage/snapshot schema changes: **0**.
- Physical-device/PWA/offline/live-origin/screen-reader evidence remains external.
