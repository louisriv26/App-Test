#!/usr/bin/env python3
from pathlib import Path
import json,csv,hashlib,re,zipfile,subprocess,sys
from playwright.sync_api import sync_playwright
sys.path.insert(0,'/mnt/data/v101105_execution')
from common import parse_const,sha_file,text_registry
TREE=Path('/mnt/data/v101105_execution/run2/tree'); BASEZIP=Path('/mnt/data/L24H_v101103_GITHUB_DEPLOY_DIVINE_QUOTE_PRESENTATION_REGRESSION_REPAIR_R1_LOCKED.zip'); BASEHTML=Path('/mnt/data/v101105_execution/baseline103_full/luisa_24_heures.html'); WIT=Path('/mnt/data/_v101101/luisa_24_heures.html')
html=(TREE/'luisa_24_heures.html').read_text(encoding='utf8').lstrip('\ufeff'); base=BASEHTML.read_text(encoding='utf8').lstrip('\ufeff'); wit=WIT.read_text(encoding='utf8').lstrip('\ufeff')
checks=[]
def ck(passn,name,ok,evidence):checks.append({'pass':passn,'name':name,'status':'PASS' if ok else 'FAIL','evidence':evidence})
# PASS 1 files/spec
ck(1,'baseline_exact_sha',sha_file(BASEZIP)=='d08fa70a4931f8c2e997bc8bae46a8292ed9b14725346727852361a84cfdb664',sha_file(BASEZIP))
ck(1,'root_runtime_parity',(TREE/'index.html').read_bytes()==(TREE/'luisa_24_heures.html').read_bytes(),{'index':sha_file(TREE/'index.html'),'app':sha_file(TREE/'luisa_24_heures.html')})
req=['reports/no_regression_fix_ledger.csv','reports/full_regression_matrix.csv','reports/v101101_native_visual_topology_witness.csv','reports/v101101_native_visual_topology_witness.json','reports/v101103_semantic_presentation_witness.json','reports/v101103_quote_role_witness.csv','reports/hybrid_boundary_decision_ledger.csv','reports/quote_edge_hybrid_reconciliation.csv','reports/presentation_projection_summary.json','reports/visible_paragraph_topology_report.md','reports/android_visible_paragraph_groups.csv','reports/chromium_interaction_topology_results.json','reports/appwide_prepackage_regression.json','reports/protected_data_diff_report.csv','reports/stale_reference_scan.txt','reports/root_deploy_consistency_report.md','reports/nested_zip_consistency_report.md','reports/report_claims_vs_evidence_audit.md']
missing=[x for x in req if not (TREE/x).exists()];ck(1,'required_prepackage_artifacts_present',not missing,missing)
prot=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT']; pd={n:parse_const(base,n)==parse_const(html,n) for n in prot};ck(1,'protected_declarations_exact_semantic_parity',all(pd.values()),pd)
P=parse_const(html,'SPEECH_PRESENTATION_PROJECTION');Topo=parse_const(html,'VISIBLE_PARAGRAPH_TOPOLOGY');B101=parse_const(wit,'SPEECH_END_VISUAL_BREAKS');X101=parse_const(wit,'SPEECH_CROSS_RECORD_VISUAL_BREAKS');S=parse_const(html,'SPEECH_DATA');C=parse_const(html,'CORPUS');L=parse_const(html,'TEXT_LIBRARY');T=text_registry(C,L)
# exact native break map equality, not count-only
finalBreakMap={k:v for k,v in Topo['local_breaks'].items() if v}; nativeBreakMap={k:v for k,v in B101.items() if v};ck(1,'final_local_break_map_equals_v101101_native_speech_end_map',finalBreakMap==nativeBreakMap,{'final_targets':len(finalBreakMap),'native_targets':len(nativeBreakMap),'final_count':sum(map(len,finalBreakMap.values())),'native_count':sum(map(len,nativeBreakMap.values()))})
ck(1,'final_cross_breaks_equal_v101101',Topo['cross_record_breaks']==X101,Topo['cross_record_breaks'])
ck(1,'quote_edge_join_population',len(Topo.get('cross_record_joins',[]))==24,Topo.get('cross_record_joins',[]))
# PASS 2 independently recompute runtime behavior
runtime={'console':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1480,'height':1000});p.on('console',lambda m:runtime['console'].append(m.text) if m.type=='error' else None);p.set_content(html,wait_until='load');p.wait_for_timeout(120)
 ident=p.evaluate("() => ({v:APP_VERSION,stage:APP_EVIDENCE_STAGE,joins:VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_joins.length})");ck(2,'runtime_identity',ident=={'v':'v101.105','stage':'NATIVE_24H_PARAGRAPH_LDC_SEMANTIC_HYBRID_PRESENTATION_R1','joins':24},ident)
 # H20 original native-inline Jesus presentation
 h20=p.evaluate("""() => {openHour(20,false);const id='PASSION24.HOUR.20.P016',el=document.querySelector('[data-para-id="'+id+'"]'),proj=SPEECH_PRESENTATION_PROJECTION[id],t=getFullParaText(id);return {breaks:proj.breaks,hidden:proj.hidden.length,jesus:[...el.querySelectorAll('.sp-jesus')].map(x=>x.textContent),domBreaks:el.querySelectorAll('.speech-presentation-visual-break').length,text:el.textContent,canonical:t};}""");ck(2,'G_PRES_001_native_inline_Jesus',h20['breaks']==[] and h20['hidden']==2 and h20['domBreaks']==0 and len(h20['jesus'])==1 and h20['text']==h20['canonical'],h20)
 # all 24 quote-edge joins actual grouping and geometry in three representative widths
 jr=[]
 for w,h in [(390,844),(820,1180),(1480,1000)]:
  p.set_viewport_size({'width':w,'height':h})
  for a,n in Topo['cross_record_joins']:
   item=a.split('.BODY.P')[0];p.evaluate('(x)=>openLibraryText(x,false)',item)
   z=p.evaluate("""([a,n])=>{const A=document.getElementById(a),N=document.getElementById(n);if(!A||!N)return {ok:false};const s=A.closest('.ldc-flow-surface');if(!s||N.closest('.ldc-flow-surface')!==s)return {ok:false};const g=getFlowVisualParagraphGroups(s).find(g=>g.some(x=>x.paraId===a)&&g.some(x=>x.paraId===n));const ta=getFullParaText(a)||'',tn=getFullParaText(n)||'';const ra=makeDomRangeForParaOffsets(a,ta.length-1,ta.length),rn=makeDomRangeForParaOffsets(n,0,Math.min(1,tn.length));const r1=ra&&[...ra.getClientRects()].pop(),r2=rn&&[...rn.getClientRects()][0];return {ok:!!g&&!!r1&&!!r2,same:!!r1&&!!r2&&Math.abs(r1.top-r2.top)<2,open:ta.slice(-1)};}""",[a,n]);jr.append({'w':w,'a':a,'n':n,**z})
 ck(2,'all_24_quote_edges_group_and_no_orphan_geometry',len(jr)==72 and all(x['ok'] and x['same'] and x['open']=='«' for x in jr),{'tested':len(jr),'bad':[x for x in jr if not (x['ok'] and x['same'] and x['open']=='«')][:10]})
 # IMG4532 exact joined group and Samsung target/count
 p.set_viewport_size({'width':820,'height':1180});p.evaluate("openLibraryText('PASSION24.TEXT.RELATED_HOUR_20',false)")
 g=p.evaluate("""() => {const A=document.getElementById('PASSION24.TEXT.RELATED_HOUR_20.BODY.P015'),s=A.closest('.ldc-flow-surface'),gs=getFlowVisualParagraphGroups(s),chosen=gs.find(g=>g.some(x=>x.paraId.endsWith('.P015')&&x.start===105)&&g.some(x=>x.paraId.endsWith('.P016')&&x.start===0));const h=document.getElementById('PASSION24.TEXT.RELATED_HOUR_20.BODY.P016'),el=h.querySelector('.para-text'),t=buildLdcVisualParagraphTargetFromOffset(el,0);const items=t.ranges.map(x=>({paraId:x.paraId,hl:{start_offset:x.start,end_offset:x.end,visual_paragraph:true,group_id:'i'}}));return {group:chosen&&chosen.map(x=>({id:x.paraId,start:x.start,end:x.end,text:x.text})),ranges:t.ranges,count:countCurrentVisibleParagraphsForHighlightItems(items)};}""");ck(2,'IMG4532_and_shared_Samsung_topology',bool(g['group']) and len(g['ranges'])>=2 and g['count']==1 and 'je me disais : «' in ''.join(x['text'] for x in g['group']) and 'Mon Jésus' in ''.join(x['text'] for x in g['group']),g)
 # all projection DOM canonical reconstruction and all speech offsets
 inv=p.evaluate("""() => {let bad=[];for(const id of Object.keys(SPEECH_PRESENTATION_PROJECTION)){const t=getFullParaText(id)||'',d=document.createElement('div');d.innerHTML=renderParaText(t,id);if(d.textContent!==t)bad.push(id)}return {n:Object.keys(SPEECH_PRESENTATION_PROJECTION).length,bad};}""");ck(2,'all_projection_DOM_reconstructs_canonical',inv['n']==2197 and not inv['bad'],inv)
 bad=[]
 for pid,segs in S.items():
  t=T.get(pid)
  if t is None:bad.append([pid,'missing']);continue
  last=-1
  for q in segs:
   a,e=int(q['start']),int(q['end'])
   if not 0<=a<e<=len(t) or a<last:bad.append([pid,a,e,len(t),last])
   last=max(last,e)
 ck(2,'speech_offsets_independent',not bad,{'targets':len(S),'segments':sum(len(x) for x in S.values()),'bad':bad[:10]})
 # H19/H21 lock
 hh=p.evaluate("""() => ({h19:SPEECH_PRESENTATION_PROJECTION['PASSION24.TEXT.RELATED_HOUR_19.BODY.P019'].runs,h21:SPEECH_PRESENTATION_PROJECTION['PASSION24.TEXT.RELATED_HOUR_21.BODY.P059'].runs})""");ck(2,'H19_H21_locked',len(hh['h19'])==0 and any(x['speaker']=='JESUS' and x['start']<=26 and x['end']>=93 for x in hh['h21']) and not any(x['start']<142 and x['end']>108 for x in hh['h21']),hh)
 ck(2,'runtime_no_console_errors',not runtime['console'],runtime['console']);b.close()
