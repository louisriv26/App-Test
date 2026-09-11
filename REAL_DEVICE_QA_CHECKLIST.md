# Real-device QA checklist — v101.143 R1 / CONC-24H-01

Use only the exact SHA-bound frozen candidate after external reopened-package certification.

## Multi-context personal-state integrity
- Open two active instances of 24H on the same origin.
- Add a note in A while B holds stale progress state; then change progress in B. Both committed changes must survive.
- Repeat in the reverse direction.
- Add independent notes/highlights on the same paragraph from A/B; both must survive.
- Create a same-record edit conflict; the newer durable record must not be silently overwritten and the stale action must fail/retry visibly.
- Delete/Undo note, highlight and library-mark records while the peer adds an independent record; unrelated peer records must survive.
- Exercise rapid reading-position movement while adding a note in the peer; the note must survive and the latest non-conflicting position must persist.
- Create a same-Hour position conflict; the newer durable pointer must be preserved.
- Begin Import confirmation, commit a peer change, then continue Import; Import must abort rather than erase the peer change.

## Failure/recovery
- Storage write failure preserves previous durable bytes.
- Read-back mismatch rolls back exact previous bytes where possible.
- Future snapshot/schema remains fail-closed and byte-preserved.
- Canonical success with a legacy mirror failure remains canonical success with honest warning.

## Protected regression
- Existing notes/highlights/progress/resume/theme/font/Repères mechanics survive update and reopen.
- Search behavior/cap, Hour 24, Méditée, native visible-flow topology and stable anchors are unchanged.
- Manifest installed identity remains unchanged.

## External gates
- Physical iPhone.
- Physical iPad portrait/landscape.
- Physical Samsung/Android.
- Live-origin exact-byte binding.
- Installed-PWA update from deployed v101.142 R1 and three close/reopen cycles.
- True offline cold reopen.
- Representative VoiceOver/TalkBack.
