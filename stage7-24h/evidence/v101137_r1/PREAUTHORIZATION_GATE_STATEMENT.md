# FINAL AUTHORIZATION STATEMENT — USER GATE

**No authorization has yet been given. No app mutation has been performed.**

To authorize the next bounded mutation stage, the authorization must bind to all of the following exact authorities:

- Immutable French v101.136 R5 baseline SHA-256: `7ef830738ff5665ae5b880d52bde029e4b9ba092d834f81b008d24615e1ab9e7`
- Italian R3 authority SHA-256: `bab1e4de16137577c9a100127509ff307b0532f13ad545bb9b6a61e7141041b8`
- Frozen R4 authority SHA-256: `2534e383966d60b462c81ab3a48143a916b2141cdc732fca9450e26b9157afe6`
- Frozen R4 ledger SHA-256: `ca07f0e7877d19d93c5e716b5aed1114f3d14be59e9d32ccca5e15d34255e68f`
- **Final authorization-ready ledger CSV SHA-256: `f9a9c4c74df33b3f96909e3611acb74c448deed5fa367fa86072d2e27cbfef49`**
- Final ledger JSON mirror SHA-256: `f7d6c3bd5ca9880a0db4f290242015bd1f4a38e8edc139c02e14852d9813c370`
- Final row count: **79**
- Final status count: **55 ACCEPT_FOR_AUTHORIZATION + 24 PRESERVE_MOVE**
- Final operation count: **41 REPLACE_RECORD + 12 TRIM_RECORD + 24 MOVE_OUT_OF_CANONICAL_LAYER + 2 DELETE_FROM_CANONICAL_LAYER**

The exact bounded R4→final delta is five rows only: C0025, C0050, C0066, C0068 and C0093.

## Authorization wording

If the user decides to proceed, an unambiguous authorization is:

> I authorize the exact 79-row mutation universe in `FINAL_AUTHORIZATION_READY_LEDGER.csv`, SHA-256 `f9a9c4c74df33b3f96909e3611acb74c448deed5fa367fa86072d2e27cbfef49`, and no other textual mutation, starting only from the immutable v101.136 R5 baseline SHA-256 `7ef830738ff5665ae5b880d52bde029e4b9ba092d834f81b008d24615e1ab9e7`. Preserve all `PRESERVE_MOVE` material outside the canonical layer; leave all deferred/recension-sensitive loci unchanged; do not synthesize H23 Forms A and B; do not move the H24 burial/deposition block; keep the Desolation of Mary within H24 meditation scope.

Authorization of this exact ledger does **not** authorize any unlisted app, corpus, associated Livre du Ciel, UI, metadata or recension change except the minimum version/cache/build metadata necessarily required to produce the successor build.
