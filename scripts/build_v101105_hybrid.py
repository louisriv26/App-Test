#!/usr/bin/env python3
from __future__ import annotations
import csv, json, hashlib, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path
from copy import deepcopy
from datetime import datetime
sys.path.insert(0,'/mnt/data/v101105_execution')
from common import sha_file, parse_const, replace_const, text_registry, write_csv

ROOT=Path('/mnt/data')
BASE=ROOT/'L24H_v101103_GITHUB_DEPLOY_DIVINE_QUOTE_PRESENTATION_REGRESSION_REPAIR_R1_LOCKED.zip'
BASE_SHA='d08fa70a4931f8c2e997bc8bae46a8292ed9b14725346727852361a84cfdb664'
WIT=ROOT/'_v101101/luisa_24_heures.html'
PRE=ROOT/'v101105_execution/preedit_evidence/reports'
OUTROOT=ROOT/'v101105_execution/run2'
TREE=OUTROOT/'tree'
VERSION='v101.105'; STAGE='NATIVE_24H_PARAGRAPH_LDC_SEMANTIC_HYBRID_PRESENTATION_R1'; CACHE='luisa-24h-v101-105'; DATE='2026-08-23'
ZIP_NAME='L24H_v101105_GITHUB_DEPLOY_NATIVE_24H_LDC_SEMANTIC_HYBRID_PRESENTATION_R1_LOCKED.zip'
FINAL=ROOT/ZIP_NAME

PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT']

