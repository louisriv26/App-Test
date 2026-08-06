# Luisa — 24 Heures de la Passion

Version: `v101.53` — **staging / test build. NOT authorised for production.**

App SHA-256: `25715fca859d67c473c0645edadc3621b982118e3cbfce729ff1138acf55aab6` (1,783,611 bytes). `index.html` and `luisa_24_heures.html` are byte-identical replicas. Service-worker cache: `luisa-24h-v101-53`.

**Production is at v101.51** (promoted 3 August 2026). This build carries the approved targeted corpus change set on top of it.

> ## What v101.53 fixes — the bottom bar covering the end of a view on iPad
>
> **Reported by Louis on iPad, Approfondir screen:** the bottom navigation partly hid the text of the
> last card and it could not be scrolled any further.
>
> **Cause: an iOS Safari flex bug, not missing padding.** `html.ios-device .content` is a flex column
> with `overflow-y: auto`, and iOS Safari **excludes such a container's `padding-bottom` from its
> scrollable overflow**. The app does reserve 84–104px for the bar, and Chrome honours it — but on
> device that reservation evaporated, so the last card sat flush against the viewport bottom with the
> bar on top of it and nothing left to scroll. That is why this only ever appeared on iPad.
>
> **Fix:** on iOS the padding is zeroed and the space is reserved by a `#content::after` flex-item
> spacer instead. A flex item is laid out in flow and is always counted in scrollable overflow, in
> every engine, so the reservation cannot be dropped. Zeroing the padding guarantees the two never
> add up to a double gap.
>
> Measured in a browser with the iPad runtime class applied and the Approfondir view open: scroll
> range **146px → 177px**, and the last card ends **53px clear** of the bar instead of underneath it.
>
> Corpus untouched: still byte-identical to the v101.52 contract.
>
> **Honest limitation:** the underlying Safari behaviour cannot be reproduced in desktop Chrome, so
> what is verified here is that the spacer reserves reachable space and that nothing double-spaces.
> That the symptom is gone needs confirming on your iPad.

> ## What v101.52 is — the approved targeted corpus change set
>
> **This is the first release since v101.44 in which the corpus itself changes.** Everything from
> v101.45 to v101.51 was app-only, gated on the corpus being byte-identical. That gate is
> deliberately re-baselined here, not dropped — see below.
>
> **Part A — 21 mandatory wording corrections.** All 21 targets located, all 21 required correcting
> (`CHANGED = 21, ALREADY_PRESENT = 0, UNMAPPED = 0`). Applied as minimal clause-level edits, never
> whole-paragraph overwrites, each asserted to occur exactly once in its own record and exactly once
> in the whole file. Measured against the untouched production copy: **exactly 21 of 1,839 records
> changed, 0 unrelated**, record-ID set identical.
>
> **Part C — 65 non-destructive display segmentations, 180 display units.** Canonical ids, order and
> text are untouched; each record's segment slices concatenate back to its canonical text exactly.
> Units are rendered through the app's existing `renderParaTextRange()` in **canonical coordinates**,
> which already maps highlights, speech spans, visual breaks and quote suppression — so notes,
> highlights, favourites and saved positions keep resolving through the canonical parent id with no
> migration. Verified in-browser: 65/65 unit counts, 65/65 exact concatenation, 65/65 canonical DOM
> text length, 0 duplicate DOM ids, and a highlight deliberately straddling a segment boundary
> (250–300 across the 269 boundary) renders as two pieces that reassemble to the exact canonical
> slice with status `ok`.
>
> **Part E — 4 cross-record continuity operations.** D03 and D04 already read continuously once Part
> A landed. D01 and D02 additionally needed the small text adjustments the instruction prescribes for
> them. Both stable ids are preserved in every group; the join is presentational plus copy, so
> copying either member yields the whole grammatical unit.
>
> **Part F — the 3 excluded stylistic rows are untouched**, all three still carrying
> `Elle est si grande…`.
>
> **Speech offsets were recalculated, not guessed.** Ten of the 21 corrected records carry speech
> ranges; offsets shift by the exact replacement delta, and a boundary falling *inside* a replaced
> span is refused outright rather than approximated — none did. 7 entries changed, 3 correctly
> unchanged, 0 added or removed.
>
> **Independent corroboration.** The segment boundaries computed from the authorised anchors match
> the instruction's own "historical implementation context" offsets exactly for four of the five
> speech-sensitive records. The fifth, `08.P015`, computes 146|484|620 against a historical
> 146|485|621 — off by exactly −1 on the last two, which is precisely the delta of A16's comma
> removal at char 249. The change set validates itself.
>
> **Protected-declaration contract re-baselined.** `CORPUS` and `SPEECH_DATA` change by design, so
> the v101.44 contract that gated v101.45–v101.51 can no longer hold. It is superseded by
> `L24H_v10152_Protected_Declaration_Hash_Contract.json`, which records that exactly those two
> declarations moved and that `TEXT_LIBRARY`, `HOUR_LINKED_TEXTS`, `INTERNAL_SUBHEADINGS` and
> `SPEECH_END_VISUAL_BREAKS` are unchanged. The gate keeps working for every later release.

