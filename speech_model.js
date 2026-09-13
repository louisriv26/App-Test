/* ============================================================================
   LDC R1B — Stage B: pure paragraph-local speech model builder
   ----------------------------------------------------------------------------
   buildParagraphSpeechModel(text, segments) -> model

   Pure function. No DOM, no mutation of inputs, no string deletion.
   Every canonical character of `text` appears exactly once across model.intervals.

   Governing rules (instruction v2 §7.1–7.3, §7.5, §7.7):
     - validate segments; never silently "repair" them
     - cover the paragraph with atomic intervals (narrative | speech)
     - merge adjacent styled segments ONLY when:
         same normalised speaker, truly adjacent in the FULL segment order,
         and the bridge between them contains no letter or digit
       The bridge characters are KEPT inside the run (never discarded).
     - internal quotation marks are ordinary characters of the run and must
       never terminate it
     - block/inline is decided per RUN, never per source segment
   ========================================================================== */
(function (root) {
  'use strict';

  var STYLED = { JESUS: 'jesus', MARIE: 'marie', MARY: 'marie' };

  // A bridge is "non-lexical" if it contains no letter or digit. Accents included.
  var LEXICAL = /[0-9A-Za-zÀ-ɏ]/;

  function normSpeaker(s) { return STYLED[s] || null; }
  function isStyled(s) { return !!STYLED[s]; }
  var CONF_RANK = { low: 0, medium: 1, high: 2 };
  function mergeConfidence(a, b) {
    if (!a) return b || null;
    if (!b) return a || null;
    return (CONF_RANK[a] <= CONF_RANK[b]) ? a : b;
  }


  // RA19E.1 / Version 36 — Repères dual-attribution support.  These descriptors
  // are study-layer metadata only.  They never alter canonical text, segment
  // offsets, semantic speaker identity, or presentation-parent styling.
  function semanticVoiceKey(v) {
    return String((v && v.speaker) || '').toUpperCase() + '|' +
           String((v && v.subrole) || '').toLowerCase();
  }
  function appendSemanticVoice(list, speaker, subrole) {
    list = list || [];
    var v = {speaker:String(speaker || '').toUpperCase(), subrole:String(subrole || '').toLowerCase()};
    if (!v.speaker) return list;
    var key = semanticVoiceKey(v);
    for (var i = 0; i < list.length; i++) if (semanticVoiceKey(list[i]) === key) return list;
    list.push(v);
    return list;
  }
  function mergeSemanticVoices(target, source) {
    target = target || [];
    source = source || [];
    for (var i = 0; i < source.length; i++) appendSemanticVoice(target, source[i].speaker, source[i].subrole);
    return target;
  }

  /* -- validation: report, never mutate ----------------------------------- */
  function validateSegments(text, segments) {
    var errs = [];
    var sorted = segments.slice().sort(function (a, b) {
      return a.start_char - b.start_char || a.end_char - b.end_char;
    });
    for (var i = 0; i < sorted.length; i++) {
      var s = sorted[i];
      if (!(s.start_char >= 0 && s.start_char < s.end_char && s.end_char <= text.length)) {
        errs.push({ code: 'INVALID_RANGE', segment_id: s.segment_id,
                    start: s.start_char, end: s.end_char, len: text.length });
      }
      if (i > 0 && s.start_char < sorted[i - 1].end_char) {
        errs.push({ code: 'OVERLAP', segment_id: s.segment_id,
                    prev_segment_id: sorted[i - 1].segment_id });
      }
    }
    return { sorted: sorted, errors: errs };
  }

  /* -- main ---------------------------------------------------------------- */
  function buildParagraphSpeechModel(text, segments, opts) {
    opts = opts || {};
    var v = validateSegments(text, segments || []);
    if (v.errors.length && !opts.tolerateInvalid) {
      return { ok: false, errors: v.errors, intervals: [], runs: [] };
    }
    var sorted = v.sorted;

    /* 1 — atomic intervals covering the paragraph exactly once */
    var intervals = [], cur = 0;
    for (var i = 0; i < sorted.length; i++) {
      var s = sorted[i];
      if (s.start_char > cur) {
        intervals.push({ start: cur, end: s.start_char, text: text.slice(cur, s.start_char),
                         role: 'NARRATIVE', speaker: null, styled: false,
                         confidence: null, segment_ids: [] });
      }
      var displaySpeaker = s.display_speaker || s.speaker;
      intervals.push({ start: s.start_char, end: s.end_char,
                       text: text.slice(s.start_char, s.end_char),
                       role: s.speaker, semantic_speaker: s.speaker,
                       semantic_subrole: s.semantic_subrole_normalized || s.semantic_subrole || null,
                       speaker: displaySpeaker,
                       styled: isStyled(displaySpeaker),
                       confidence: s.confidence || null,
                       quotation_depth: s.quotation_depth == null ? null : s.quotation_depth,
                       quote_depth: s.quote_depth == null ? null : s.quote_depth,
                       segment_ids: [s.segment_id] });
      cur = s.end_char;
    }
    if (cur < text.length) {
      intervals.push({ start: cur, end: text.length, text: text.slice(cur),
                       role: 'NARRATIVE', speaker: null, styled: false,
                       confidence: null, segment_ids: [] });
    }

    /* 2 — controlled coalescence into paragraph-local runs.
           Adjacency is evaluated on the FULL interval sequence: a NARRATIVE
           interval between two styled intervals means they are NOT adjacent,
           which is exactly what excludes the 99 intervening-role pairs. */
    var runs = [], merges = [];
    for (var j = 0; j < intervals.length; j++) {
      var iv = intervals[j];
      var last = runs.length ? runs[runs.length - 1] : null;
      if (last && last.styled && iv.styled &&
          normSpeaker(last.speaker) === normSpeaker(iv.speaker) &&
          last.end === iv.start) {
        // directly abutting styled intervals of the same speaker
        last.end = iv.end;
        last.text += iv.text;
        last.segment_ids = last.segment_ids.concat(iv.segment_ids);
        last.semantic_voices = mergeSemanticVoices(last.semantic_voices, iv.semantic_speaker ? [{speaker:iv.semantic_speaker,subrole:iv.semantic_subrole}] : []);
        last.confidence = mergeConfidence(last.confidence, iv.confidence);
        last.end_quotation_depth = iv.quotation_depth;
        last.end_quote_depth = iv.quote_depth;
        merges.push({ at: iv.start, kind: 'abut', bridge: '' });
        continue;
      }
      if (last && last.styled && iv.styled === false && j + 1 < intervals.length) {
        var nxt = intervals[j + 1];
        if (nxt.styled && normSpeaker(last.speaker) === normSpeaker(nxt.speaker) &&
            last.end === iv.start && iv.end === nxt.start &&
            !LEXICAL.test(iv.text)) {
          // NON-LEXICAL BRIDGE: keep the bridge characters inside the run
          last.end = nxt.end;
          last.text += iv.text + nxt.text;
          last.segment_ids = last.segment_ids.concat(nxt.segment_ids);
          last.semantic_voices = mergeSemanticVoices(last.semantic_voices, nxt.semantic_speaker ? [{speaker:nxt.semantic_speaker,subrole:nxt.semantic_subrole}] : []);
          last.confidence = mergeConfidence(last.confidence, nxt.confidence);
          last.end_quotation_depth = nxt.quotation_depth;
          last.end_quote_depth = nxt.quote_depth;
          merges.push({ at: iv.start, kind: 'non_lexical_bridge', bridge: iv.text });
          j++; // consume nxt
          continue;
        }
      }
      runs.push({ start: iv.start, end: iv.end, text: iv.text,
                  role: iv.role, speaker: iv.speaker, styled: iv.styled,
                  semantic_voices: iv.semantic_speaker ? [{speaker:String(iv.semantic_speaker).toUpperCase(),subrole:String(iv.semantic_subrole || '').toLowerCase()}] : [],
                  confidence: iv.confidence, segment_ids: iv.segment_ids.slice(),
                  start_quotation_depth: iv.quotation_depth, end_quotation_depth: iv.quotation_depth,
                  start_quote_depth: iv.quote_depth, end_quote_depth: iv.quote_depth,
                  presentation: null });
    }

    /* 3 — presentation contract per RUN (RA4C).
       Every validated visible Jesus/Mary direct-speech run starts as a new visual
       paragraph. This is deliberately stronger than the earlier heuristic that
       allowed embedded direct quotations to remain inline. Nested/reported quotes
       resolved to Luisa are not styled and remain narrative. */
    for (var k = 0; k < runs.length; k++) {
      var r = runs[k];
      if (!r.styled) { r.presentation = 'narrative'; continue; }
      r.presentation = 'block';
    }

    return { ok: true, errors: [], intervals: intervals, runs: runs, merges: merges };
  }

  /* -- reconstruction proof helper ---------------------------------------- */
  function reconstruct(model) {
    var out = '';
    for (var i = 0; i < model.intervals.length; i++) out += model.intervals[i].text;
    return out;
  }

  /* -- §7.4 link same-speaker runs across approved flow boundaries ---------
     members: [{ paraId, text, model, atoms, boundaryAfter }] in display order.
     A link is created ONLY when all seven conditions hold. Sharing a speaker is
     never sufficient — the flow decision and its boundary metadata are
     mandatory. Mutates member models in place and returns the link ledger. */
  // RA17 — visual continuity is a separate concern from semantic same-speaker
  // linking.  A logical speech run may cross a flow boundary while the visible
  // structure still needs a break (for example a genuine enumeration).
  function stripLeadingFlowDash(text) {
    return String(text || '').replace(/^\s*[-–—]\s+/, '').trim();
  }
  function effectiveTail(text) {
    return String(text || '').trim().replace(/[\s»”"\)\]\}]+$/g, '');
  }
  function isStrongColonDashEnumeration(members) {
    if (!members || members.length < 3) return false;
    var head = effectiveTail(members[0].text || '');
    if (!/:$/.test(head)) return false;
    var n = 0;
    for (var i = 1; i < members.length; i++) {
      if (/^\s*[-–—]\s+/.test(String(members[i].text || ''))) n++;
    }
    return n >= 2;
  }
  function flowBoundaryVisualPolicy(members, index, meta) {
    meta = meta || {};
    // RA19B — source-backed boundary metadata is authoritative. The RA18
    // heuristic remains only as a compatibility fallback for legacy/non-active
    // boundaries that do not carry an RA19B adjudication record.
    var explicitBoundary = members && members[index] && members[index].boundaryAfter || null;
    if (explicitBoundary && explicitBoundary.adjudication_generation === 'RA19B_MULTI_SOURCE') {
      var explicitPolicy = String(explicitBoundary.visual_policy || '');
      var explicitAction = String(explicitBoundary.visual_action || '');
      var expectedAction = explicitPolicy === 'continuous_prose' ? 'join_inline'
        : (explicitPolicy === 'preserve_break_enumeration' ? 'preserve_list_break'
        : (explicitPolicy === 'preserve_break_ambiguous' ? 'preserve_break' : ''));
      if (explicitBoundary.adjudication_status !== 'SOURCE_BACKED_CERTAIN' ||
          !expectedAction || explicitAction !== expectedAction ||
          !explicitBoundary.evidence_ref || !/^[0-9a-f]{64}$/i.test(String(explicitBoundary.evidence_sha256 || ''))) {
        throw new Error('LDC_INVALID_RA19B_EXPLICIT_FLOW_BOUNDARY:' +
          String(members[index] && members[index].paraId || index));
      }
      return { policy: explicitPolicy, reason: 'ra19b_source_backed_explicit_boundary',
               action: explicitAction, explicit: true,
               evidence_ref: String(explicitBoundary.evidence_ref),
               evidence_sha256: String(explicitBoundary.evidence_sha256) };
    }
    if (isStrongColonDashEnumeration(members)) {
      return { policy:'preserve_break_enumeration', reason:'strong_colon_dash_enumeration' };
    }
    var cls = String(meta.classification || '');
    var confidence = String(meta.confidence || '');
    if (confidence === 'high' ||
        /(?:sentence_continuation|source_quotation_continuation|source_page_break_quote_continuation)/.test(cls)) {
      return { policy:'continuous_prose', reason:'adjudicated_flow_continuation' };
    }
    var cur = effectiveTail(members[index] && members[index].text || '');
    var nxt = stripLeadingFlowDash(members[index + 1] && members[index + 1].text || '');
    // A terminal sentence/list delimiter is intentionally conservative here.
    // Inherited dash groups are not promoted merely because the next line begins
    // lower-case or because the previous one ends in a comma.
    if (/[.?!…:;]$/.test(cur)) {
      return { policy:'preserve_break_ambiguous', reason:'terminal_or_list_delimiter' };
    }
    if (/^(?:que\b|qu[’']|qui\b|dont\b|où\b|lequel\b|laquelle\b|lesquels\b|lesquelles\b|auquel\b|auxquels\b|auxquelles\b|duquel\b|desquels\b|desquelles\b|afin\s+que\b|parce\s+que\b|pour\s+que\b|de\s+sorte\s+que\b|si\s+bien\s+que\b)/i.test(nxt)) {
      return { policy:'continuous_prose', reason:'dependent_clause_starter' };
    }
    if (/^en\s+(?:(?:me|te|se|nous|vous|le|la|les|lui|leur|y)\s+)?[A-Za-zÀ-ÿŒœÆæ’'\-]+(?:ant|issant)\b/i.test(nxt)) {
      return { policy:'continuous_prose', reason:'gerund_clause' };
    }
    if (/(?:^|[\s«“"'\(])(?:de|du|des|ce|cet|cette|ces|que|qu[’']|qui|dont|où|et|ou|ni|à|au|aux|en|pour|par|avec|sans|sur|sous|dans|comme|si|afin|lorsque|quand)\s*$/i.test(cur)) {
      return { policy:'continuous_prose', reason:'syntactically_incomplete_head' };
    }
    return { policy:'preserve_break_ambiguous', reason:'pending_flow_not_safely_joinable' };
  }

  function flowJoinerPresentation(action, joinerText) {
    action = String(action || 'baseline_joiner');
    if (action === 'preserve_break') {
      return { action:action, className:'flow-joiner flow-joiner-action-break', text:'' };
    }
    if (action === 'preserve_list_break') {
      return { action:action, className:'flow-joiner flow-joiner-action-list-break', text:'' };
    }
    if (action === 'join_inline') {
      return { action:action, className:'flow-joiner flow-joiner-action-inline', text:String(joinerText == null ? '' : joinerText) };
    }
    return { action:'baseline_joiner', className:'flow-joiner', text:String(joinerText == null ? '' : joinerText) };
  }

  function linkFlowRuns(members, opts) {
    opts = opts || {};
    var links = [];
    // display-visible length of a canonical range, so an approved suppressed
    // extraction dash does not stop a run from counting as fragment-initial
    function visibleLen(atoms, from, to) {
      if (!atoms) return Math.max(0, to - from);
      var n = 0;
      for (var i = 0; i < atoms.length; i++) {
        var a = atoms[i];
        if (a.ce <= from || a.cs >= to) continue;
        if (a.kind === 'canonical') n += Math.min(a.ce, to) - Math.max(a.cs, from);
        else n += a.text.length;
      }
      return n;
    }
    for (var k = 0; k < members.length - 1; k++) {
      var cur = members[k], nxt = members[k + 1];
      var b = cur.boundaryAfter;
      // (1)+(2) same approved group, boundary permits continuation
      if (!b || b.speech_run_policy !== 'continue_same_speaker_only') continue;
      if (!cur.model || !cur.model.ok || !nxt.model || !nxt.model.ok) continue;
      var cr = cur.model.runs[cur.model.runs.length - 1];
      var nr = nxt.model.runs[0];
      if (!cr || !nr || !cr.styled || !nr.styled) continue;
      // (3) identical normalised speaker
      if (normSpeaker(cr.speaker) !== normSpeaker(nr.speaker)) continue;
      // (4) nothing may intervene: the run must reach the visible end of its
      // fragment, and the next run must start at the visible start of its own
      if (visibleLen(cur.atoms, cr.end, cur.text.length) !== 0) continue;
      if (visibleLen(nxt.atoms, 0, nr.start) !== 0) continue;
      // (5) a leading extraction dash must be an approved suppressed range
      if (nr.start > 0) {
        var supp = (b.suppress_next_leading_ranges || []);
        var covered = supp.some(function (r) { return r[0] === 0 && r[1] >= nr.start; }) ||
                      visibleLen(nxt.atoms, 0, nr.start) === 0;
        if (!covered) continue;
      }
      // (6) the joiner must be explicit
      if (!b.display_joiner) continue;
      // (7) the continuation inherits the logical run id. Visual continuity is
      // deliberately classified separately so genuine/potential list structure
      // is not flattened merely because the speaker remains the same.
      var visual = flowBoundaryVisualPolicy(members, k, opts);
      cur.visualPolicyAfter = visual.policy;
      cur.visualPolicyReason = visual.reason;
      var runId = cr.runId || (cur.paraId + '#R' + (cur.model.runs.length - 1));
      cr.runId = runId;
      nr.runId = runId;
      nr.isContinuation = true;
      // RA19B: logical same-speaker continuation and source-backed visual action are
      // independent. Every linked boundary receives one explicit action.
      var visualAction = visual.action || (visual.policy === 'continuous_prose' ? 'join_inline'
        : (visual.policy === 'preserve_break_enumeration' ? 'preserve_list_break' : 'preserve_break'));
      cur.visualBoundaryActionAfter = visualAction;
      nxt.visualBoundaryActionFromPrevious = visualAction;
      if (visualAction === 'join_inline') {
        cr.visualContinuesToNext = true;
        nr.visualContinuesFromPrevious = true;
      }
      links.push({ run_id: runId, from_paragraph: cur.paraId, to_paragraph: nxt.paraId,
                   speaker: normSpeaker(cr.speaker), joiner: b.display_joiner,
                   visual_policy: visual.policy, visual_reason: visual.reason,
                   visual_action: visualAction, explicit_source_backed: !!visual.explicit,
                   evidence_ref: visual.evidence_ref || '', evidence_sha256: visual.evidence_sha256 || '',
                   suppressed_leading: JSON.stringify(b.suppress_next_leading_ranges || []) });
    }

    // A linked visual run may cross several paragraph fragments.  Repères emits
    // its attribution only on the first fragment, so aggregate the semantic
    // voices across the complete linked run and copy that ordered unique list to
    // every fragment before rendering.  This prevents later quoted voices from
    // disappearing merely because they begin in a continuation paragraph.
    var linkedVoices = {};
    for (var mi = 0; mi < members.length; mi++) {
      var mm = members[mi];
      if (!mm.model || !mm.model.ok) continue;
      for (var ri = 0; ri < mm.model.runs.length; ri++) {
        var rr = mm.model.runs[ri];
        if (!rr.styled || !rr.runId) continue;
        if (!linkedVoices[rr.runId]) linkedVoices[rr.runId] = [];
        mergeSemanticVoices(linkedVoices[rr.runId], rr.semantic_voices || []);
      }
    }
    for (var mj = 0; mj < members.length; mj++) {
      var m2 = members[mj];
      if (!m2.model || !m2.model.ok) continue;
      for (var rj = 0; rj < m2.model.runs.length; rj++) {
        var r2 = m2.model.runs[rj];
        if (r2.styled && r2.runId && linkedVoices[r2.runId]) r2.semantic_voices = linkedVoices[r2.runId].slice();
      }
    }
    return links;
  }

  /* -- GR8: presentation speaker for nested quotations ----------------------
     Semantic attribution and presentation attribution are deliberately separate.
     A depth-2 quotation is a quotation made INSIDE an already active depth-1
     speaking turn. The quoted person's identity remains in `speaker`, but the
     visible font/colour must remain that of the outer speaker. This prevents:
       - Luisa quoting remembered words of Jesus from turning gold mid-sentence;
       - Jesus quoting a human/personified voice from turning back to narrative.

     The source speaker JSON is immutable. This function clones records and adds
     `display_speaker`; search/audit continue to use the original `speaker`.
     Parent resolution is structural: nearest preceding depth-1 segment before a
     depth-0 boundary governs. If no preceding depth-1 speaker exists, the nested
     quotation belongs to Luisa's narrative presentation (normal prose); it must
     never borrow a speaker turn that starts later. When a following depth-1
     candidate differs from the preceding one, the preceding speaker still governs
     because the nested quotation has already been introduced inside that turn.
  -------------------------------------------------------------------------- */
  function resolveNestedQuotationPresentation(segments, paragraphOrder) {
    paragraphOrder = paragraphOrder || {};

    /* RA19E.1 / Version 45 mixed-entry hardening.
       Main-corpus presentation_parent is authoritative PER SEGMENT. Supplement
       records intentionally have no presentation_parent and therefore use the
       legacy contextual fallback. A parentless supplement must never force an
       explicitly adjudicated backbone segment back through legacy inference. */
    var sourceSegments = segments || [];
    var arr = sourceSegments.map(function (s, ix) {
      var c = {};
      for (var k in s) if (Object.prototype.hasOwnProperty.call(s, k)) c[k] = s[k];
      c.__ix = ix;
      c.display_speaker = s.speaker;
      c.display_resolution = 'semantic_speaker';
      return c;
    });
    arr.sort(function (a, b) {
      var ao = paragraphOrder[a.paragraph_id];
      var bo = paragraphOrder[b.paragraph_id];
      if (ao == null) ao = 0;
      if (bo == null) bo = 0;
      return ao - bo || a.start_char - b.start_char || a.end_char - b.end_char || a.__ix - b.__ix;
    });

    /* Compute the historical contextual fallback over the whole entry. This
       remains the only authority for parentless supplement records. */
    var prevParent = new Array(arr.length), nextParent = new Array(arr.length);
    var active = null;
    for (var i = 0; i < arr.length; i++) {
      var q = Number(arr[i].quotation_depth || 0);
      if (q === 0) active = null;
      else if (q === 1) active = arr[i].speaker;
      prevParent[i] = active;
    }
    active = null;
    for (var j = arr.length - 1; j >= 0; j--) {
      var q2 = Number(arr[j].quotation_depth || 0);
      if (q2 === 0) active = null;
      else if (q2 === 1) active = arr[j].speaker;
      nextParent[j] = active;
    }

    var fallbackLedger = [], fallbackErrors = [];
    for (var n = 0; n < arr.length; n++) {
      var s = arr[n];
      if (Number(s.quotation_depth || 0) !== 2) continue;
      var prev = prevParent[n], next = nextParent[n];
      var parent = prev || 'LUISA';
      s.display_speaker = parent;
      s.display_resolution = prev
        ? (next && next !== prev ? 'outer_prev_conflict_resolved' : 'outer_prev')
        : 'narrative_luisa_default';
      fallbackLedger.push({ scheme: 'quotation_depth', segment_id: s.segment_id, paragraph_id: s.paragraph_id,
                    semantic_speaker: s.speaker, display_speaker: parent,
                    previous_depth1: prev, next_depth1: next,
                    resolution: s.display_resolution });
    }

    /* GR8 legacy quote_depth fallback. */
    var legacyParent = null;
    for (var qx = 0; qx < arr.length; qx++) {
      var ls = arr[qx];
      var ld = Number(ls.quote_depth || 0);
      if (ld === 1) {
        legacyParent = ls.speaker;
        continue;
      }
      if (ld !== 2 || Number(ls.quotation_depth || 0) === 2) continue;
      var legacyDisplay = legacyParent || 'LUISA';
      ls.display_speaker = legacyDisplay;
      ls.display_resolution = legacyParent ? 'legacy_outer_prev' : 'legacy_narrative_luisa_default';
      if (!legacyParent) {
        fallbackErrors.push({ code: 'LEGACY_NESTED_WITHOUT_PRECEDING_DEPTH1',
                      segment_id: ls.segment_id, paragraph_id: ls.paragraph_id });
      }
      fallbackLedger.push({ scheme: 'legacy_quote_depth', segment_id: ls.segment_id,
                    paragraph_id: ls.paragraph_id, semantic_speaker: ls.speaker,
                    display_speaker: legacyDisplay, previous_depth1: legacyParent,
                    next_depth1: null, resolution: ls.display_resolution });
    }

    /* Overlay explicit RA19E.1 parent authority PER SEGMENT. Invalid explicit
       values are blocking. Fallback errors are relevant only to records that
       actually depend on fallback; an explicit segment is never invalidated by
       an unused legacy path. */
    var explicitLedger = [], fallbackUseLedger = [], explicitErrors = [];
    var explicitIds = {}, parentlessIds = {};
    for (var ex = 0; ex < arr.length; ex++) {
      var x = arr[ex];
      if (x.presentation_parent != null && String(x.presentation_parent).trim() !== '') {
        var ep = String(x.presentation_parent).toUpperCase();
        if (ep !== 'JESUS' && ep !== 'MARY' && ep !== 'LUISA') {
          explicitErrors.push({code:'INVALID_EXPLICIT_PRESENTATION_PARENT',segment_id:x.segment_id,presentation_parent:x.presentation_parent});
          parentlessIds[x.segment_id] = true;
          continue;
        }
        explicitIds[x.segment_id] = true;
        x.display_speaker = ep;
        x.display_resolution = 'explicit_ra19e1_parent_overlay';
        explicitLedger.push({scheme:'ra19e1_explicit_parent_overlay',segment_id:x.segment_id,paragraph_id:x.paragraph_id,
          semantic_speaker:x.speaker,display_speaker:ep,resolution:x.display_resolution});
      } else {
        parentlessIds[x.segment_id] = true;
        fallbackUseLedger.push({scheme:'legacy_fallback_missing_explicit_parent',segment_id:x.segment_id,paragraph_id:x.paragraph_id,
          semantic_speaker:x.speaker,display_speaker:x.display_speaker,resolution:x.display_resolution});
      }
    }
    var relevantFallbackErrors = fallbackErrors.filter(function (e) { return !!parentlessIds[e.segment_id]; });
    var errors = explicitErrors.concat(relevantFallbackErrors);
    var ledger = fallbackUseLedger.concat(explicitLedger);

    // Restore source order and remove private sort key.
    arr.sort(function (a, b) { return a.__ix - b.__ix; });
    for (var z = 0; z < arr.length; z++) delete arr[z].__ix;
    return {
      ok: errors.length === 0,
      segments: arr,
      ledger: ledger,
      errors: errors,
      explicit_parent_count: explicitLedger.length,
      fallback_parent_count: fallbackUseLedger.length,
      mixed_parent_mode: explicitLedger.length > 0 && fallbackUseLedger.length > 0
    };
  }

  root.LDCSpeechModel = {
    buildParagraphSpeechModel: buildParagraphSpeechModel,
    reconstruct: reconstruct,
    validateSegments: validateSegments,
    normSpeaker: normSpeaker,
    isStyled: isStyled,
    linkFlowRuns: linkFlowRuns,
    flowBoundaryVisualPolicy: flowBoundaryVisualPolicy,
    isStrongColonDashEnumeration: isStrongColonDashEnumeration,
    flowJoinerPresentation: flowJoinerPresentation,
    resolveNestedQuotationPresentation: resolveNestedQuotationPresentation
  };
})(typeof window !== 'undefined' ? window : globalThis);

/* ============================================================================
   Stage C — renderSpeechModel(model, opts) -> HTML string
   ----------------------------------------------------------------------------
   Emits ONE styled element per RUN (never per source segment) and ONE speaker
   label per run. Performs NO string deletion: every canonical character is
   emitted. An outer direct-speech delimiter is wrapped in
   <span class="speech-outer-delimiter"> so it can be visually suppressed by CSS
   while remaining present in the DOM with its canonical offsets.
   ========================================================================== */
(function (root) {
  'use strict';
  var M = root.LDCSpeechModel;

  function semanticVoiceLabel(speaker, subrole) {
    var sp = String(speaker || '').toUpperCase();
    var sr = String(subrole || '').toLowerCase();
    if (sp === 'LUISA') return 'Luisa';
    if (sp === 'MARY' || sp === 'MARIE') return 'Marie';
    if (sp === 'FATHER') return 'Père';
    if (sp === 'ANGEL') return 'ange';
    if (sp === 'CONFESSOR') return 'confesseur';
    if (sp === 'PRIEST') return 'prêtre';
    if (sp === 'DEMON') return 'démons';
    if (sp === 'SAINT') return sr.indexOf('blessed') >= 0 ? 'Bienheureux' : 'saint';
    if (sp === 'GENERIC_SOUL') {
      if (sr.indexOf('future_blessed') >= 0) return 'bienheureux';
      if (sr.indexOf('human_will') >= 0) return 'volonté humaine';
      if (sr.indexOf('worker') >= 0) return 'ouvrier';
      if (sr.indexOf('observer') >= 0) return 'observateur';
      if (sr.indexOf('child') >= 0) return 'enfant';
      if (sr.indexOf('creatures') >= 0 || sr.indexOf('collective') >= 0 || sr.indexOf('future_creatures') >= 0) return 'créatures';
      if (sr.indexOf('creature') >= 0 || sr.indexOf('created_voice') >= 0) return 'créature';
      return 'âme';
    }
    if (sp === 'PERSONIFIED_VOICE') {
      if (sr.indexOf('sun') >= 0) return 'soleil';
      if (sr.indexOf('divine_will') >= 0 || sr.indexOf('divine_will_personified') >= 0) return 'Volonté Divine';
      if (sr.indexOf('divine_love') >= 0) return 'Amour divin';
      if (sr.indexOf('sufferings') >= 0) return 'souffrances';
      if (sr.indexOf('attributes') >= 0) return 'attributs divins';
      if (sr.indexOf('good_acts') >= 0 || sr.indexOf('created_acts') >= 0 || sr.indexOf('created_act') >= 0 || sr.indexOf('divine_acts') >= 0) return 'actes';
      if (sr.indexOf('created_works') >= 0 || sr.indexOf('created_work') >= 0 || sr.indexOf('divine_works') >= 0) return 'œuvres';
      if (sr.indexOf('created_things') >= 0 || sr.indexOf('creation') >= 0 || sr.indexOf('celestial_orchestra') >= 0) return 'Création';
      if (sr.indexOf('created_soul') >= 0) return 'âme créée';
      if (sr.indexOf('collective_divinity') >= 0) return 'Divinité';
      return 'voix personnifiée';
    }
    if (sp === 'OTHER') {
      if (sr.indexOf('collective_divinity') >= 0) return 'Entité Suprême';
      if (sr.indexOf('adam') >= 0) return 'Adam';
      if (sr.indexOf('angelic') >= 0) return 'anges';
      if (sr.indexOf('blessed') >= 0) return 'Bienheureux';
      if (sr.indexOf('celestial') >= 0) return 'cour céleste';
      if (sr.indexOf('church_leaders') >= 0) return 'responsables de l’Église';
      if (sr.indexOf('church') >= 0) return 'voix ecclésiale';
      if (sr.indexOf('future_readers') >= 0) return 'lecteurs futurs';
      if (sr.indexOf('humanity') >= 0) return 'humanité';
      if (sr.indexOf('hypothetical_father') >= 0) return 'père';
      if (sr.indexOf('creator_response') >= 0) return 'Créateur';
      if (sr.indexOf('creator_creature') >= 0 || sr.indexOf('joint_creator') >= 0 || sr.indexOf('mutual_creator') >= 0) return 'Créateur et créature';
      if (sr.indexOf('created') >= 0) return 'Création';
      if (sr.indexOf('prayer') >= 0) return 'voix collective';
      if (sr.indexOf('interlocutor') >= 0) return 'interlocuteur';
      return 'autre voix';
    }
    return 'autre voix';
  }

  function quotedVoiceLabels(run) {
    var display = String((run && run.speaker) || '').toUpperCase();
    if (display === 'MARIE') display = 'MARY';
    var out = [], seen = {};
    var voices = (run && run.semantic_voices) || [];
    for (var i = 0; i < voices.length; i++) {
      var sem = String(voices[i].speaker || '').toUpperCase();
      if (sem === 'MARIE') sem = 'MARY';
      if (!sem || sem === display) continue;
      var label = semanticVoiceLabel(sem, voices[i].subrole || '');
      if (!seen[label]) { seen[label] = true; out.push(label); }
    }
    return out;
  }

  // Stage A accessibility authority: AT attribution is derived from the exact same
  // presentation speaker + natural-language quoted-voice model used by Repères.
  // This does not widen Repères product scope and does not mutate semantic metadata.
  function attributionText(run, quotedLabels) {
    var display = M.normSpeaker(run && run.speaker) === 'marie' ? 'Marie' : 'Jésus';
    var labels = Array.isArray(quotedLabels) ? quotedLabels : quotedVoiceLabels(run);
    if (!labels.length) return display + '.';
    return display + '. ' + (labels.length === 1 ? 'Voix citée : ' : 'Voix citées : ') + labels.join(' · ') + '.';
  }

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  var OPEN = '«“„"';
  var CLOSE = '»”"';
  // LDC-GR4 — display-only handling for direct-speech guillemets that sit
  // immediately OUTSIDE the validated speaker span. Canonical text is never changed.
  // Outer delimiters of validated direct Jesus/Mary speech are display-suppressed.
  // Nested/internal quotation punctuation is preserved through quotation-depth guards.
  function isNestedStart(r) { return !!r && (Number(r.start_quotation_depth || 0) >= 2 || Number(r.start_quote_depth || 0) >= 2); }
  function isNestedEnd(r) { return !!r && (Number(r.end_quotation_depth || 0) >= 2 || Number(r.end_quote_depth || 0) >= 2); }
  function splitNarrativeBoundaryDelimiters(t, prevRun, nextRun, hideOuter) {
    if (!hideOuter) return { lead: '', core: t, trail: '' };
    var lead = '', trail = '', core = t;

    // Closing delimiter immediately after validated Jesus/Mary speech.
    // The speaker styling is already the visible quotation cue, so the redundant
    // outer guillemet is suppressed for block and inline speech alike.
    if (prevRun && prevRun.styled && !isNestedEnd(prevRun)) {
      var cm = core.match(/^(\s*[»”"])/);
      if (cm) {
        lead = cm[1];
        core = core.slice(lead.length);
        // Quote-only suffix: hide residual whitespace too, so no empty visual line remains.
        if (/^\s*$/.test(core)) { lead += core; core = ''; }
      }
    }

    // Opening delimiter immediately before validated Jesus/Mary speech.
    // Hide only the delimiter token itself; all preceding narrative remains.
    // Internal quotation marks inside a speech run remain untouched.
    if (nextRun && nextRun.styled && !isNestedStart(nextRun)) {
      var om = core.match(/([«“„"]\s*)$/);
      if (om) {
        trail = om[1];
        core = core.slice(0, core.length - om[1].length);
      }
    }
    return { lead: lead, core: core, trail: trail };
  }

  // RA4B — narrow corrective handling for boundary delimiters that are not
  // immediately adjacent to the validated speaker span. This is display-only:
  // canonical text, speaker offsets and paragraph IDs stay unchanged.
  function directAttributionBeforeOpening(t, pos) {
    var prefix = t.slice(0, pos).trim();
    // Conservative attribution vocabulary. This intentionally excludes generic
    // reported-speech introductions such as "On dira toujours :".
    return /(?:Jésus|Jesus|Il|Elle|Marie|Maman|Seigneur)[^.!?;:]{0,48}(?:dit|répondit|répliqua|ajouta|reprit|poursuivit|sourit)\s*:\s*$/i.test(prefix);
  }

  function extraNarrativeDelimiterOffsets(r, prevRun, nextRun, hideOuter) {
    if (!hideOuter) return [];
    var out = [];
    // 1) A validated direct turn can begin after a short unstyled lexical prefix
    // inside the guillemets when the source speaker span starts a few characters
    // late. Hide only the opening guillemet when an explicit Jesus/Mary
    // attribution proves the turn. Nested/reported quotations are left visible.
    if (nextRun && nextRun.styled && !isNestedStart(nextRun)) {
      var oi = r.text.lastIndexOf('«');
      if (oi >= 0) {
        var gap = r.text.slice(oi + 1);
        if (/[0-9A-Za-zÀ-ɏ]/.test(gap) &&
            !/[«»“”„"]/.test(gap) &&
            gap.length <= 40 && directAttributionBeforeOpening(r.text, oi)) {
          out.push(r.start + oi);
        }
      }
    }
    // 2) Speaker offsets sometimes stop just before terminal punctuation, e.g.
    // "... Volonté.»". Hide the closing guillemet while preserving the punctuation.
    if (prevRun && prevRun.styled && !isNestedEnd(prevRun)) {
      var ci = r.text.indexOf('»');
      if (ci >= 0) {
        var beforeClose = r.text.slice(0, ci);
        if (beforeClose.length > 0 && !/^\s*$/.test(beforeClose) &&
            !/[0-9A-Za-zÀ-ɏ]/.test(beforeClose) &&
            !/[«»“”„"]/.test(beforeClose) && beforeClose.length <= 8) {
          out.push(r.start + ci);
        }
      }
    }
    return out.filter(function (v, ix, a) { return a.indexOf(v) === ix; }).sort(function(a,b){return a-b;});
  }

  function emitRangeWithExtraHidden(atoms, start, end, lead, trail, hiddenOffsets) {
    if (!hiddenOffsets || !hiddenOffsets.length) return emitRange(atoms, start, end, lead, trail);
    var list = hiddenOffsets.filter(function(p){ return p >= start && p < end; }).sort(function(a,b){return a-b;});
    if (!list.length) return emitRange(atoms, start, end, lead, trail);
    var out = '', cur = start;
    for (var i = 0; i < list.length; i++) {
      var p = list[i];
      if (p > cur) {
        var left = emitRange(atoms, cur, p, cur === start ? lead : 0, 0);
        if (left === null) return null;
        out += left;
      }
      var mid = emitRange(atoms, p, p + 1, 1, 0);
      if (mid === null) return null;
      out += mid;
      cur = p + 1;
    }
    if (cur < end) {
      var right = emitRange(atoms, cur, end, 0, trail);
      if (right === null) return null;
      out += right;
    }
    return out;
  }

  function plainNarrativeWithExtraHidden(t, np, absoluteStart, hiddenOffsets) {
    var hidden = {};
    for (var i = 0; i < (hiddenOffsets || []).length; i++) hidden[hiddenOffsets[i] - absoluteStart] = true;
    var leadLen = np.lead.length, trailLen = np.trail.length;
    var out = '', hiddenMode = null, buf = '';
    function flush() {
      if (!buf) return;
      out += hiddenMode ? '<span class="speech-outer-delimiter" aria-hidden="true">' + esc(buf) + '</span>' : esc(buf);
      buf = '';
    }
    for (var j = 0; j < t.length; j++) {
      var h = j < leadLen || j >= t.length - trailLen || !!hidden[j];
      if (hiddenMode === null) hiddenMode = h;
      if (h !== hiddenMode) { flush(); hiddenMode = h; }
      buf += t[j];
    }
    flush();
    return out;
  }

  // RA9 — uncoloured direct speech remains normal prose, but semantic run
  // boundaries must not create accidental visual paragraph boundaries.
  function isUnstyledDirectRun(r) {
    return !!r && !r.styled && r.role && r.role !== 'NARRATIVE';
  }
  function leadingClosingDelimiterLength(t) {
    // Return the canonical prefix through the first closing quote when everything
    // before it is non-lexical punctuation/space. This keeps the closing quote
    // attached to the direct speech that precedes it.
    var limit = Math.min(String(t || '').length, 12);
    for (var i = 0; i < limit; i++) {
      var ch = t[i];
      if (/[0-9A-Za-zÀ-ɏ]/.test(ch) || OPEN.indexOf(ch) !== -1) return 0;
      if (CLOSE.indexOf(ch) !== -1) return i + 1;
    }
    return 0;
  }
  function paragraphBreakHtml() {
    return '<span class="speech-paragraph-break" aria-hidden="true"></span>';
  }
  function renderNarrativeSlice(r, start, end, prevRun, nextRun, atoms, DM, hideOuter) {
    var local = { start:start, end:end, text:r.text.slice(start-r.start, end-r.start) };
    var display = local.text;
    if (atoms && DM) {
      var ra = DM.atomsForRange(atoms, start, end);
      display = '';
      for (var q = 0; q < ra.length; q++) display += ra[q].text;
    }
    var np = splitNarrativeBoundaryDelimiters(display, prevRun, nextRun, hideOuter);
    var extraHidden = extraNarrativeDelimiterOffsets(local, prevRun, nextRun, hideOuter);
    var html = atoms ? emitRangeWithExtraHidden(atoms, start, end, np.lead.length, np.trail.length, extraHidden) : null;
    if (html === null) html = plainNarrativeWithExtraHidden(local.text, np, start, extraHidden);
    return { html:html, core:np.core };
  }

  // Split a run into [openDelim, core, closeDelim] without dropping anything.
  function splitOuterDelimiters(t) {
    var a = 0, b = t.length;
    var lead = '', trail = '';
    while (a < b && /\s/.test(t[a])) a++;
    if (a < b && OPEN.indexOf(t[a]) !== -1) { lead = t.slice(0, a + 1); a = a + 1; }
    else { lead = ''; a = 0; }
    var e = b;
    while (e > a && /\s/.test(t[e - 1])) e--;
    if (e > a && CLOSE.indexOf(t[e - 1]) !== -1) { trail = t.slice(e - 1); b = e - 1; }
    else { trail = ''; b = t.length; }
    return { lead: lead, core: t.slice(a, b), trail: trail };
  }

  /* Emit a canonical range as DISPLAY text (structural-dash handoff v2).
     Suppressed and replaced tokens become spans carrying their canonical
     [cs,ce), so nothing downstream has to re-derive offsets from rendered text.
     `lead`/`trail` are display-space lengths of an outer speech delimiter. */
  function emitRange(atoms, start, end, lead, trail) {
    var DM = root.LDCDisplayMap;
    if (!DM || !atoms) {                       // no map loaded — canonical passthrough
      return null;
    }
    var ra = DM.atomsForRange(atoms, start, end);
    var total = 0, i;
    for (i = 0; i < ra.length; i++) total += ra[i].text.length;
    lead = lead || 0; trail = trail || 0;
    var out = '', d = 0;
    for (i = 0; i < ra.length; i++) {
      var a = ra[i];
      if (a.kind !== 'canonical') {
        out += '<span class="dtok dtok-' + (a.kind === 'suppressed' ? 'suppressed' : 'replaced') +
               '" data-cs="' + a.cs + '" data-ce="' + a.ce + '"' +
               (a.kind === 'suppressed' ? ' aria-hidden="true"' : '') +
               ' data-decision="' + esc(a.decision_id || '') + '">' + esc(a.text) + '</span>';
        d += a.text.length;
        continue;
      }
      // split this canonical atom across the lead / core / trail zones
      var txt = a.text, base = d, off = 0;
      while (off < txt.length) {
        var pos = base + off, zoneEnd;
        if (pos < lead)                 zoneEnd = Math.min(txt.length, lead - base);
        else if (pos >= total - trail)  zoneEnd = txt.length;
        else                            zoneEnd = Math.min(txt.length, (total - trail) - base);
        var chunk = txt.slice(off, zoneEnd);
        if (pos < lead || pos >= total - trail) {
          out += '<span class="speech-outer-delimiter" aria-hidden="true">' + esc(chunk) + '</span>';
        } else {
          out += esc(chunk);
        }
        off = zoneEnd;
      }
      d += txt.length;
    }
    return out;
  }

  function renderSpeechModel(model, opts) {
    opts = opts || {};
    var showLabels = !!opts.showLabels;         // labels emitted; Repères CSS controls visibility
    var hideOuter  = opts.hideOuterDelimiters !== false;
    var paraId     = opts.paraId || '';
    var flowMemberIndex = Number.isInteger(opts.flowMemberIndex) ? opts.flowMemberIndex : 0;
    var atoms      = opts.atoms || null;        // display projection, may be absent
    var DM         = root.LDCDisplayMap;
    var html = '';
    for (var i = 0; i < model.runs.length; i++) {
      var r = model.runs[i];
      if (!r.styled) {
        var prevRun = i > 0 ? model.runs[i - 1] : null;
        var nextRun = i + 1 < model.runs.length ? model.runs[i + 1] : null;

        // If normal-prose direct speech just ended, keep its closing guillemet
        // with that speech, then start resumed narration as a new visual paragraph.
        // No canonical character or semantic run is changed.
        var closePrefixLen = (r.role === 'NARRATIVE' && isUnstyledDirectRun(prevRun))
          ? leadingClosingDelimiterLength(r.text) : 0;
        if (closePrefixLen && /[0-9A-Za-zÀ-ɏ]/.test(r.text.slice(closePrefixLen))) {
          var closePart = renderNarrativeSlice(r, r.start, r.start + closePrefixLen,
                                               prevRun, null, atoms, DM, hideOuter);
          var resumed = renderNarrativeSlice(r, r.start + closePrefixLen, r.end,
                                             null, nextRun, atoms, DM, hideOuter);
          html += closePart.html + paragraphBreakHtml() +
                  '<span class="speech-post-narrative">' + resumed.html + '</span>';
          continue;
        }

        var whole = renderNarrativeSlice(r, r.start, r.end, prevRun, nextRun,
                                         atoms, DM, hideOuter);
        var postSpeechNarrative = prevRun && prevRun.styled && !isNestedEnd(prevRun) &&
          (prevRun.presentation === 'block' || prevRun.isContinuation) &&
          /[0-9A-Za-zÀ-ɏ]/.test(whole.core || '');
        // The break marker, rather than a block wrapper, creates the visual
        // paragraph start. The following normal-prose speaker run therefore
        // remains inline with an attribution/opening guillemet that precedes it.
        html += postSpeechNarrative
          ? paragraphBreakHtml() + '<span class="speech-post-narrative">' + whole.html + '</span>'
          : whole.html;
        continue;
      }
      var cls = M.normSpeaker(r.speaker) === 'marie' ? 'speech-marie' : 'speech-jesus';
      var label = M.normSpeaker(r.speaker) === 'marie' ? 'Marie' : 'Jésus';
      // A run linked across a flow boundary keeps ONE logical id; only its first
      // fragment emits the speaker label and block-start spacing (§6.4).
      var runId = r.runId || (paraId + '#R' + i);
      var isCont = !!r.isContinuation;
      var isInlineFlowHead = !!r.visualContinuesToNext && !isCont;
      // A flow-linked head that must continue visually cannot itself be a block:
      // a block would create an unwanted END boundary.  If visible material
      // precedes the head, preserve the required speech START boundary with the
      // existing one-sided paragraph-break marker instead.
      if (isInlineFlowHead && (i > 0 || flowMemberIndex > 0)) html += paragraphBreakHtml();
      // outer delimiters are decided on the DISPLAY text, since a mapped token
      // may change what the run visually starts or ends with
      var runDisplay = r.text;
      if (atoms && DM) {
        var ra = DM.atomsForRange(atoms, r.start, r.end);
        runDisplay = '';
        for (var q = 0; q < ra.length; q++) runDisplay += ra[q].text;
      }
      // Outer direct-speech delimiters are redundant once a validated Jesus/Mary
      // run is styled. Suppress the run's own outer delimiters for every styled
      // run; nested/internal quotation marks remain ordinary characters inside
      // the run and therefore remain visible.
      var hideLeadDelim = hideOuter && !isNestedStart(r);
      var hideTrailDelim = hideOuter && !isNestedEnd(r);
      var parts = (hideLeadDelim || hideTrailDelim)
        ? splitOuterDelimiters(runDisplay)
        : { lead: '', core: runDisplay, trail: '' };
      var inner = null;
      if (atoms) {
        inner = emitRange(atoms, r.start, r.end,
                          hideLeadDelim ? parts.lead.length : 0,
                          hideTrailDelim ? parts.trail.length : 0);
      }
      if (inner === null) {
        inner = '';
        if (parts.lead)  inner += '<span class="speech-outer-delimiter"' +
                                  (hideLeadDelim ? ' aria-hidden="true"' : '') + '>' + esc(parts.lead) + '</span>';
        inner += esc(parts.core);
        if (parts.trail) inner += '<span class="speech-outer-delimiter"' +
                                  (hideTrailDelim ? ' aria-hidden="true"' : '') + '>' + esc(parts.trail) + '</span>';
      }
      var quotedLabels = quotedVoiceLabels(r);
      var quotedVoiceHtml = '';
      var attributionSrHtml = !isCont
        ? '<span class="speech-attribution-sr">' + esc(attributionText(r, quotedLabels)) + '</span>'
        : '';
      if (showLabels && !isCont && quotedLabels.length) {
        var prefix = quotedLabels.length === 1 ? 'voix citée : ' : 'voix citées : ';
        quotedVoiceHtml = '<span class="speech-quoted-voice" aria-hidden="true" data-quoted-voices="' + esc(quotedLabels.join('|')) + '">' +
                          prefix + esc(quotedLabels.join(' · ')) + '</span>';
      }
      html += '<span class="' + cls + ' speech-run speech-' +
              (isCont ? 'inline speech-run-continuation' : (isInlineFlowHead ? 'inline speech-run-flow-head' : r.presentation)) + '"' +
              ' data-speech-run-id="' + esc(runId) + '"' +
              (isCont ? ' data-run-continuation="1"' : '') +
              (isInlineFlowHead ? ' data-run-flow-head="1" data-visual-policy="continuous_prose"' : '') +
              ' data-run-start="' + r.start + '" data-run-end="' + r.end + '">' +
              attributionSrHtml +
              (showLabels && !isCont ? '<span class="speech-label lbl-' +
                 (M.normSpeaker(r.speaker) === 'marie' ? 'marie' : 'jesus') + '" aria-hidden="true">' + label + '</span>' +
                 quotedVoiceHtml +
                 (r.confidence ? '<span class="speech-conf" aria-hidden="true" data-confidence="' + esc(r.confidence) + '">' +
                   (r.confidence === 'high' ? 'confiance élevée' : r.confidence === 'medium' ? 'confiance moyenne' : 'confiance faible') +
                  '</span>' : '') : '') +
              inner + '</span>';
    }
    return html;
  }

  M.renderSpeechModel = renderSpeechModel;
  M.semanticVoiceLabel = semanticVoiceLabel;
  M.quotedVoiceLabels = quotedVoiceLabels;
  M.attributionText = attributionText;
  M.splitOuterDelimiters = splitOuterDelimiters;
  M.splitNarrativeBoundaryDelimiters = splitNarrativeBoundaryDelimiters;
  M.escapeForRender = esc;
  M.extraNarrativeDelimiterOffsets = extraNarrativeDelimiterOffsets;
})(typeof window !== 'undefined' ? window : globalThis);