def sha_bytes(b:bytes):return hashlib.sha256(b).hexdigest()
def jsha(o):return sha_bytes(json.dumps(o,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode())
def fail(msg): raise RuntimeError(msg)
def stable_zip(tree:Path,out:Path):
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(x for x in tree.rglob('*') if x.is_file()):
            rel=p.relative_to(tree).as_posix(); data=p.read_bytes()
            zi=zipfile.ZipInfo(rel,(2026,8,23,0,0,0)); zi.compress_type=zipfile.ZIP_DEFLATED; zi.external_attr=(0o644&0xFFFF)<<16; zi.create_system=3
            z.writestr(zi,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)

def ordered_next_map(C,L):
    nxt={}
    def chain(ids):
        for a,b in zip(ids,ids[1:]): nxt[a]=b
    for h in C['hours']:
        chain([p['id'] for p in h.get('paragraphs',[])])
        chain([p['id'] for p in h.get('reflections',[])])
        for sub in h.get('subsections',[]): chain([p['id'] for p in sub.get('paragraphs',[])])
    for pr in C.get('prayers',[]): chain([p['id'] for p in pr.get('paragraphs',[])])
    for sec in C.get('sections',[]): chain([p['id'] for p in sec.get('paragraphs',[])])
    for item in L:
        if item.get('type')=='library_group':continue
        nums=item.get('body_stable_numbers'); ids=[]
        for i,_ in enumerate(item.get('body',[])):
            n=int(nums[i]) if nums and i<len(nums) else i+1
            ids.append(item['id']+'.BODY.P'+str(n).zfill(3))
        chain(ids)
    return nxt

def patch_html(src103:str,src101:str,quote_rows:list[dict]):
    C=parse_const(src103,'CORPUS');L=parse_const(src103,'TEXT_LIBRARY');T=text_registry(C,L)
    P103=parse_const(src103,'SPEECH_PRESENTATION_PROJECTION'); Topo103=parse_const(src103,'VISIBLE_PARAGRAPH_TOPOLOGY')
    B101=parse_const(src101,'SPEECH_END_VISUAL_BREAKS'); X101=parse_const(src101,'SPEECH_CROSS_RECORD_VISUAL_BREAKS')
    # All 139 native v101.101 speech-end visual boundaries, and no v101.102+ speech-start-only breaks.
    P=deepcopy(P103)
    for pid in P:
        P[pid]['breaks']=sorted(set(int(x) for x in B101.get(pid,[])))
    missing=[pid for pid in B101 if pid not in P]
    if missing: fail('native speech-end targets missing from v101.103 semantic projection: '+repr(missing[:5]))
    # Exhaustively derive quote-edge integrity joins for every visible cross-record quotation whose opening guillemet is terminal in its storage record.
    nxt=ordered_next_map(C,L); joins=[]; join_rows=[]
    for r in quote_rows:
        if r.get('char')!='«' or str(r.get('role','')).endswith('_HIDE') or not r.get('paired_target') or r['paired_target']==r['target_id']: continue
        pid=r['target_id']; off=int(r['offset'])
        if not T[pid][off+1:].strip():
            np=nxt.get(pid)
            if not np: fail('visible terminal opening guillemet has no next record: '+pid)
            joins.append([pid,np])
            join_rows.append({'open_target':pid,'next_target':np,'close_target':r['paired_target'],'role':r['role'],'open_offset':off,'action':'QUOTE_EDGE_INTEGRITY_JOIN','reason':'Visible opening guillemet is terminal in record; remove only the inter-record boundary before first lexical content.'})
    # Locked expected semantic population from v101.103 ledger.
    if len(joins)!=24: fail(f'expected 24 visible terminal-opening quote joins, got {len(joins)}')
    Topo={'local_breaks':{pid:list(B101[pid]) for pid in sorted(B101) if B101[pid]},'cross_record_breaks':deepcopy(X101),'cross_record_joins':joins}
    # Exact semantic layers are preserved.
    src=replace_const(src103,'SPEECH_PRESENTATION_PROJECTION',P)
    src=replace_const(src,'VISIBLE_PARAGRAPH_TOPOLOGY',Topo)
    src=src.replace("const APP_VERSION = 'v101.103';",f"const APP_VERSION = '{VERSION}';",1)
    src=src.replace("const APP_EVIDENCE_STAGE = 'DIVINE_QUOTE_PRESENTATION_REGRESSION_REPAIR_R1';",f"const APP_EVIDENCE_STAGE = '{STAGE}';",1)
    src=src.replace("const BUILD_DATE = '2026-08-22'; // v101.103 / divine quote presentation regression repair",f"const BUILD_DATE = '{DATE}'; // v101.105 / native-24H + LDC semantic hybrid presentation",1)
    src=src.replace('// v101.103 — quote-role adjudication + visible-guillemet boundary repair. Canonical SPEECH_DATA stays immutable.','// v101.105 — native 24H paragraph topology + v101.103 LDC semantic quotation/speaker projection. Canonical source and SPEECH_DATA stay immutable.',1)
    # Narrow CSS: non-breaking presentation joiner, no canonical/source mutation.
    cssneedle='.ldc-flow-joiner{display:inline;white-space:pre;}'
    cssrepl=cssneedle+'\n.quote-edge-integrity-joiner{display:inline;white-space:nowrap;}'
    if cssneedle not in src: fail('CSS joiner anchor missing')
    src=src.replace(cssneedle,cssrepl,1)
    # Narrow runtime helpers: topology-driven cross-record joins. No source-flow authority mutation.
    anchor="function getLdcFlowBlocks(itemId) {\n  const rows = (typeof LDC_LIBRARY_FLOW_LAYOUT !== 'undefined' && LDC_LIBRARY_FLOW_LAYOUT) ? LDC_LIBRARY_FLOW_LAYOUT[itemId] : null;\n  return Array.isArray(rows) ? rows : [];\n}\n"
    if anchor not in src: fail('getLdcFlowBlocks anchor missing')
    helper=anchor+r'''// v101.105 — presentation-only quote-edge joins. These pairs never alter LDC_LIBRARY_FLOW_LAYOUT or canonical records.
function getQuoteEdgeIntegrityJoinPairs() {
  const rows = (typeof VISIBLE_PARAGRAPH_TOPOLOGY !== 'undefined' && VISIBLE_PARAGRAPH_TOPOLOGY && Array.isArray(VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_joins)) ? VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_joins : [];
  return rows.filter(pair => Array.isArray(pair) && pair.length === 2 && pair[0] && pair[1]);
}
function hasQuoteEdgeIntegrityJoin(prevId,nextId) {
  return getQuoteEdgeIntegrityJoinPairs().some(pair => pair[0] === prevId && pair[1] === nextId);
}
function getQuoteEdgeIntegrityJoinBlock(item, bodyItems, startIndex) {
  if (!item || !Array.isArray(bodyItems) || !(startIndex >= 0) || startIndex >= bodyItems.length - 1) return null;
  const firstId = makeLibraryParaId(item.id,startIndex);
  const nextId = makeLibraryParaId(item.id,startIndex+1);
  if (!hasQuoteEdgeIntegrityJoin(firstId,nextId)) return null;
  let end = startIndex + 2;
  while (end < bodyItems.length && hasQuoteEdgeIntegrityJoin(makeLibraryParaId(item.id,end-1),makeLibraryParaId(item.id,end))) end++;
  const intra={}, intraActions={};
  for (let i=startIndex;i<end;i++) {
    const pid=makeLibraryParaId(item.id,i), cuts=getPresentationLocalBreaks(pid);
    if (cuts.length) {
      intra[String(i)]=cuts.slice(); intraActions[String(i)]={};
      cuts.forEach(cut => { intraActions[String(i)][String(cut)]='presentation_break'; });
    }
  }
  return {entry_id:'QUOTE_EDGE_INTEGRITY:'+firstId,start:startIndex,end:end,break_before:[],break_before_actions:{},intra:intra,intra_actions:intraActions,quote_edge_integrity_join:true};
}
'''
    src=src.replace(anchor,helper,1)
    # Existing source-flow renderer: quote-edge overlay wins only at the exact explicit pair; source flow data itself stays frozen.
    old=r'''      if (before.has(i+1)) {
        const action=String(beforeActions[String(i+1)]||beforeActions[i+1]||'paragraph_break');
        html += `<span class="ldc-visual-paragraph-break ldc-ra18-boundary ldc-ra18-${escHtml(action)}" aria-hidden="true" data-ldc-boundary-action="${escHtml(action)}"></span>`;
      } else {
        const nextPid = String(idGetter(rows[i + 1], i + 1) || '');
        if (hasSpeechCrossRecordVisualBreak(pid, nextPid)) {
          html += `<span class="speech-end-visual-break speech-presentation-visual-break speech-cross-record-visual-break" aria-hidden="true" data-speech-cross-record-break="${escHtml(pid)}→${escHtml(nextPid)}"></span>`;
        } else html += '<span class="ldc-flow-joiner" aria-hidden="true"> </span>';
      }'''
    new=r'''      const nextPid = String(idGetter(rows[i + 1], i + 1) || '');
      if (hasQuoteEdgeIntegrityJoin(pid,nextPid)) {
        html += '<span class="ldc-flow-joiner quote-edge-integrity-joiner" aria-hidden="true">&nbsp;</span>';
      } else if (before.has(i+1)) {
        const action=String(beforeActions[String(i+1)]||beforeActions[i+1]||'paragraph_break');
        html += `<span class="ldc-visual-paragraph-break ldc-ra18-boundary ldc-ra18-${escHtml(action)}" aria-hidden="true" data-ldc-boundary-action="${escHtml(action)}"></span>`;
      } else {
        if (hasSpeechCrossRecordVisualBreak(pid, nextPid)) {
          html += `<span class="speech-end-visual-break speech-presentation-visual-break speech-cross-record-visual-break" aria-hidden="true" data-speech-cross-record-break="${escHtml(pid)}→${escHtml(nextPid)}"></span>`;
        } else html += '<span class="ldc-flow-joiner" aria-hidden="true"> </span>';
      }'''
    if old not in src: fail('renderLdcFlowSurface anchor missing')
    src=src.replace(old,new,1)
    # Ordinary library records: synthesize a flow surface only when explicit quote-edge join metadata demands it.
    old1="""      const t=bodyItems[i], block=flowByStart.get(i);\n      if (block) {\n        paras += renderLdcFlowSurface(bodyItems,block,(x)=>x,(_x,j)=>makeLibraryParaId(item.id,j),'library_text','library-para-block');\n        i=Number(block.end)-1; continue;\n      }"""
    new1="""      const t=bodyItems[i], block=flowByStart.get(i), quoteJoinBlock=getQuoteEdgeIntegrityJoinBlock(item,bodyItems,i);\n      if (block) {\n        paras += renderLdcFlowSurface(bodyItems,block,(x)=>x,(_x,j)=>makeLibraryParaId(item.id,j),'library_text','library-para-block');\n        i=Number(block.end)-1; continue;\n      }\n      if (quoteJoinBlock) {\n        paras += renderLdcFlowSurface(bodyItems,quoteJoinBlock,(x)=>x,(_x,j)=>makeLibraryParaId(item.id,j),'library_text','library-para-block');\n        i=Number(quoteJoinBlock.end)-1; continue;\n      }"""
    if old1 not in src: fail('indexed library loop anchor missing')
    src=src.replace(old1,new1,1)
    old2="""    const block=flowByStart.get(i);\n    if (block) {\n      paras += renderLdcFlowSurface(bodyItems,block,(x)=>x,(_x,j)=>makeLibraryParaId(item.id,j),'library_text','library-para-block');\n      i=Number(block.end)-1; continue;\n    }\n    paras += renderOrdinaryAt(bodyItems[i],i);"""
    new2="""    const block=flowByStart.get(i), quoteJoinBlock=getQuoteEdgeIntegrityJoinBlock(item,bodyItems,i);\n    if (block) {\n      paras += renderLdcFlowSurface(bodyItems,block,(x)=>x,(_x,j)=>makeLibraryParaId(item.id,j),'library_text','library-para-block');\n      i=Number(block.end)-1; continue;\n    }\n    if (quoteJoinBlock) {\n      paras += renderLdcFlowSurface(bodyItems,quoteJoinBlock,(x)=>x,(_x,j)=>makeLibraryParaId(item.id,j),'library_text','library-para-block');\n      i=Number(quoteJoinBlock.end)-1; continue;\n    }\n    paras += renderOrdinaryAt(bodyItems[i],i);"""
    if old2 not in src: fail('ordinary library loop anchor missing')
    src=src.replace(old2,new2,1)
    # Mon Espace / export paragraph counting must consume the same cross-record join topology.
    oldcount=r'''function countCurrentVisibleParagraphsForHighlightItems(items) {
  const keys=new Set();
  for (const item of (items||[])) {
    const pid=item.paraId || item.pid; const h=item.hl || item.h || {}; const info=getTargetInfo(pid); if(!info) continue;
    const start=Number(h.start_offset ?? h.start ?? 0), end=Number(h.end_offset ?? h.end ?? info.text.length);
    const cuts=getPresentationLocalBreaks(pid); const bounds=[0].concat(cuts).concat([info.text.length]);
    for(let i=0;i<bounds.length-1;i++) { if(end>bounds[i] && start<bounds[i+1]) keys.add(pid+':'+bounds[i]+'-'+bounds[i+1]); }
  }
  return keys.size;
}'''
    newcount=r'''function getVisibleParagraphPieceGroupKey(paraId,start,end) {
  let pid=paraId, a=start, b=end, guard=0;
  const joins=getQuoteEdgeIntegrityJoinPairs();
  while (guard++ < 64 && a === 0) {
    const pair=joins.find(x => x[1] === pid); if(!pair) break;
    const prevId=pair[0], prevText=getFullParaText(prevId)||'', prevCuts=getPresentationLocalBreaks(prevId);
    const prevStart=prevCuts.length ? prevCuts[prevCuts.length-1] : 0;
    pid=prevId; a=prevStart; b=prevText.length;
  }
  return pid+':'+a+'-'+b;
}
function countCurrentVisibleParagraphsForHighlightItems(items) {
  const keys=new Set();
  for (const item of (items||[])) {
    const pid=item.paraId || item.pid; const h=item.hl || item.h || {}; const info=getTargetInfo(pid); if(!info) continue;
    const start=Number(h.start_offset ?? h.start ?? 0), end=Number(h.end_offset ?? h.end ?? info.text.length);
    const cuts=getPresentationLocalBreaks(pid); const bounds=[0].concat(cuts).concat([info.text.length]);
    for(let i=0;i<bounds.length-1;i++) if(end>bounds[i] && start<bounds[i+1]) keys.add(getVisibleParagraphPieceGroupKey(pid,bounds[i],bounds[i+1]));
  }
  return keys.size;
}'''
    if oldcount not in src: fail('Mon Espace paragraph count anchor missing')
    src=src.replace(oldcount,newcount,1)
    return src,P,Topo,join_rows

def build_tree():
    if sha_file(BASE)!=BASE_SHA: fail('baseline hash mismatch')
    if OUTROOT.exists(): shutil.rmtree(OUTROOT)
    OUTROOT.mkdir(parents=True); TREE.mkdir()
    with zipfile.ZipFile(BASE) as z:z.extractall(TREE)
    src103=(TREE/'luisa_24_heures.html').read_text(encoding='utf8')
    src101=WIT.read_text(encoding='utf8')
    # Snapshot protected declarations before changes.
    before={n:parse_const(src103,n) for n in PROTECTED}
    qrows=list(csv.DictReader((TREE/'reports/quotation_role_ledger.csv').open(encoding='utf-8-sig')))
    patched,P,Topo,join_rows=patch_html(src103,src101,qrows)
    # Verify protected declarations byte/semantic identical after patch.
    after={n:parse_const(patched,n) for n in PROTECTED}
    if any(before[n]!=after[n] for n in PROTECTED): fail('protected declaration changed')
    (TREE/'index.html').write_text(patched,encoding='utf8');(TREE/'luisa_24_heures.html').write_text(patched,encoding='utf8')
    # Clean generated active evidence universe, then regenerate only current prepackage evidence.
    for d in ['reports','audit','scripts','metadata']:
        p=TREE/d
        if p.exists(): shutil.rmtree(p)
        p.mkdir(parents=True,exist_ok=True)
    # External/visual user evidence remains valid historical input, but copy with explicit current provenance.
    # Pre-edit witnesses created under strict script.
    for fn in ['v101101_native_visual_topology_witness.csv','v101101_native_visual_topology_witness.json','v101103_semantic_presentation_witness.json','v101103_quote_role_witness.csv','v101101_native_visual_topology_reconciliation.csv','v101101_native_visual_topology_reconciliation.json','v101101_native_visual_topology_reconciliation.md']:
        shutil.copy2(PRE/fn,TREE/'reports'/fn)
    # Current semantic quote role ledger = exact v101.103 approved semantics, copied as data witness (not a stale PASS report).
    shutil.copy2(ROOT/'v101105_execution/baseline103_full/reports/quotation_role_ledger.csv',TREE/'reports/quotation_role_ledger.csv')
    # Scope escalation authority from the user's explicit "do it" after hard stop.
    (TREE/'metadata'/'scope_escalation_authority.md').write_text('''# v101.105 narrow scope escalation authority\n\nOn 23 August 2026, after the strict pre-edit hard stop `FAIL_SCOPE_ESCALATION_REQUIRED`, the user explicitly instructed: **“do it”**.\n\nAuthorized expansion is limited to the renderer/topology capability required to implement `QUOTE_EDGE_INTEGRITY_JOIN` while preserving canonical text, protected declarations, raw `SPEECH_DATA`, IDs/order, RA19B flow authority, Apple exact-selection semantics, storage schema, and unrelated runtime behavior.\n''',encoding='utf8')
    # Build final hybrid decision ledger by augmenting preedit ledger with all 24 systematic joins.
    ledger=list(csv.DictReader((PRE/'hybrid_boundary_decision_ledger.csv').open(encoding='utf-8-sig')))
    # remove the single provisional join row to avoid duplicate; append full population
    ledger=[r for r in ledger if (r.get('\ufeffrecord_kind') or r.get('record_kind'))!='REQUIRED_QUOTE_EDGE_JOIN']
    fields=['record_kind','target','prev_id','next_id','offset','v101101_native_offset','v101103_break_evidence','classification','final_action','speaker_before','speaker_after','quote_role_around_boundary','RA19B_flow_action','reason','evidence_path']
    norm=[]
    for r in ledger:
        rr={k:(r.get(k) if k in r else r.get('\ufeff'+k,'')) for k in fields}; norm.append(rr)
    for j in join_rows:
        norm.append({'record_kind':'QUOTE_EDGE_INTEGRITY_JOIN','target':j['open_target'].split('.BODY.P')[0],'prev_id':j['open_target'],'next_id':j['next_target'],'offset':'','v101101_native_offset':'inter-record edge','v101103_break_evidence':'source-flow or ordinary block edge','classification':'QUOTE_EDGE_INTEGRITY_JOIN','final_action':'JOIN_PRESENTATION_ONLY','speaker_before':'','speaker_after':'','quote_role_around_boundary':j['role'],'RA19B_flow_action':'PRESERVED_UNCHANGED','reason':j['reason'],'evidence_path':'quotation_role_ledger.csv + canonical record order + user presentation contract'})
    write_csv(TREE/'reports/hybrid_boundary_decision_ledger.csv',norm,fields)
    write_csv(TREE/'reports/quote_edge_hybrid_reconciliation.csv',join_rows)
    # Protected diff evidence.
    prot=[]
    for n in PROTECTED: prot.append({'declaration':n,'before_sha256':jsha(before[n]),'after_sha256':jsha(after[n]),'status':'PASS' if before[n]==after[n] else 'FAIL'})
    write_csv(TREE/'reports/protected_data_diff_report.csv',prot)
    # Core summary prepackage facts only.
    summary={'version':VERSION,'stage':STAGE,'semantic_projection_targets':len(P),'local_break_targets':len(Topo['local_breaks']),'local_break_count':sum(len(v) for v in Topo['local_breaks'].values()),'cross_record_break_count':len(Topo['cross_record_breaks']),'quote_edge_integrity_join_count':len(Topo['cross_record_joins']),'quote_event_count':len(qrows),'unresolved_quote_roles':sum(1 for r in qrows if 'UNRESOLVED' in r.get('role','')),'protected_declarations_unchanged':all(x['status']=='PASS' for x in prot),'final_package_reopen_gate':'POST_PACKAGE_EXTERNAL','independent_reopen_gate':'POST_PACKAGE_EXTERNAL'}
    (TREE/'reports'/'presentation_projection_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (TREE/'reports'/'visible_paragraph_topology_report.md').write_text(f'''# v101.105 visible paragraph topology — prepackage\n\n- Native v101.101 speech-end local boundaries retained: **{summary['local_break_count']}**.\n- Native v101.101 cross-record speech-end boundaries retained: **{summary['cross_record_break_count']}**.\n- v101.102+ divine-speech-start-only boundaries retained: **0** by construction.\n- Explicit presentation-only visible quote-edge joins: **{summary['quote_edge_integrity_join_count']}**.\n- `LDC_LIBRARY_FLOW_LAYOUT` remains unchanged; quote-edge joins are a separate presentation overlay.\n- Renderer and Samsung whole-paragraph selection consume the same joined flow surface model.\n''',encoding='utf8')
    # Android group static map (presentation-specific pieces), enough to audit shared topology without inventing device evidence.
    T=text_registry(parse_const(patched,'CORPUS'),parse_const(patched,'TEXT_LIBRARY'))
    rows=[]
    join_prev={b:a for a,b in Topo['cross_record_joins']}
    def groupkey(pid,a,b):
        guard=0
        while a==0 and pid in join_prev and guard<64:
            prev=join_prev[pid]; cuts=Topo['local_breaks'].get(prev,[]); a=cuts[-1] if cuts else 0; b=len(T[prev]);pid=prev;guard+=1
        return f'{pid}:{a}-{b}'
    for pid,t in sorted(T.items()):
        cuts=Topo['local_breaks'].get(pid,[]);bounds=[0]+cuts+[len(t)]
        for a,b in zip(bounds,bounds[1:]):rows.append({'group_key':groupkey(pid,a,b),'para_id':pid,'start':a,'end':b,'text_sha256':sha_bytes(t[a:b].encode())})
    write_csv(TREE/'reports/android_visible_paragraph_groups.csv',rows)
    # Version/cache identity.
    ver=json.loads((TREE/'version.json').read_text(encoding='utf8'))
    ver.update({'app_version':VERSION,'build_date':DATE,'cache_name':CACHE,'release_scope':'Native 24H paragraph rhythm restored from exact v101.101 runtime witness while retaining v101.103 LDC-derived semantic speaker/quotation projection; all 24 visible terminal-opening cross-record quotation edges use explicit presentation-only integrity joins; renderer/Samsung share the same topology.','real_device_status':'v101.105 physical Samsung/iPhone/iPad/live-PWA/offline validation NOT_TESTED'})
    (TREE/'version.json').write_text(json.dumps(ver,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    mani=json.loads((TREE/'manifest.json').read_text(encoding='utf8'));mani['version']=VERSION;(TREE/'manifest.json').write_text(json.dumps(mani,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    sw=(TREE/'sw.js').read_text(encoding='utf8').replace('/* v101.103 */','/* v101.105 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-103';",f"const CACHE_NAME = '{CACHE}';",1);(TREE/'sw.js').write_text(sw,encoding='utf8')
    readme=f'''# Les 24 Heures de la Passion — v101.105\n\nStage: `{STAGE}`\n\nThis successor restores the native v101.101 24H visual paragraph rhythm while retaining v101.103 semantic quotation/speaker intelligence. It adds a narrowly scoped presentation-only cross-record join capability for visible opening-guillemet edges; canonical text, raw `SPEECH_DATA`, IDs/order and RA19B flow authority are unchanged.\n\nRelease ceiling before physical-device/live/offline validation: `LIMITED_PASS_STATIC`.\n\nFinal reopened-ZIP audits and the final decision lock are external post-package evidence and are intentionally not embedded here.\n'''
    (TREE/'README.md').write_text(readme,encoding='utf8')
    qa=(TREE/'REAL_DEVICE_QA_CHECKLIST.md').read_text(encoding='utf8') if (TREE/'REAL_DEVICE_QA_CHECKLIST.md').exists() else '# Real-device QA\n'
    qa=re.sub(r'v101\.103',VERSION,qa)
    qa += '''\n## v101.105 mandatory presentation fixtures\n- iPad/iPhone H20.P016: direct Jesus words inline with native paragraph rhythm; redundant outer guillemets invisible.\n- iPad/iPhone IMG_4532 class: `je me disais : « Mon Jésus...` stays one visual paragraph; no orphan opening guillemet.\n- Verify all visible quotation openings never strand `«` from the first lexical word.\n- Samsung: whole-paragraph target matches the same visible joined paragraph as the reader.\n'''
    (TREE/'REAL_DEVICE_QA_CHECKLIST.md').write_text(qa,encoding='utf8')
    # Results template remains NOT_TESTED, update version.
    rp=TREE/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'
    if rp.exists():
        rr=list(csv.DictReader(rp.open(encoding='utf-8-sig')))
        for r in rr:r['app_version']=VERSION;r['status']='NOT_TESTED';r['evidence']=''
        write_csv(rp,rr,fields=rr[0].keys() if rr else ['scenario','app_version','device','status','evidence','notes'])
    # Build provenance + lifecycle, no postpackage claims.
    (TREE/'metadata'/'build_provenance.json').write_text(json.dumps({'version':VERSION,'stage':STAGE,'baseline_zip':BASE.name,'baseline_sha256':BASE_SHA,'native_topology_witness':'v101.101 exact runtime','semantic_witness':'v101.103 exact projection/quotation roles','date':DATE,'scope_escalation':'user explicit do it after FAIL_SCOPE_ESCALATION_REQUIRED'},indent=2)+'\n')
    (TREE/'metadata'/'release_evidence_lifecycle.json').write_text(json.dumps({'model':'non_circular_external_final_audits','prepackage_reports_inside_zip':True,'final_reopen_reports_inside_zip':False,'final_decision_lock_inside_zip':False,'primary_reopen':'POST_PACKAGE_EXTERNAL','independent_reopen':'POST_PACKAGE_EXTERNAL'},indent=2)+'\n')
    # User evidence authority; only facts supplied/observed, no pass claims.
    (TREE/'metadata'/'user_feedback_authority.md').write_text('''# User feedback authority\n\nPhysical iPad screenshots supplied for v101.102 demonstrate orphan opening-guillemet defects, including Luisa's visible quotation in IMG_4532. On 23 August 2026 the user approved the final architecture: **native 24H paragraph presentation + LDC semantic quotation/speaker intelligence + shared renderer/Samsung topology**, and explicitly authorized the narrow renderer/topology scope escalation after the strict pre-edit hard stop.\n''',encoding='utf8')
    # New scripts.
    shutil.copy2(Path(__file__),TREE/'scripts'/'build_v101105_hybrid.py')
    shutil.copy2(ROOT/'L24H_v101105_NATIVE_24H_LDC_SEMANTIC_HYBRID_PRESENTATION_HARDGATED_EXECUTION_SCRIPT_2026-08-23.md',TREE/'scripts'/'EXECUTION_SPEC.md')
    return patched,Topo,join_rows

def build_manifests():
    # Package manifest = paths/sizes only, generated before hash manifest.
    paths=[]
    for p in sorted(x for x in TREE.rglob('*') if x.is_file() and x.relative_to(TREE).as_posix() not in {'metadata/package_manifest.json','metadata/hash_manifest.json'}):
        paths.append({'path':p.relative_to(TREE).as_posix(),'size':p.stat().st_size})
    pm={'version':VERSION,'generated_prepackage':True,'files':paths,'self_exclusion':['metadata/package_manifest.json','metadata/hash_manifest.json']}
    (TREE/'metadata'/'package_manifest.json').write_text(json.dumps(pm,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    # Hash manifest includes package manifest but excludes itself, explicitly non-circular.
    hashes=[]
    for p in sorted(x for x in TREE.rglob('*') if x.is_file() and x.relative_to(TREE).as_posix()!='metadata/hash_manifest.json'):
        hashes.append({'path':p.relative_to(TREE).as_posix(),'sha256':sha_file(p),'size':p.stat().st_size})
    hm={'version':VERSION,'algorithm':'SHA-256','generated_prepackage':True,'self_excluded':True,'entries':hashes}
    (TREE/'metadata'/'hash_manifest.json').write_text(json.dumps(hm,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    patched,Topo,join_rows=build_tree()
    print('TREE',TREE)
    print('projection local breaks',sum(len(v) for v in Topo['local_breaks'].values()),'cross',len(Topo['cross_record_breaks']),'joins',len(Topo['cross_record_joins']))
    # Manifests delayed until runtime reports have been written by harness. Caller completes freeze.
if __name__=='__main__': main()
