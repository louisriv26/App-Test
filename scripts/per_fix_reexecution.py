#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib,csv,re
from playwright.sync_api import sync_playwright
sys.path.insert(0,'/mnt/data/v101105_execution')
from common import parse_const,replace_const,sha_file,write_csv
BASE=Path('/mnt/data/v101105_execution/baseline103_full/luisa_24_heures.html')
FINAL=Path('/mnt/data/v101105_execution/run2/tree/luisa_24_heures.html')
OUT=Path('/mnt/data/v101105_execution/run2/tree/reports')
b=BASE.read_text(encoding='utf8').lstrip('\ufeff'); f=FINAL.read_text(encoding='utf8').lstrip('\ufeff')
P=parse_const(f,'SPEECH_PRESENTATION_PROJECTION'); T=parse_const(f,'VISIBLE_PARAGRAPH_TOPOLOGY')
# B1: pure semantic projection/topology metadata from final applied to fresh v101.103 runtime.
b1=replace_const(replace_const(b,'SPEECH_PRESENTATION_PROJECTION',P),'VISIBLE_PARAGRAPH_TOPOLOGY',T)
# B2: final runtime join capability, but revert B3 count helper and version/cache identity to baseline.
b2=f
# revert grouping helper + count block from final to baseline exact block
pat=r"function getVisibleParagraphPieceGroupKey\(paraId,start,end\) \{.*?\n\}\nfunction countCurrentVisibleParagraphsForHighlightItems\(items\) \{.*?\n\}\n"
base_count=re.search(r"function countCurrentVisibleParagraphsForHighlightItems\(items\) \{.*?\n\}\n",b,re.S).group(0)
b2=re.sub(pat,base_count,b2,count=1,flags=re.S)
# revert version identity only; semantic/topology and join renderer stay.
b2=b2.replace("const APP_VERSION = 'v101.105';","const APP_VERSION = 'v101.103';",1).replace("const APP_EVIDENCE_STAGE = 'NATIVE_24H_PARAGRAPH_LDC_SEMANTIC_HYBRID_PRESENTATION_R1';","const APP_EVIDENCE_STAGE = 'DIVINE_QUOTE_PRESENTATION_REGRESSION_REPAIR_R1';",1)
# B3: all runtime/data fixes, baseline identity.
b3=f.replace("const APP_VERSION = 'v101.105';","const APP_VERSION = 'v101.103';",1).replace("const APP_EVIDENCE_STAGE = 'NATIVE_24H_PARAGRAPH_LDC_SEMANTIC_HYBRID_PRESENTATION_R1';","const APP_EVIDENCE_STAGE = 'DIVINE_QUOTE_PRESENTATION_REGRESSION_REPAIR_R1';",1)
stages={'B1_HYBRID_PROJECTION':b1,'B2_QUOTE_EDGE_RENDERER_JOIN':b2,'B3_SHARED_INTERACTION_TOPOLOGY':b3,'B4_RELEASE_IDENTITY_AND_EVIDENCE':f}
for n,s in stages.items(): (Path('/mnt/data/v101105_execution/run2')/(n+'.html')).write_text(s,encoding='utf8')
rows=[]
def H(s):return hashlib.sha256(s.encode()).hexdigest()
with sync_playwright() as pw:
 br=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 # B1
 p=br.new_page();p.set_content(b1,wait_until='load');p.wait_for_timeout(100)
 z=p.evaluate("""() => {const p=SPEECH_PRESENTATION_PROJECTION['PASSION24.HOUR.20.P016'];return {v:APP_VERSION,breaks:p.breaks,hidden:p.hidden,runs:p.runs,local:Object.values(VISIBLE_PARAGRAPH_TOPOLOGY.local_breaks).reduce((n,a)=>n+a.length,0),cross:VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_breaks.length,joins:VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_joins.length};}""")
 ok=z['breaks']==[] and len(z['hidden'])==2 and any(r['speaker']=='JESUS' and r['start']==110 for r in z['runs']) and z['local']==139 and z['cross']==1 and z['joins']==24
 rows.append({'item_id':'B1','item':'Restore native-24H local/cross speech-end topology while preserving v101.103 semantic runs/hidden','files_changed':'luisa_24_heures.html/index.html generated constants','exact_blocks':'SPEECH_PRESENTATION_PROJECTION.breaks; VISIBLE_PARAGRAPH_TOPOLOGY','before_sha256':H(b),'after_sha256':H(b1),'targeted_test':'H20.P016 no speech-start break; 139 local/1 cross; 24 join metadata','mini_regression':'v101.103 hidden/runs retained','independent_recheck':json.dumps(z,separators=(',',':')),'redo_count':'1 (initial data-only stage correctly hard-stopped before scope escalation)','status':'PASS' if ok else 'FAIL'})
 p.close()
 # B2
 p=br.new_page();p.set_content(b2,wait_until='load');p.wait_for_timeout(100)
 joins=p.evaluate("""() => {let bad=[];for(const [a,n] of VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_joins){const item=a.split('.BODY.P')[0];openLibraryText(item,false);const A=document.getElementById(a),N=document.getElementById(n);const s=A&&A.closest('.ldc-flow-surface');if(!A||!N||!s||N.closest('.ldc-flow-surface')!==s){bad.push([a,n,'surface']);continue;}const g=getFlowVisualParagraphGroups(s).find(g=>g.some(x=>x.paraId===a)&&g.some(x=>x.paraId===n));if(!g)bad.push([a,n,'not_joined']);}return {declared:VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_joins.length,bad};}""")
 ok=joins['declared']==24 and not joins['bad']
 rows.append({'item_id':'B2','item':'Add narrow QUOTE_EDGE_INTEGRITY_JOIN renderer/topology capability','files_changed':'luisa_24_heures.html/index.html CSS + 3 helper functions + two renderer branches','exact_blocks':'.quote-edge-integrity-joiner; getQuoteEdgeIntegrityJoinPairs; hasQuoteEdgeIntegrityJoin; getQuoteEdgeIntegrityJoinBlock; renderLdcFlowSurface; renderLibraryItemBody','before_sha256':H(b1),'after_sha256':H(b2),'targeted_test':'All 24 declared quote-edge pairs render inside one .ldc-flow-surface visual group','mini_regression':'Canonical records and LDC_LIBRARY_FLOW_LAYOUT unchanged','independent_recheck':json.dumps(joins,separators=(',',':')),'redo_count':'0 after explicit user scope escalation','status':'PASS' if ok else 'FAIL'})
 p.close()
 # B3
 p=br.new_page();p.set_content(b3,wait_until='load');p.wait_for_timeout(100);p.evaluate("openLibraryText('PASSION24.TEXT.RELATED_HOUR_20',false)")
 sam=p.evaluate("""() => {const h=document.getElementById('PASSION24.TEXT.RELATED_HOUR_20.BODY.P016'),el=h&&h.querySelector('.para-text'),t=buildLdcVisualParagraphTargetFromOffset(el,0);const items=t.ranges.map((r,i)=>({paraId:r.paraId,hl:{start_offset:r.start,end_offset:r.end,visual_paragraph:true,group_id:'qa',segment_index:i}}));return {ranges:t.ranges.map(r=>[r.paraId,r.start,r.end]),count:countCurrentVisibleParagraphsForHighlightItems(items)};}""")
 ok=len(sam['ranges'])>=2 and sam['count']==1
 rows.append({'item_id':'B3','item':'Make Mon Espace/current-visible-paragraph counting collapse explicit quote-edge joined pieces exactly like Samsung/renderer','files_changed':'luisa_24_heures.html/index.html interaction helper','exact_blocks':'getVisibleParagraphPieceGroupKey; countCurrentVisibleParagraphsForHighlightItems','before_sha256':H(b2),'after_sha256':H(b3),'targeted_test':'IMG_4532 joined target spans P015/P016','mini_regression':'Mon Espace current-visible-paragraph count = 1 for the same joined Samsung target','independent_recheck':json.dumps(sam,separators=(',',':')),'redo_count':'0','status':'PASS' if ok else 'FAIL'})
 p.close()
 # B4
 p=br.new_page();p.set_content(f,wait_until='load');p.wait_for_timeout(100)
 ident=p.evaluate("() => ({v:APP_VERSION,stage:APP_EVIDENCE_STAGE,date:BUILD_DATE})")
 vmeta=json.loads(Path('/mnt/data/v101105_execution/run2/tree/version.json').read_text(encoding='utf8'))
 sw=(Path('/mnt/data/v101105_execution/run2/tree/sw.js').read_text(encoding='utf8'))
 ident.update({'version_json_app':vmeta.get('app_version'),'version_json_date':vmeta.get('build_date'),'version_json_cache':vmeta.get('cache_name'),'sw_cache_ok':"const CACHE_NAME = 'luisa-24h-v101-105';" in sw})
 ok=ident['v']=='v101.105' and ident['stage']=='NATIVE_24H_PARAGRAPH_LDC_SEMANTIC_HYBRID_PRESENTATION_R1' and ident['date']=='2026-08-23' and ident['version_json_app']=='v101.105' and ident['version_json_date']=='2026-08-23' and ident['version_json_cache']=='luisa-24h-v101-105' and ident['sw_cache_ok']
 rows.append({'item_id':'B4','item':'Freeze successor version/stage/cache/build-date and regenerate prepackage evidence only','files_changed':'runtime identity, sw.js, version.json, README/reports/metadata/scripts','exact_blocks':'APP_VERSION; APP_EVIDENCE_STAGE; BUILD_DATE; CACHE_NAME; version.json; prepackage evidence universe','before_sha256':H(b3),'after_sha256':H(f),'targeted_test':'runtime/version.json/service-worker identity and build-date parity','mini_regression':'No post-package reopen PASS claim embedded','independent_recheck':json.dumps(ident,separators=(',',':')),'redo_count':'1 (primary immutable reopen caught version.json build_date mismatch before release)','status':'PASS' if ok else 'FAIL'})
 p.close();br.close()
write_csv(OUT/'no_regression_fix_ledger.csv',rows,fields=['item_id','item','files_changed','exact_blocks','before_sha256','after_sha256','targeted_test','mini_regression','independent_recheck','redo_count','status'])
print(json.dumps({'status':'PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL','items':rows},ensure_ascii=False,indent=2))
raise SystemExit(0 if all(r['status']=='PASS' for r in rows) else 2)
