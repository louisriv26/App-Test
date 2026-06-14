# Stage 6R — validated corpus patch report

Final status: LIMITED_PASS_STATIC

## Scope
Applied only user-validated Stage 6Q decisions and exact tracked-change mappings. The broad Stage 6Q safe-tidy candidate batch was not applied globally because preflight found French-typography-risk candidates; it is deferred pending a stricter filter.

## Corpus changes
- Exact mapped tracked-change rows applied: 10
- A1/A2 corrected mappings verified: 2
- Controlled paragraph splits inserted: 2 new paragraph IDs (`PASSION24.HOUR.20.P027B`, `PASSION24.HOUR.20.P017B`)
- User-validated formatting actions applied/preserved: 30 rows
- Corpus fingerprint before: 67f9ec5829ec8963c3f106f7ae9272f272d0723dab3cc292962ca5136d6ee324
- Corpus fingerprint after: 77b6aa8db9d38df29ac3e45328c4d8431f70d5cfb57c966f68b1f33b9a9384b3

## Runtime preservation
App logic, highlighting logic, linked text mappings, internal subheaders, and PWA runtime behaviour are preserved. Service worker cache name and version metadata were updated only so the corpus update can be detected/cached.

## Counts
Before: `{"hours": 24, "meditation_paragraphs": 1038, "reflection_paragraphs": 183, "subsection_paragraphs": 65, "prayers": 5, "prayer_paragraphs": 46, "sections": 4, "section_paragraphs": 178, "all_corpus_t_paragraphs": 1510}`

After: `{"hours": 24, "meditation_paragraphs": 1040, "reflection_paragraphs": 183, "subsection_paragraphs": 65, "prayers": 5, "prayer_paragraphs": 46, "sections": 4, "section_paragraphs": 178, "all_corpus_t_paragraphs": 1512}`

## Speech validation
- total speech segments: 368
- missing speech targets: 0
- invalid speech offsets: 0
- overlapping speech segments: 0

## Real device status
NOT_TESTED. This package is not a public-release PASS.
