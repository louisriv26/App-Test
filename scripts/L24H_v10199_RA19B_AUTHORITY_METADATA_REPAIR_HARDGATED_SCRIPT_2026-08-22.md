# L24H v101.99 — RA19B current-authority metadata repair — HARD-GATED EXECUTION

## Governing inputs
- Baseline: `L24H_v10198_GITHUB_DEPLOY_LDC_RA19B_MULTI_SOURCE_FLOW_SYNC_R1_LOCKED.zip`
  - SHA-256 `4e60d4de82fe7d4ca79f753328e6fa8e399eb4157ea4217234f63cf5838cdbda`
- LDC authority: `LDC_v2.19.29-R1B_GITHUB_DEPLOY_RA19B_MULTI_SOURCE_FLOW_ADJUDICATED_LOCKED(1).zip`
  - SHA-256 `eb2fa6abce1525399547f469ad1c2d64e818ff8685fe11cc20a57571c59f92fc`
- Fresh v101.98 failure: stale active RA18 authority metadata in `LDC_CURRENT_SYNC_AUTHORITY`, Promesses `CORPUS.ldc_sync`, and 21 Promesses `ldc_source_map` records.

## Hard stop rules
Stop before modifying app files if any input hash is wrong; RA19B Version 29 authority cannot be verified; current v101.98 flow/text/speaker data differ from the audited baseline; repair scope is not mechanically identifiable; or any editorial/product judgement is required.

Do not proceed past any failed gate. Do not claim PASS unless the sealed final ZIP reopens and both the primary and separately implemented independent reopened-ZIP audits pass.

## Protected invariants
The following must remain semantically/exactly unchanged from v101.98:
- `TEXT_LIBRARY`
- `SPEECH_DATA`
- `SPEECH_END_VISUAL_BREAKS`
- `HOUR_LINKED_TEXTS`
- `LDC_LIBRARY_FLOW_LAYOUT`
- all user-visible `CORPUS` wording/titles/paragraph IDs/order
- all highlighting, Samsung grouping, Apple selection, notes/favourites and storage code

`CORPUS` may change only in `PASSION24.SECTION.BENEFITS` source-governance metadata:
- `ldc_sync.source_app_version`
- `ldc_sync.source_public_version`
- `ldc_sync.source_package_sha256`
- `ldc_sync.mode`
- each of the 21 `ldc_source_map[*].status`
- each of the 21 `ldc_source_map[*].source_reason`

## Authorized repairs
1. Replace stale `LDC_CURRENT_SYNC_AUTHORITY` RA18 identity/counts with RA19B Version 29 identity/counts:
   - source `Version 29 / v2.19.29-R1B`
   - source SHA `eb2fa6ab...9f92fc`
   - 115 mapped blocks
   - 61 changed blocks vs RA18
   - 100 preserve breaks
   - 0 list breaks
   - 66 runtime overrides
2. Synchronize Promesses `CORPUS.ldc_sync` to RA19B.
3. Synchronize its 21 current-source-map records from `SYNCED_CURRENT_LDC_RA18` to `SYNCED_CURRENT_LDC_RA19B` with RA19B source-backed-flow reason.
4. Bump release to v101.99 / cache `luisa-24h-v101-99`.
5. Strengthen static/stale tests so any current RA18 authority identity in active HTML is blocking.
6. Regenerate current reports, QA identity, manifests, hashes, provenance and final decision lock.

## Prepackage hard gates
- HTML twins byte-identical.
- `LDC_CURRENT_SYNC_AUTHORITY` exactly RA19B.
- Promesses `CORPUS.ldc_sync` exactly RA19B.
- Promesses 21/21 source maps current RA19B.
- no `SYNCED_CURRENT_LDC_RA18` or `Current LDC RA18` remains in active HTML.
- no active Version 28 / RA18 package SHA remains in current source-governance objects.
- protected objects exact vs v101.98 except explicitly allowed `CORPUS` metadata paths.
- runtime layout counts unchanged: 66 overrides, 1,518 paragraph actions, 100 preserve actions, 0 list actions.
- runtime browser suite: 66 flow surfaces, 1,584/1,584 Samsung groups, 145 Promesses Jesus spans, no duplicate IDs/errors.

## Final audit gates
### Primary reopened-ZIP audit
Fresh extraction of sealed final ZIP; verify CRC/member/path integrity, package/hash manifests, HTML twins, version/cache identity, enhanced current-authority assertions, static test and browser runtime suite.

### Independent reopened-ZIP audit
Separate implementation and fresh extraction. It must not call the primary audit. Verify:
- package/hash integrity independently;
- exact protected-object parity against immutable v101.98 baseline;
- only allowed `CORPUS` metadata paths differ;
- final flow layout exact-equals v101.98 layout;
- 100 preserve-boundary source pairs remain backed by RA19B `visual_action=preserve_break` evidence;
- active source-governance metadata is RA19B everywhere;
- no current RA18 authority markers remain;
- independent Chromium smoke of Promesses and representative flow rerender/grouping.

## Final decision
Write/report only the status supported by both reopened-ZIP audits. Physical iPhone/iPad/Samsung, live PWA and true offline remain `NOT_TESTED` unless separately proven.

No Word review packs.