# PASS 3 report claims vs current evidence
mat=list(csv.DictReader(open(TREE/'reports/full_regression_matrix.csv',encoding='utf-8-sig')));fix=list(csv.DictReader(open(TREE/'reports/no_regression_fix_ledger.csv',encoding='utf-8-sig')));protRows=list(csv.DictReader(open(TREE/'reports/protected_data_diff_report.csv',encoding='utf-8-sig'))); appwide=json.load(open(TREE/'reports/appwide_prepackage_regression.json'))
ck(3,'full_regression_matrix_no_fail',bool(mat) and all(x['status']=='PASS' for x in mat),{'rows':len(mat),'failures':sum(x['status']!='PASS' for x in mat)})
ck(3,'fix_ledger_no_fail',len(fix)==4 and all(x['status']=='PASS' for x in fix),{'rows':len(fix),'failures':sum(x['status']!='PASS' for x in fix)})
ck(3,'protected_report_matches_recomputed',all(x['status']=='PASS' for x in protRows) and all(pd.values()),{'report_rows':len(protRows),'recomputed':pd})
ck(3,'appwide_summary_matches_matrix',appwide['scenario_count']==len(mat) and appwide['pass_count']==len(mat) and appwide['failure_count']==0,appwide)
# PASS 4 adversarial/staleness/semantics
qrows=list(csv.DictReader(open(TREE/'reports/quotation_role_ledger.csv',encoding='utf-8-sig'))); unresolved=[r for r in qrows if 'UNRESOLVED' in r.get('role','') or r.get('role')=='QUOTED_FORMULA_OR_TITLE_KEEP'];ck(4,'quote_ledger_no_unresolved_or_catchall',len(qrows)==1026 and not unresolved,{'events':len(qrows),'bad':unresolved[:5]})
# Every final projection break must be a native v101101 speech-end break exactly.
extra=[]
for pid,pj in P.items():
 for x in pj.get('breaks',[]):
  if x not in B101.get(pid,[]):extra.append([pid,x])
