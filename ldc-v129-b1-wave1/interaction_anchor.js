/* ============================================================================
   LDC R1B — canonical interaction anchoring (instruction v2 §8)
   ----------------------------------------------------------------------------
   Offsets are NEVER reconstructed from visible text. Each .para-fragment is
   indexed once after insertion against its canonical p.text and its display
   atoms, giving an explicit text-node -> canonical-offset map.

   Public API
     indexFragment(fragEl, paraId, canonicalText, atoms)
     canonicalPosition(node, offset)      -> {paraId, canonical} | null
     selectionParts(range)                -> [{para_id, start_char, end_char, text}]
     paintParts(fragEl, records)          -> paints by canonical offsets
     groupedQuote(parts, joiner)          -> user-visible grouped quotation
   ========================================================================== */
(function (root) {
  'use strict';

  // fragment element -> { paraId, text, atoms, nodes:[{node,ds,de}], displayLen }
  var REG = new WeakMap();

  function isLabel(node, stop) {
    var el = node.parentElement;
    while (el && el !== stop) {
      if (el.classList && (el.classList.contains('speech-label') || el.classList.contains('speech-conf') || el.classList.contains('speech-quoted-voice') || el.classList.contains('speech-attribution-sr'))) return true;
      el = el.parentElement;
    }
    return false;
  }

  /* -- §8.1 explicit map, built from canonical text + display atoms --------- */
  function indexFragment(fragEl, paraId, canonicalText, atoms, opts) {
    if (!fragEl) return null;
    opts = opts || {};
    var canonicalStart = Number.isFinite(opts.canonicalStart) ? opts.canonicalStart : 0;
    var canonicalEnd = Number.isFinite(opts.canonicalEnd) ? opts.canonicalEnd : canonicalText.length;
    canonicalStart = Math.max(0, Math.min(canonicalStart, canonicalText.length));
    canonicalEnd = Math.max(canonicalStart, Math.min(canonicalEnd, canonicalText.length));
    var nodes = [], ds = 0;
    var w = document.createTreeWalker(fragEl, NodeFilter.SHOW_TEXT, null, false);
    var n;
    while ((n = w.nextNode())) {
      if (!n.nodeValue) continue;
      if (isLabel(n, fragEl)) continue;          // labels are injected, not content
      nodes.push({ node: n, ds: ds, de: ds + n.nodeValue.length });
      ds += n.nodeValue.length;
    }
    var rec = { paraId: paraId, text: canonicalText, atoms: atoms || null,
                canonicalStart: canonicalStart, canonicalEnd: canonicalEnd,
                nodes: nodes, displayLen: ds };
    REG.set(fragEl, rec);
    fragEl.dataset.displayLength = String(ds);
    fragEl.dataset.canonicalStart = String(canonicalStart);
    fragEl.dataset.canonicalEnd = String(canonicalEnd);
    return rec;
  }

  function recordFor(fragEl) { return fragEl ? REG.get(fragEl) : null; }

  function fragmentOf(node) {
    if (!node) return null;
    var el = node.nodeType === 3 ? node.parentElement : node;
    return el ? el.closest('.para-fragment') : null;
  }

  // display offset of (node, offset) within its fragment.
  //
  // Safari/iPadOS may expose a native Selection endpoint as an ELEMENT boundary
  // beside an injected accessibility/presentation node rather than directly in the
  // visible canonical text node. Those injected nodes are intentionally absent from
  // rec.nodes. Resolve such boundaries to the nearest INDEXED canonical text node
  // with an endpoint-specific bias; never let a noncanonical label become a reason
  // to substitute an entire paragraph.
  function displayOffsetOf(rec, node, offset, bias) {
    bias = bias === 'backward' ? 'backward' : 'forward';
    if (node.nodeType === 3) {
      var exact = entryFor(rec, node);
      if (exact) return exact.ds + Math.min(Math.max(0, offset), node.nodeValue.length);
      // The text node itself is presentation-only (for example
      // .speech-attribution-sr). Skip the whole injected presentation wrapper in
      // the requested direction and bind to neighbouring canonical content.
      var frag = fragmentOf(node), carrier = presentationOnlyAncestor(node, frag) || node;
      return indexedOffsetFromNodeBoundary(rec, carrier, bias);
    }
    return indexedOffsetFromElementBoundary(rec, node, offset, bias);
  }

  function entryFor(rec, node) {
    for (var i = 0; i < rec.nodes.length; i++) if (rec.nodes[i].node === node) return rec.nodes[i];
    return null;
  }

  function presentationOnlyAncestor(node, stop) {
    var el = node && (node.nodeType === 3 ? node.parentElement : node);
    while (el && el !== stop) {
      if (el.classList && (el.classList.contains('speech-label') || el.classList.contains('speech-conf') || el.classList.contains('speech-quoted-voice') || el.classList.contains('speech-attribution-sr'))) return el;
      el = el.parentElement;
    }
    return null;
  }

  function firstIndexedTextIn(rec, el) {
    if (!el) return null;
    if (el.nodeType === 3) return entryFor(rec, el) ? el : null;
    var w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false), n;
    while ((n = w.nextNode())) if (entryFor(rec, n)) return n;
    return null;
  }
  function lastIndexedTextIn(rec, el) {
    if (!el) return null;
    if (el.nodeType === 3) return entryFor(rec, el) ? el : null;
    var w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false), n, last = null;
    while ((n = w.nextNode())) if (entryFor(rec, n)) last = n;
    return last;
  }

  function nextIndexedTextAfter(rec, node, stop) {
    var cur = node;
    while (cur && cur !== stop) {
      var sib = cur.nextSibling;
      while (sib) {
        var hit = firstIndexedTextIn(rec, sib);
        if (hit) return hit;
        sib = sib.nextSibling;
      }
      cur = cur.parentNode;
    }
    return null;
  }
  function previousIndexedTextBefore(rec, node, stop) {
    var cur = node;
    while (cur && cur !== stop) {
      var sib = cur.previousSibling;
      while (sib) {
        var hit = lastIndexedTextIn(rec, sib);
        if (hit) return hit;
        sib = sib.previousSibling;
      }
      cur = cur.parentNode;
    }
    return null;
  }

  function indexedOffsetFromNodeBoundary(rec, node, bias) {
    var frag = fragmentOf(node);
    if (!frag) return null;
    if (bias === 'backward') {
      var prev = previousIndexedTextBefore(rec, node, frag);
      var pe = prev && entryFor(rec, prev);
      if (pe) return pe.de;
      var nextFallback = nextIndexedTextAfter(rec, node, frag);
      var neFallback = nextFallback && entryFor(rec, nextFallback);
      return neFallback ? neFallback.ds : null;
    }
    var next = nextIndexedTextAfter(rec, node, frag);
    var ne = next && entryFor(rec, next);
    if (ne) return ne.ds;
    var prevFallback = previousIndexedTextBefore(rec, node, frag);
    var peFallback = prevFallback && entryFor(rec, prevFallback);
    return peFallback ? peFallback.de : null;
  }

  function indexedOffsetFromElementBoundary(rec, node, offset, bias) {
    var frag = fragmentOf(node);
    if (!frag) return null;
    var kids = node.childNodes || [], clamped = Math.max(0, Math.min(Number(offset) || 0, kids.length));
    if (bias === 'forward') {
      for (var i = clamped; i < kids.length; i++) {
        var fwd = firstIndexedTextIn(rec, kids[i]);
        var fe = fwd && entryFor(rec, fwd);
        if (fe) return fe.ds;
      }
      var after = nextIndexedTextAfter(rec, node, frag);
      var ae = after && entryFor(rec, after);
      if (ae) return ae.ds;
      for (var j = clamped - 1; j >= 0; j--) {
        var backFallback = lastIndexedTextIn(rec, kids[j]);
        var bfe = backFallback && entryFor(rec, backFallback);
        if (bfe) return bfe.de;
      }
      var prevFallback = previousIndexedTextBefore(rec, node, frag);
      var pfe = prevFallback && entryFor(rec, prevFallback);
      return pfe ? pfe.de : null;
    }
    for (var k = clamped - 1; k >= 0; k--) {
      var back = lastIndexedTextIn(rec, kids[k]);
      var be = back && entryFor(rec, back);
      if (be) return be.de;
    }
    var before = previousIndexedTextBefore(rec, node, frag);
    var bfe2 = before && entryFor(rec, before);
    if (bfe2) return bfe2.de;
    for (var m = clamped; m < kids.length; m++) {
      var fwdFallback = firstIndexedTextIn(rec, kids[m]);
      var ffe = fwdFallback && entryFor(rec, fwdFallback);
      if (ffe) return ffe.ds;
    }
    var nextFallback2 = nextIndexedTextAfter(rec, node, frag);
    var nfe2 = nextFallback2 && entryFor(rec, nextFallback2);
    return nfe2 ? nfe2.ds : null;
  }

  /* -- display offset -> canonical offset, via the display map -------------- */
  function toCanonical(rec, dispOffset) {
    if (dispOffset === null || dispOffset === undefined) return null;
    if (!rec.atoms || !root.LDCDisplayMap) return Math.min(rec.canonicalStart + dispOffset, rec.canonicalEnd);
    return root.LDCDisplayMap.displayToCanonical(rec.atoms, dispOffset);
  }
  function toDisplay(rec, canOffset) {
    canOffset = Math.max(rec.canonicalStart, Math.min(canOffset, rec.canonicalEnd));
    if (!rec.atoms || !root.LDCDisplayMap) return Math.max(0, Math.min(canOffset - rec.canonicalStart, rec.displayLen));
    return root.LDCDisplayMap.canonicalToDisplay(rec.atoms, canOffset);
  }

  function canonicalPosition(node, offset, bias) {
    var frag = fragmentOf(node);
    var rec = recordFor(frag);
    if (!rec) return null;
    var d = displayOffsetOf(rec, node, offset, bias);
    if (d === null) return null;
    return { paraId: rec.paraId, canonical: toCanonical(rec, d), fragment: frag };
  }

  /* -- §8.3 one part per paragraph fragment -------------------------------- */
  function selectionParts(range) {
    if (!range) return [];
    var startFrag = fragmentOf(range.startContainer);
    var endFrag   = fragmentOf(range.endContainer);
    var reader = document.getElementById('reader-body');
    // Fail closed. If either browser Range endpoint escapes the canonical reader
    // fragment layer, do NOT “snap” it to some neighbouring/distant fragment.
    // That old recovery could turn a small mouse/touch selection into a range
    // spanning many paragraphs or almost the whole screen.
    if (!reader || !startFrag || !endFrag || !reader.contains(startFrag) || !reader.contains(endFrag)) return [];

    var all = Array.prototype.slice.call(
      reader.querySelectorAll('.para-fragment'));
    var i0 = all.indexOf(startFrag), i1 = all.indexOf(endFrag);
    if (i0 < 0 || i1 < 0) return [];

    // Endpoints are authoritative. If either one cannot be mapped explicitly to
    // canonical text, fail closed. Only truly INTERMEDIATE fragments may use their
    // full canonicalStart/canonicalEnd. Never repair an unresolved endpoint by
    // silently expanding it to the start/end of its paragraph.
    var startPos = canonicalPosition(range.startContainer, range.startOffset, 'forward');
    var endPos   = canonicalPosition(range.endContainer,   range.endOffset,   'backward');
    if (!startPos || !endPos || startPos.fragment !== startFrag || endPos.fragment !== endFrag) return [];
    if (i0 > i1) {
      var t = i0; i0 = i1; i1 = t;
      t = startFrag; startFrag = endFrag; endFrag = t;
      t = startPos; startPos = endPos; endPos = t;
    }

    var parts = [];
    for (var i = i0; i <= i1; i++) {
      var f = all[i], rec = recordFor(f);
      if (!rec) continue;
      var sc = (f === startFrag) ? startPos.canonical : rec.canonicalStart;
      var ec = (f === endFrag)   ? endPos.canonical   : rec.canonicalEnd;
      if (sc > ec) { var q = sc; sc = ec; ec = q; }
      sc = Math.max(0, Math.min(sc, rec.text.length));
      ec = Math.max(0, Math.min(ec, rec.text.length));   // never exceed paragraph length
      if (ec <= sc) continue;
      parts.push({ para_id: rec.paraId, start_char: sc, end_char: ec,
                   text: rec.text.slice(sc, ec) });
    }
    return parts;
  }

  function nextFragment(node, dir) {
    var el = node.nodeType === 3 ? node.parentElement : node;
    while (el) {
      var sib = dir > 0 ? el.nextElementSibling : el.previousElementSibling;
      while (sib) {
        if (sib.classList && sib.classList.contains('para-fragment')) return sib;
        var inner = sib.querySelector && sib.querySelector('.para-fragment');
        if (inner) return inner;
        sib = dir > 0 ? sib.nextElementSibling : sib.previousElementSibling;
      }
      el = el.parentElement;
      if (el && el.id === 'reader-body') break;
    }
    return null;
  }

  /* -- painting by canonical offsets ---------------------------------------
     All pieces are computed against the FRESH index first, then wrapped from
     the end backwards, because <mark> insertion splits text nodes. */
  function paintParts(fragEl, records) {
    var rec = recordFor(fragEl);
    if (!rec || !records || !records.length) return { painted: 0, fallback: [] };
    var pieces = [], fallback = [], painted = 0;

    records.forEach(function (h) {
      if (fragEl.querySelector('mark[data-hl-id="' + h.id + '"]')) return;
      var s = h.start_char, e = h.end_char;
      var usable = (typeof s === 'number' && typeof e === 'number' &&
                    s >= 0 && e > s && e <= rec.text.length);
      if (usable && h.text) {
        // the stored slice must still be the canonical slice (quote/space folded)
        var want = fold(h.text), got = fold(rec.text.slice(s, e));
        if (want && got !== want) usable = false;
      }
      if (!usable) { fallback.push(h); return; }
      // A canonical paragraph may be projected into multiple display slices around
      // an exact within-paragraph COMPLÉMENT. Paint only the intersection owned by
      // this slice while keeping the persisted offsets relative to the unsplit text.
      var ps = Math.max(s, rec.canonicalStart), pe = Math.min(e, rec.canonicalEnd);
      if (pe <= ps) return;
      var ds = toDisplay(rec, ps), de = toDisplay(rec, pe);
      if (de <= ds) return;
      rec.nodes.forEach(function (nd) {
        var a = Math.max(ds, nd.ds), b = Math.min(de, nd.de);
        if (b > a) pieces.push({ node: nd.node, start: a - nd.ds, end: b - nd.ds, h: h });
      });
      painted++;
    });

    pieces.sort(function (x, y) {
      var p = x.node.compareDocumentPosition(y.node);
      if (p & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
      if (p & Node.DOCUMENT_POSITION_PRECEDING) return 1;
      return x.start - y.start;
    });
    pieces.reverse().forEach(function (pc) {
      try {
        var r = document.createRange();
        r.setStart(pc.node, pc.start);
        r.setEnd(pc.node, pc.end);
        var mk = document.createElement('mark');
        mk.className = 'hl hl-' + pc.h.color;
        mk.setAttribute('data-hl-id', pc.h.id);
        if (pc.h.highlight_group_id) mk.setAttribute('data-hl-group', pc.h.highlight_group_id);
        r.surroundContents(mk);
      } catch (e) { /* node already re-split by a later piece */ }
    });
    return { painted: painted, fallback: fallback };
  }

  function fold(s) {
    return String(s || '')
      .replace(/[‘’‚‛]/g, "'")
      .replace(/[“”„«»]/g, '"')
      .replace(/[‐-―]/g, '-')
      .replace(/[    ]/g, ' ')
      .replace(/\s+/g, ' ').trim();
  }

  /* -- §8.3 reconstruct the grouped quotation with the recorded joiner ------ */
  function groupedQuote(parts, joiner) {
    var j = joiner === 'none' ? '' : (joiner === 'nonbreaking_space' ? ' ' : ' ');
    return parts.map(function (p) { return p.text; }).join(j);
  }

  root.LDCAnchor = {
    indexFragment: indexFragment,
    recordFor: recordFor,
    fragmentOf: fragmentOf,
    canonicalPosition: canonicalPosition,
    selectionParts: selectionParts,
    paintParts: paintParts,
    groupedQuote: groupedQuote,
    fold: fold
  };
})(typeof window !== 'undefined' ? window : globalThis);
