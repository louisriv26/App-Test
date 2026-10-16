# R237 — APPLICATION-ONLY SUCCESSOR, DEVELOPMENT ONLY (2026-10-16)

**Status: HOLD — NOT DEPLOYABLE; not a replacement for the full immutable R237 candidate.**

This branch is derived from exact App Test v142.37 commit `8c036b4736d3ebde5bc816e772c29f05da54126d` and changes **only application shell and release metadata**, not any `corpus/**` asset, user-data schema, or semantic search component. The corpus generation and `offline_content_binding_sha256=38833ef76d248a6b55c1a09d460939781c30e081a2d7bbd27ed47aa7d9ed12ee` remain unchanged. The pre-existing offline persistent cache is intended to be preserved.

This staging extension adds **seven narrowly guarded visual presentation cases** in Tome 34 only, without overwriting semantic attribution or real standalone interventions of Marie. It additionally corrects stale `version.json` descriptive totals to 205 assets / 119244276 bytes, and synchronizes app/SW/offline/package identities to public candidate version 142.38.

**Critical limitation:** the full local R237 corrective adapter (28 paragraphs, 21 boundaries, T23 and T30 controls) resides in an earlier nondeployable ZIP and **is NOT included** here. This branch is an application-only integration *staging substrate*, not the full R237 corrected release. Preserve the sole R237 correction program, integrate the original adapter and the seven-case additions before any candidate qualification. No App Test/MAIN deployment authority is implied.

**Required gates:** full Reader render, CSS & Repères, historical selection/anchors/highlight persistence, IndexedDB migration and backup/restore, offline/SW update compatibility, iPhone/iPad Safari, independent package-integrity reopen, and distinct user GO.

## Independent follow-up audit and local repair (2026-10-16)
The first published development commit passed exact semantic/color tests but revealed an untested **visible-guillemet regression**: five of the seven adjusted paragraphs (T34 E0016 P009; E0018 P019; E0019 P010/P012/P018) had an embedded *closing* French quotation mark hidden by the inherited outer-dialogue CSS/renderer. In two other passages (E0019 P011/P014) the internal closing marks remained visible. A bounded pre-index derived-DOM repair now restores only the five confirmed nested closers; no canonical text bytes or user offsets change. Negative controls include real standalone Mary speech, tampered paragraph text, and slices.

The package inventory was also normalized to inherited **codepoint lexical order** after the initial development commit accidentally applied locale-sensitive ordering, which remained hash-consistent but violated established deterministic serialization.

**Release status remains HOLD.** This branch is still a seven-paragraph limited visual pilot, not the full R237 28-paragraph/21-boundary reader fix. No full browser, WebKit, offline activation, IDB upgrade, long-text selection or backup/restore success is asserted.
