# M1 blind semantic-layer qualification

The first blind freeze was created before current speaker/presentation metadata was revealed and is preserved byte-for-byte as `BLIND_FREEZE_MANIFEST_ORIGINAL_FIRST_FREEZE.json`.

During post-freeze closure, raw reporter clauses exposed a material precision problem in the provisional semantic classifier: multiple quotations explicitly introduced by raw phrases such as “Jésus me dit :” had been labelled `DIRECT_LUISA`, `DIRECT_OTHER` or `AMBIGUOUS_HOLD`. This is a defect in the audit classifier, not evidence of an app defect.

Consequences and containment:

- the original blind evidence is not silently rewritten;
- no proposed mutation depends solely on a disputed blind semantic label;
- nested presentation-parent holes are detected structurally against the inherited v101.119 presentation invariant;
- explicit missing divine speech is independently detected from raw reporter text;
- unquoted reporter cases were separately scanned;
- Cycle 2 re-scans current raw/projection structure without consuming the disputed blind semantic classifications;
- Cycle 2 reproduces all four candidate loci and finds zero new candidate IDs.

This qualification must remain attached to the M1 evidence package.