> ## What v101.51 fixed — highlights that existed but were never shown
>
> **Reported by Louis:** a highlight made in "Prière avant chaque Heure" never appeared in Mon Espace.
>
> The record was fine. It saved correctly, resolved correctly through `getTargetInfo()` as
> `Prière — Prière avant chaque Heure`, and was not stale. It was simply **never rendered**: the
> highlight list was sorted by passage label and then cut to the first 8 entries. Labels beginning
> with a letter — `Prière — …`, `Complément — …` — sort after every `Ne Heure` label, so a prayer
> highlight always landed at the end of the list. Measured on Louis's real data it sat **35th of 39
> groups**, so it was structurally unreachable. This was never specific to his device or his data:
> *no* prayer or complement highlight could ever be seen by anyone with more than a handful of marks.
>
> The same cap was silently hiding **31 of his 39 highlight groups**, with nothing on screen to
> suggest anything was missing. Two further prayer highlights already in his live export —
> "Prière de remerciement pour l'Heure Sainte" and "Prière à la fin de chaque Heure" — had therefore
> never been visible to him either.
>
> **Fix, two parts:**
> 1. **Order by recency, not by label.** Newest first, which is what the notes list already did and
>    what you want when looking for the highlight you just made.
> 2. **The cap is now a preview, not a ceiling.** A "Voir mes N surlignages" button expands to the
>    full list and collapses again. Notes had the identical silent cap and got the identical
>    treatment. Stale entries still come first, since those are the ones needing action.
>
> Verified against Louis's real 56-highlight export plus one added prayer highlight: the prayer went
> from invisible to 4th in the list (the three above it are his stale entries, deliberately first);
> the expander goes 11 cards → 39 → 11; 11 seeded notes preview 8 newest-first and expand to 11,
> persisted through `persistPersonalSnapshot`; 0 console errors.

> ## What v101.50 fixes — the iPhone note panel and the sideways scroll
>
> **Reported by Louis on iPhone against v101.49:** opening a note showed a panel slightly wider than
> the screen, and after closing it the whole app stayed pannable sideways.
>
> **Cause: iOS Safari auto-zoom, not a layout overflow.** iOS zooms the page in whenever a text field
> with a font smaller than 16px receives focus — and it never zooms back out. The layout viewport
> then stays wider than the visual viewport, so the page pans horizontally and a `position:fixed`
> panel reads as wider than the screen. `.note-textarea` was `0.9rem` (14.4px) and the Approfondir
> section search was `0.95rem` (15.2px). `.search-input` was already 16px, which is exactly why
> searching never triggered this and only the note panel did.
>
> This was verified *not* to be an overflow: at 390×844 in desktop Chrome, with the `html`/`body`
> `overflow-x: hidden` masking removed, `scrollWidth` equalled `innerWidth` on the home screen, in
> the reader, with the note modal open, and after closing it — zero overflowing elements outside
> intentional horizontal scrollers.
>
> **Fix:** both fields raised to `1rem` (16px). The viewport meta deliberately carries no
> `maximum-scale` or `user-scalable`, so pinch-zoom stays available; suppressing zoom would have
> hidden the symptom at the cost of a real accessibility regression.
>
> **Guard added:** the build and the reopened-ZIP gate now parse the shipped stylesheet (with CSS
> comments stripped, so a comment above a rule is not mistaken for its selector) and fail if any
> text-entry selector declares a font under 16px. This cannot be reintroduced silently.
>
> **Honest limitation:** iOS focus-zoom cannot be reproduced in desktop Chrome. The mechanism and the
> font sizes are verified, and the note panel now measures exactly 0–390px with 0px overflow, but
> that the *symptom* is gone needs confirming on a real iPhone.

