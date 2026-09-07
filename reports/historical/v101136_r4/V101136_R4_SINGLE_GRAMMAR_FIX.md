# v101.136 R4 — Single Grammar Fix

- Release-engineering predecessor: v101.136 R3 `994e7a76ecc1947f150d68c5d01d36fdeaca96574ae459787fd845fd82b59f14`.
- Public app version remains **v101.136**; build revision is **R4**.
- Exact new authorized mutation: **1 record**, `PASSION24.TEXT.RELATED_HOUR_13.BODY.P124`.
- R3 text: `à la porte leur cœur`.
- R4 text: `à la porte de leur cœur`.
- Total canonical delta relative to immutable v101.135 is now **97 records = 84 local + 13 official-R6 sync**.
- New 97-record authority ledger SHA-256: `f9c89f2fdcb0f6588cb4250e8ea4bc00d9ccf1f51900a83d77e6e3b415ae9394`.
- No H23 source-critical finding is included. This record had previously been under the upstream dependency gate; the user’s new explicit authorization supersedes that gate **only for the exact insertion `de `**. No other upstream finding or action is consumed by R4.
- The correction is recension-invariant French grammar. The French GE/Lumen Luminis source itself contains the inherited omission; Italian/English controls confirm the intended meaning concerns knocking at hearts.
- Official LDC R6 is not mutated here; the corresponding source defect is flagged for its separate QA workstream.
- Physical-device, installed-PWA, true-offline, accessibility and live-origin gates remain open; final public deployment remains unauthorized until those tests pass.