ck(4,'no_speech_start_only_or_other_extra_break',not extra,{'extra':extra[:10],'final_breaks':sum(len(x.get('breaks',[])) for x in P.values())})
# Production source must not contain v101.104 generic relocation policy string; historical scripts may.
prod=html+'\n'+(TREE/'sw.js').read_text(encoding='utf8')+'\n'+(TREE/'version.json').read_text(encoding='utf8')
ck(4,'no_v101104_generic_relocation_in_production','MOVE_VISUAL_BOUNDARY_BEFORE_OPENING_GUILLEMET' not in prod,[])
# Meaningful fixtures visible, outer H20 hidden semantics intact.
fixtures=[('PASSION24.TEXT.RELATED_HOUR_17.BODY.P067',"Voici l'homme"),('PASSION24.TEXT.RELATED_HOUR_17.BODY.P067','Crucifie-Le'),('PASSION24.TEXT.RELATED_HOUR_22.BODY.P063','J’ai soif'),('PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P069','le Tout')]; fb=[]
for pid,needle in fixtures:
 t=T[pid];k=t.find(needle);o=t.rfind('«',0,k+1);c=t.find('»',k); hid=P[pid].get('hidden',[]); fb.append({'pid':pid,'needle':needle,'visible':o>=0 and c>o and not any(h['start']<=o<h['end'] or h['start']<=c<h['end'] for h in hid)})