> ## What v101.49 added — Note on the text-selection bar
>
> **Reported by Louis:** selecting part of a passage still offered only Surligner, Copier and Fermer.
> He was right, and v101.47's claim that "notes now work on mobile" was too broad.
>
> There are **two** distinct mobile action bars, and v101.47 only fixed one of them:
>
> | Bar | Raised by | Buttons before v101.49 |
> |---|---|---|
> | `#mobileActionBar` | long-pressing a paragraph | Surligner · Copier · **Note** · Fermer |
> | `#selectionActionBar` | **selecting text** | Surligner · Copier · Fermer |
>
> So the most natural way to annotate a passage — select the words you want to write about — had no
> route to a note at all. The bar's own stylesheet has declared
> `grid-template-columns: repeat(4, minmax(0, 1fr))` since it was written, for three buttons: the
> fourth slot existed and had simply never been filled.
>
> **Fix:** the selection bar now reads **Surligner · Copier · Note · Fermer**. The note attaches to
> the paragraph containing the selection, matching what long-press already did. The paragraph id is
> read *before* the bar closes, because closing it clears the pending selection.
>
> Verified at 375×812 on two different Hours: a real text selection raised the bar with four buttons
> (77.5px per column, no overflow), Note opened the modal titled for the correct Hour, the note saved
> to the canonical snapshot, survived a reload, showed its ✎ indicator beside the paragraph and was
> listed in Mon Espace. The long-press bar was re-checked for regression and still carries Note.
>
> **Also corrected: provenance comments.** The inherited build script bumps versions with a blanket
> string replace, which had been silently rewriting historical `/* v101.NN: … */` comments to the
> current version on every release — so v101.48's explanatory comments claimed to be v101.49, and
> v101.47's claimed the same. Each comment I could attribute has been restored to its true version,
> and the reopened-ZIP gate now asserts on identity sites only, so genuine history survives the bump.

> ## What v101.48 added — highlights stop silently disappearing
>
> **Reported symptom:** Mon Espace listed highlights that were no longer in the text, with no way to
> remove them. The underlying problem was larger than the listing.
>
> A highlight is anchored to three things at once: the paragraph id, character offsets, and a
> `text_hash` of the whole paragraph. Editorial work invalidates all three. Change a single
> character anywhere in a paragraph and its hash no longer matches, so the highlight is **not drawn
> at all** — silently, with no message. Merge a paragraph away and the record becomes unreachable,
> leaving exactly the un-removable Mon Espace entry that was reported.
>
> **Measured on a real 56-highlight export from the live v101.25 app:** 48 of 56 still render on
> production today; on the new corpus that falls to **38**, because the accumulated R3A/R3B
> corrections touched paragraphs that carried highlights. Nothing was corrupt — the text was still
> there. Only the anchor could no longer see it.
>
> **Recovery, on load.** Each stale record's stored passage text is located in the current corpus
> using a normalised comparison (NFC, narrow/no-break spaces folded, typographic apostrophes
> folded, punctuation and case ignored, whitespace collapsed and trimmed), and re-anchored — but
> **only when the location is unambiguous**: either the whole passage occurs exactly once, or, for
> long passages whose middle was edited, both of its ends do, with a length sanity check. A
> multi-paragraph selection whose target disappeared is moved to a surviving sibling *of the same
> selection only*, never anywhere else in the corpus. Ambiguous or short matches are refused rather
> than guessed, because silently moving a highlight onto the wrong passage is worse than leaving it
> stale. **Nothing is ever deleted automatically.**
>
> **Result: 53 of 56.** 13 re-anchored in place, 2 moved to a sibling. The 3 remaining are listed in
> Mon Espace with a plain explanation and a working **✕ Retirer** button — and **2 of those 3
> already fail to render on production v101.25**, because their stored text predates earlier corpus
> corrections. So no highlight is worse off than it is today.
>
> **Two further fixes found while testing this.** Mon Espace shows at most 8 highlights, ordered by
> passage label — so 2 of the 3 stale entries fell outside the visible list and their Remove buttons
> could never be pressed. Stale entries are now listed first, ahead of that cap. And the matcher's
> own normaliser left a trailing space when a passage ended in a narrow no-break space before a
> closing guillemet, which blocked two otherwise-perfect matches.
>
> Verified end-to-end in a browser against a seeded v101.25 install (canonical snapshot at schema 4,
> R41 anchor-reset marker present): schema migrated 4→5, 53/56 renderable, every recovered span
> re-checked independently, and the Retirer button exercised (56→55 records, persisted, view
> refreshed).

