# Current execution specification — v101.118

Stage: `FOUR_PASS_GENERIC_EXECUTION_SPEC_INTEGRITY_REPAIR_R1`.

Baseline: immutable v101.117.

Scope: execution-spec/evidence integrity only. No governed runtime declaration, canonical devotional text, RA19B source-flow decision, RA19E.2 semantic/presentation decision, feature behaviour or UX behaviour may change.

Required build lifecycle: exact baseline hash → protected declaration parity → current metadata/spec checks → fresh 52/52 Chromium matrix → fresh 15/15 service-worker logic matrix → independent prefreeze audit → active-report line audit → deterministic A/B package freeze → external primary reopened-ZIP audit → external separately implemented reopened-ZIP audit → external final decision lock.

External physical Samsung/iPhone/iPad, live-origin PWA/offline, and VoiceOver/TalkBack gates remain `NOT_TESTED` until directly executed.
