# Build script vs files audit — v101.123

**PASS**

- Immutable v101.122 baseline SHA-256 `039f7ad95bced983b5deb1613bacb92ababf75e2a162462b4389a3a028bf8565` is the verified functional baseline.
- The current builder reconstructs the **entire current package tree**, not only runtime files, from the immutable baseline plus the package-contained overlay manifest.
- Exact tree equality and current hash-manifest reconciliation are mandatory build-script gates.
- v101.123 functional HTML differs from v101.122 only by release identity/build comment after normalisation.
- Protected declarations: 14/14 byte-identical to v101.122.
- `showHelp()` block: byte-identical to v101.122.
- Current audit tooling contains no transient `/mnt/data/v101122_run/` or `/mnt/data/v101123_run/` dependency.