> ## What v101.47 added — notes finally work on phone and tablet
>
> **Notes were impossible to create on a touch device.** Not hard to find — absent. Three
> independent rules each blocked the only note button: `.para-actions` is `display:none` under
> `max-width:768px`, it is additionally gated behind `.mode-etude` (study mode), and it is revealed
> by `:hover`, which touch devices do not have. The fallback `✎` dot is `display:none` unless the
> paragraph *already* has a note, so it could never create the first one. The long-press action bar
> — the only remaining mobile route — offered Surligner, Copier and Fermer, with no note entry.
>
> **This was not a regression.** Production v101.25 behaves identically. Notes have never been
> reachable on a phone or tablet.
>
> **Fix:** the long-press bar now reads **Surligner · Copier · Note · Fermer**. Long-press any
> paragraph, tap **Note**, write. It works in Prier mode as well as Étudier, deliberately: that bar
> has always been mode-agnostic, and highlighting — the *more* intrusive act, since it marks the
> sacred text itself — was already offered there. A note changes nothing about how the passage
> reads. Personal devotional response is not study apparatus.
>
> **The help text was also wrong,** and actively misleading: it told users to enable study marks and
> look for a per-paragraph `✎` button that never appears on mobile. Both affected help rows now
> describe the phone/tablet route and the desktop route separately.
>
> Verified at a 375×812 viewport: long-press → bar shows Note → modal opens → note saved →
> persisted to the canonical snapshot → survived a reload → indicator dot appeared. Confirmed in
> both Prier and Étudier modes, and desktop behaviour is unchanged.

## Corpus status — frozen and complete

The corpus is frozen at the **v101.44** content and carried into v101.45 **byte-identical**: all six protected declarations (`CORPUS`, `TEXT_LIBRARY`, `HOUR_LINKED_TEXTS`, `SPEECH_DATA`, `INTERNAL_SUBHEADINGS`, `SPEECH_END_VISUAL_BREAKS`) verified against the v101.44 hash contract, twice — once in the work tree and again from the reopened package.

It contains the full accumulated editorial line:

- **R3A** — 48 text operations across 44 paragraphs (reverence capitalisation per the documented referent policy, grammar/agreement/punctuation fixes, and 9 substantive editorial items individually approved by Louis).
- **R3B — complete, all 24 Hours.** 24 operations across 23 records; 13 Hours corrected, 11 with no substantive change; every Hour `SOURCE_CONTENT_RECONCILED`, none pending. Reconciled against **both** complete Italian witnesses (`IT_COMPLETE_364` and `IT_REFLECTIONS_174`) plus the English witness.
- **v101.40–v101.42** — full-text convergence across every `TEXT_LIBRARY.body` record and all active textual layers; 94/94 Book-of-Heaven extracts reconciled.
- **v101.43–v101.44** — two independent blind adversarial revalidation passes.

Independently reproduced at takeover: 24 Hours, 5 prayers, 4 sections, 40 library objects, 2,735 body records, 381 speech segments, 30 internal subheadings, 94 extracts, 4,501 runtime-addressable DOM targets, 0 duplicate paragraph IDs.

> **Correction to earlier versions of this file.** Every README up to v101.32 carried the line *"R3B reflection completeness is not certified — the supplied Italian edition does not contain the complete Riflessioni e Pratiche."* **That statement is obsolete and was wrong to carry forward.** It described the *initial* Stage S0 attempt, which halted before any modification because the complete Italian binaries were not then available. Once they were supplied, Stage S0 was rerun and R3B was completed at v101.37. The witness in question — `IT_Luisa_Piccarreta_Le_24_Ore_complete_con_Riflessioni_e_Pratiche.pdf`, SHA-256 `7af33d29854078366a4cb0fabafb8b547370faef20997178c91e2bbe84f3d671` — was bound and used in that process. The stale line caused a closed question to be reopened in error during the v101.45 takeover; supersession markers have now been added to the two v101.26-era decision documents that carried it.

## What's new in v101.45 — one fix

**Service-worker update flow (FINDING-01).** Pressing "Actualiser" could complete and leave the client still running the **old** version — permanently, not just for one reload. Reproduced end-to-end, then fixed.

`sw.js`'s install handler precached with `cache.addAll(ASSETS)`, whose fetches consult the browser's HTTP cache. A newly installing worker could therefore pull the *previous* version's files out of the HTTP cache and store them into its *own new* cache. The cache name flipped to the new version while its contents were still the old build; because the fetch handler is cache-first with `{ignoreSearch: true}`, the `?lp_force_reload=` parameter could not escape it. Fixed with:

