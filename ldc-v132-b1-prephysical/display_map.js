/* ============================================================================
   LDC R1B — structural-dash display projection (handoff RECHECKED v2)
   ----------------------------------------------------------------------------
   The canonical paragraph string is never edited. This module projects it into
   display atoms, each of which carries the canonical [cs,ce) range it came from,
   so highlights, notes, bookmarks and speaker offsets keep working across
   suppressed and expanded tokens.

     projectParagraph(text, ops) -> { atoms, display, ok, errors }

   atom.kind:
     'canonical'  verbatim canonical run           (text === canonical slice)
     'suppressed' source-layout marker, zero width (text === '')
     'replaced'   exact display replacement        (text !== canonical slice)

   Operations come from LDC_R1B_runtime_display_transform_map_v2.json via
   corpus/display_NN.json. No regex ever makes an editorial punctuation
   decision here — the map is the sole authority.
   ========================================================================== */
(function (root) {
  'use strict';

  function projectParagraph(text, ops) {
    var errors = [];
    ops = (ops || []).slice().sort(function (a, b) { return a.s - b.s || a.e - b.e; });

    // validate: in-bounds, non-overlapping, exact source slice
    var prevEnd = -1;
    for (var i = 0; i < ops.length; i++) {
      var o = ops[i];
      if (!(o.s >= 0 && o.s <= o.e && o.e <= text.length)) {
        errors.push({ code: 'RANGE', decision_id: o.d, s: o.s, e: o.e, len: text.length });
        continue;
      }
      if (o.s < prevEnd) errors.push({ code: 'OVERLAP', decision_id: o.d });
      if (text.slice(o.s, o.e) !== o.t) {
        errors.push({ code: 'BASELINE_MISMATCH', decision_id: o.d,
                      expected: o.t, got: text.slice(o.s, o.e) });
      }
      prevEnd = o.e;
    }
    if (errors.length) {
      // fail safe: show canonical text untouched rather than a wrong projection
      return { ok: false, errors: errors,
               atoms: [{ cs: 0, ce: text.length, text: text, kind: 'canonical' }],
               display: text };
    }

    var atoms = [], cur = 0, display = '';
    for (var j = 0; j < ops.length; j++) {
      var op = ops[j];
      if (op.s > cur) {
        atoms.push({ cs: cur, ce: op.s, text: text.slice(cur, op.s), kind: 'canonical' });
      }
      atoms.push({ cs: op.s, ce: op.e, text: op.r,
                   kind: op.r === '' ? 'suppressed' : 'replaced',
                   src: op.t, action: op.a, decision_id: op.d, pair_id: op.p || '' });
      cur = op.e;
    }
    if (cur < text.length) {
      atoms.push({ cs: cur, ce: text.length, text: text.slice(cur), kind: 'canonical' });
    }
    for (var k = 0; k < atoms.length; k++) display += atoms[k].text;
    return { ok: true, errors: [], atoms: atoms, display: display };
  }

  /* -- canonical <-> display coordinate mapping ---------------------------- */
  // Canonical offset -> display offset. A canonical position inside a suppressed
  // or replaced token collapses to that token's display start, which keeps
  // selections and stored anchors resolvable.
  function canonicalToDisplay(atoms, canOffset) {
    var d = 0;
    for (var i = 0; i < atoms.length; i++) {
      var a = atoms[i];
      if (canOffset >= a.ce) { d += a.text.length; continue; }
      if (canOffset <= a.cs) return d;
      return a.kind === 'canonical' ? d + (canOffset - a.cs) : d;
    }
    return d;
  }

  // Display offset -> canonical offset.
  function displayToCanonical(atoms, dispOffset) {
    var d = 0;
    for (var i = 0; i < atoms.length; i++) {
      var a = atoms[i], len = a.text.length;
      if (dispOffset > d + len) { d += len; continue; }
      var within = dispOffset - d;
      if (a.kind === 'canonical') return a.cs + within;
      return within >= len ? a.ce : a.cs;   // inside an expanded/suppressed token
    }
    return atoms.length ? atoms[atoms.length - 1].ce : 0;
  }

  // Atoms overlapping a canonical range, clipped to it. Used to render one
  // speech run without letting a display token leak into a neighbouring run.
  function atomsForRange(atoms, start, end) {
    var out = [];
    for (var i = 0; i < atoms.length; i++) {
      var a = atoms[i];
      if (a.ce <= start || a.cs >= end) continue;
      if (a.kind === 'canonical') {
        var s = Math.max(a.cs, start), e = Math.min(a.ce, end);
        out.push({ cs: s, ce: e, text: a.text.slice(s - a.cs, e - a.cs), kind: 'canonical' });
      } else {
        if (a.cs < start || a.ce > end) {
          // guaranteed not to happen: no mapped operation straddles a speaker
          // segment boundary (verified corpus-wide), and run edges are segment
          // edges. Kept as a hard guard rather than a silent partial render.
          out.push({ cs: a.cs, ce: a.ce, text: a.text, kind: a.kind, src: a.src,
                     straddles: true, decision_id: a.decision_id });
        } else {
          out.push(a);
        }
      }
    }
    return out;
  }

  root.LDCDisplayMap = {
    projectParagraph: projectParagraph,
    canonicalToDisplay: canonicalToDisplay,
    displayToCanonical: displayToCanonical,
    atomsForRange: atomsForRange
  };
})(typeof window !== 'undefined' ? window : globalThis);