ck(4,'meaningful_fixture_quotes_remain_visible',all(x['visible'] for x in fb),fb)
# Embedded stale scan says zero active failures, and no final reopen PASS artifacts inside.
stale=(TREE/'reports/stale_reference_scan.txt').read_text(encoding='utf8'); future=[x for x in TREE.rglob('*') if x.is_file() and x.name in {'FINAL_REOPEN_AUDIT.md','INDEPENDENT_REOPEN_AUDIT.md','FINAL_DECISION_LOCK.json'}]
ck(4,'embedded_stale_scan_zero_active','active_stale_failures=0' in stale,stale.splitlines()[:8]);ck(4,'no_embedded_postpackage_final_evidence',not future,[str(x.relative_to(TREE)) for x in future])
# Write audit only if all four passes are clean.
status='PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL'
lines=['# Independent four-pass prepackage audit — v101.105','',f'Overall status: **{status}**','', 'This auditor is separately implemented from the build script and recomputes critical runtime and package-tree facts directly.','']
for n in range(1,5):
 lines += [f'## Pass {n}', '']
 for x in checks:
  if x['pass']==n:lines.append(f"- **{x['status']}** — `{x['name']}` — `{json.dumps(x['evidence'],ensure_ascii=False,separators=(',',':'))[:1800]}`")
 lines.append('')
lines += ['## Not tested externally','', '- physical Samsung', '- physical iPhone', '- physical iPad', '- installed-PWA update', '- live GitHub Pages exact-byte binding', '- true airplane-mode/cold offline reopen', '- VoiceOver/TalkBack','']
(TREE/'audit/independent_four_pass_audit.md').write_text('\n'.join(lines),encoding='utf8')
(TREE/'audit/independent_four_pass_audit.json').write_text(json.dumps({'status':status,'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':status,'checks':len(checks),'failures':[x['name'] for x in checks if x['status']!='PASS']},indent=2));raise SystemExit(0 if status=='PASS' else 2)