```js
await cache.addAll(ASSETS.map(u => new Request(u, { cache: 'reload' })));
```

This is the defect behind the reported iOS symptom ("it actualises but stays on the old version", surviving a hard close on iPhone and iPad) and why deleting the home-screen icon and re-adding from Safari was the only reliable remedy — that clears both the service-worker registration and the origin's HTTP cache.

Trade-off accepted: `addAll` is all-or-nothing, so an update now needs real network at install time. If it fails, the old worker keeps serving and the app stays usable — the update simply waits.

## Everything carried forward from v101.26–v101.44

- **Canonical personal-state persistence.** `state.lastHour` is the single live source for the resume Hour; `applyPersonalSnapshot()` is a pure in-memory apply; `openHour`, study mode and cycle reset commit through the canonical snapshot. Fixes the last-opened Hour being forgotten, study mode reverting, and a completed reset resurrecting the old resume Hour.
- **Speech punctuation (P2-COLON).** The introducing colon and its adjacent spaces are no longer deleted from rendered text; 99 paragraphs across 22 Hours plus the Approfondir section restored.
- **Meditated-hour boxes.** 2px border in both themes on the home grid *and* the Heures list, so thickness consistently means "meditated"; completion tick darkened and enlarged.
- **Dark-mode accessibility.** The "· Heure Sainte" label was 2.18:1 against the dark card (WCAG AA needs 4.5:1); now 6.32:1.
- **Theme option** reads "Automatique" rather than "Système".
- **Compléments cleanup.** "Les trois Heures de Gethsémani" shows only its genuine "Règle spéciale" sentence.

## What to test on device

**Read this first — a single-stage test will not test the update fix.**

Because a client already pinned by the old bug can be served the *old* `sw.js` from its HTTP cache, installing this build on a device that already has an older one requires deleting the icon and re-adding from Safari — and **that step bypasses the update path entirely**. So:

- **Stage 1 — install. DONE** on iPhone and iPad (2026-07-31). Icon deleted, v101.45 confirmed in Safari, re-added to Home Screen. The app then offered Actualiser and the update succeeded — an encouraging real-device signal, because the *incoming* worker’s install code is what runs, and v101.45 carries the fix.
- **Stage 2 — the update-flow test.** From the previously installed build, press **Actualiser** once; it must land on v101.53 immediately. Do it on both iPhone and iPad — each home-screen icon has its own storage partition.

Then, in order of risk:

1. **Resume Hour is remembered.** Open an Hour, read a little, close the app completely, reopen. Home should offer "Reprendre la lecture" pointing at that Hour.
2. **Study mode sticks.** Toggle the `#` button on, close completely, reopen — still on.
3. **Reset stays reset.** With progress recorded, use "Réinitialiser ma progression" and confirm. Close completely, reopen. There must be **no** "Reprendre la lecture" card.
4. **Speech punctuation.** Hour 20 should read `La première Parole : Père, pardonne-leur car ils ne savent pas ce qu'ils font !` — colon present, spaces either side, no guillemets. Hours 8, 17, 19, 21, 22 have the most instances.
5. **Upgrade with real data.** On a device holding real notes, highlights and progress, confirm nothing is lost. Highest-risk untested path.
6. **Dark mode.** "· Heure Sainte" on Hours 5–7 in the Heures list must be readable.
7. **Notes (new — please test).** Long-press a paragraph → **Note** → write → save. Confirm it survives a full close and reopen, that a small ✎ appears beside that paragraph afterwards, and that it is listed in **Mon Espace**. Then highlights/progress survive a reopen; export–import round-trip; offline launch after first load.
8. **Highlights after upgrade (new — please test).** This matters most on a device that already
   holds real highlights. Open **Mon Espace** and confirm your highlights are still listed and still
   open to the right passage. Any that could not be recovered appear first, with a "⚠ le texte de ce
   passage a changé" note and a **✕ Retirer** button — pressing it must remove that entry and keep it
   removed after a full close and reopen.
9. **Notes from a text selection (new — please test).** Select part of a paragraph with your
   finger. The bar must read **Surligner · Copier · Note · Fermer**. Tap **Note**, write, save, and
   confirm it survives a full close and reopen. Test the long-press route too — both should work.
10. **iPhone zoom/pan (new — the reason for this build).** Open a note, type something, close the
    panel. The app must NOT be left zoomed in or scrollable sideways. Then do the same in
    **Approfondir** → section search box. Both were sub-16px fonts and both should now leave the
    layout exactly as it was.
11. **Mon Espace shows everything (new).** Highlight something in **Prières & compléments** and
    confirm it appears in Mon Espace — it should be at or near the top, since the list is now
    newest-first. Then press **Voir mes N surlignages** and confirm the full list opens and collapses
    again. Same for notes.
12. General reading, search including the Réflexions filter, Hour 24 burial + Désolation structure.

## Known limits — not defects

- **Real-device QA is `NOT_TESTED`.** That is the remaining release blocker and the purpose of this build.
- **The update fix is verified on desktop Chrome only**, on a real HTTP origin with a genuine before/after reproduction. It is *not* yet verified on an installed iOS PWA, where storage partitioning differs. Stage 2 above is what closes that gap.
- **Deliberately deferred:** storage-full / storage-unavailable recovery, malformed or future-snapshot recovery, atomic R41 highlight-anchor reset, and honest "not saved" messaging across all mutation paths. If a save fails because storage is full, the app may still report success.
- **`stored_text_units = 4577`** is a hardcoded literal in the v101.44 build script and does not reconcile with an independent recount (4,574 / 4,579). Corpus integrity is unaffected — the declarations hash-match — but that figure is unverified.
- **The stray bare LF** at offset 959303, carried unchanged since the v101.44 baseline, was incidentally normalised to CRLF while editing v101.47. It sat outside all protected declarations, all six of which still hash-match the v101.44 contract, so the corpus is unaffected. The file is now uniformly CRLF (0 bare LF).
- **Android Play Protect** "compatibility too low" on a browser-minted WebAPK: one unreproduced report, deprioritised.

## Verification completed

```text
Input binding (FP2 baseline)   PASS   both ZIPs exact on bytes + members + SHA-256
Package integrity              PASS   760/760 manifest records, 0 missing, 0 mismatch, 0 unaccounted
Protected declarations         PASS   6/6 byte-identical to the v101.44 contract (verified twice)
Replica parity                 PASS   app == deploy/luisa == deploy/index
Packaged suites                6/9    3 suites could not run here - see below
Reopened-ZIP gate              PASS   41/41 checks incl. 75/75 manifest records
Live HTTP load                 PASS   0 console errors on a served origin
SW registration + activation   PASS   cache luisa-24h-v101-53
iPad bottom-bar clearance      PASS   scroll range 146->177px, last card 53px clear of the bar
Wording corrections            PASS   21/21 CHANGED, 0 unrelated records touched
Display segmentations          PASS   65/65 records, 180 units, concatenation exact
Continuity operations          PASS   4/4, both stable ids preserved in each group
Excluded stylistic rows        PASS   0/3 changed
Highlight across a boundary    PASS   reassembles to the exact canonical slice
Mon Espace reachability        PASS   prayer highlight now 4th, not 35th; 11 -> 39 -> 11 on expand
Text-entry fonts (iOS zoom)    PASS   note textarea, section search and search input all >= 16px
Layout overflow at 390x844     PASS   0px, masking removed, incl. note modal open and after close
Highlight recovery             PASS   53/56 on a real v101.25 export (was 38/56 unrecovered)
Stale-entry removal            PASS   Retirer removed 1 of 3 and persisted (56 -> 55)
Selection-bar Note             PASS   4 buttons at 375px; note saved, reloaded, listed in Mon Espace
Long-press Note (regression)   PASS   still Surligner/Copier/Note/Fermer
DOM target sweep               PASS   4501/4501, 0 missing, 0 page errors
Offline cold start             PASS   booted and rendered with the HTTP server stopped
Update flow (before)           FAIL   reproduced on v101.44 — pinned to old version
Update flow (after)            PASS   single Actualiser press landed on the successor
Real-device QA                 NOT_TESTED
```

Three packaged suites could not be executed in this environment and were **not** silently counted as
passing: `test_v10144_syntax_and_json.py` and `test_v10144_service_worker_contract.py` both shell out
to `node --check`, and `test_v10144_persistence_runtime.py` needs `playwright`; neither Node nor
Playwright is installed here. In their place the same properties were established against a real
browser on a served origin, which is a stronger check for this build than a static parse: the app and
`sw.js` were both parsed, executed and activated (cache `luisa-24h-v101-53`), and persistence was
driven directly — schema 4→5 migration, recovery written back to the canonical snapshot, and a
highlight removal that survived. `manifest.json` and `version.json` were validated as JSON
separately. The gap is recorded in `L24H_v10153_Decision_Lock.json`.
