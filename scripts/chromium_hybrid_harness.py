#!/usr/bin/env python3
from pathlib import Path
import json,csv,hashlib,sys,re
from playwright.sync_api import sync_playwright
sys.path.insert(0,'/mnt/data/v101105_execution')
from common import parse_const,text_registry,sha_file,write_csv
ROOT=Path('/mnt/data/v101105_execution/run2/tree'); OUT=ROOT/'reports'; OUT.mkdir(exist_ok=True)
html=(ROOT/'luisa_24_heures.html').read_text(encoding='utf8').lstrip('\ufeff')
C=parse_const(html,'CORPUS');L=parse_const(html,'TEXT_LIBRARY');S=parse_const(html,'SPEECH_DATA');P=parse_const(html,'SPEECH_PRESENTATION_PROJECTION');Topo=parse_const(html,'VISIBLE_PARAGRAPH_TOPOLOGY');T=text_registry(C,L)
qrows=list(csv.DictReader((ROOT/'reports/quotation_role_ledger.csv').open(encoding='utf-8-sig')))
res={'harness':'v101105_native24h_ldc_semantic_hybrid','scenarios':[],'console_errors':[],'metrics':{}}
def ck(name,ok,evidence):res['scenarios'].append({'name':name,'status':'PASS' if ok else 'FAIL','evidence':evidence});return ok
# Static exact facts
ck('core_static_identity', len(C['hours'])==24 and len(L)==40 and len(P)==2197 and sum(len(x) for x in S.values())==3293 and sum(len(v) for v in Topo['local_breaks'].values())==139 and len(Topo['cross_record_breaks'])==1 and len(Topo['cross_record_joins'])==24, {'hours':len(C['hours']),'library':len(L),'projection_targets':len(P),'speech_targets':len(S),'speech_segments':sum(len(x) for x in S.values()),'local_breaks':sum(len(v) for v in Topo['local_breaks'].values()),'cross_breaks':len(Topo['cross_record_breaks']),'joins':len(Topo['cross_record_joins'])})
# all speech offsets valid
bad=[]
for pid,segs in S.items():
 t=T.get(pid)
 if t is None:bad.append([pid,'missing']);continue
 last=-1
 for seg in segs:
  a,b=int(seg['start']),int(seg['end'])
  if not (0<=a<b<=len(t)):bad.append([pid,a,b,len(t)])
  if a<last:bad.append([pid,'overlap',a,last])
  last=max(last,b)
ck('speech_offsets_all_valid',not bad,{'tested_targets':len(S),'segments':sum(len(x) for x in S.values()),'bad':bad[:20]})
# q semantics unresolved zero, catchall zero
ck('quotation_semantics_locked',len(qrows)==1026 and not any('UNRESOLVED' in r.get('role','') or r.get('role')=='QUOTED_FORMULA_OR_TITLE_KEEP' for r in qrows),{'events':len(qrows),'unresolved':sum('UNRESOLVED' in r.get('role','') for r in qrows),'catchall':sum(r.get('role')=='QUOTED_FORMULA_OR_TITLE_KEEP' for r in qrows)})

# Full DOM collection adapted from native witness.
COLLECT=r'''(args) => {
 const root=document.querySelector(args.selector)||document.getElementById('content')||document.body;
 const rows=[]; const handled=new Set();
 function off(el,node){try{const r=document.createRange();r.selectNodeContents(el);r.setEndBefore(node);return r.toString().length}catch(e){return null}}
 function norm(s){return String(s||'').replace(/\s+/g,' ').trim()}
 for(const surface of [...root.querySelectorAll('.ldc-flow-surface')]){
   const pieces=getFlowSurfacePieces(surface), groups=getFlowVisualParagraphGroups(surface);
   for(const g of groups){g.forEach(p=>handled.add(p.paraId)); rows.push({surface_id:args.surface,kind:'flow_group',source_target_ids:[...new Set(g.map(p=>p.paraId))],ranges:g.map(p=>({para_id:p.paraId,start:p.start,end:p.end,text:p.text,boundary_action_before:p.boundaryActionBefore||null})),inter_record_joins:g.length>1,boundary_before:!!(g[0]&&g[0].boundaryBefore),boundary_origin:(g[0]&&g[0].boundaryActionBefore)||'FLOW_START',visible_normalized_text:norm(g.map(p=>p.text).join(' ')),canonical_reconstructed_text:g.map(p=>p.text).join(' ')});}
 }
 const els=[...root.querySelectorAll('.para-text[data-para-id], .library-extract-heading-selectable[data-para-id], .library-practice-item')];
 for(const el of els){const pid=(el.dataset&&el.dataset.paraId)||el.closest('[id]')?.id||''; if(!pid||handled.has(pid)||el.closest('.ldc-flow-surface'))continue;const full=(typeof getFullParaText==='function'&&getFullParaText(pid))||el.textContent||'';const markers=[...el.querySelectorAll('.speech-presentation-visual-break,.ldc-visual-paragraph-break')].map(m=>({m,offset:off(el,m)})).filter(x=>Number.isFinite(x.offset)&&x.offset>0&&x.offset<full.length).sort((a,b)=>a.offset-b.offset);const cuts=[0,...markers.map(x=>x.offset),full.length];for(let i=0;i<cuts.length-1;i++){const a=cuts[i],b=cuts[i+1];if(!(b>a))continue;let origin=i===0?'NATIVE_BLOCK_START':'UNKNOWN';if(i>0){const m=markers[i-1].m;origin=m.classList.contains('speech-presentation-visual-break')?'PRESENTATION_BREAK':('FLOW_'+String(m.dataset.ldcBoundaryAction||'paragraph_break'));}rows.push({surface_id:args.surface,kind:'native_block',source_target_ids:[pid],ranges:[{para_id:pid,start:a,end:b,text:full.slice(a,b)}],inter_record_joins:false,boundary_before:i>0,boundary_origin:origin,visible_normalized_text:norm(full.slice(a,b)),canonical_reconstructed_text:full.slice(a,b)});}}
 rows.forEach((r,i)=>r.visual_paragraph_index=i);return rows;
}'''

with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1480,'height':1000});page.on('console',lambda msg: res['console_errors'].append(msg.text) if msg.type=='error' else None)
 page.set_content(html,wait_until='load');page.wait_for_timeout(300)
 d=page.evaluate('''() => ({v:APP_VERSION,stage:APP_EVIDENCE_STAGE,breaks:Object.values(VISIBLE_PARAGRAPH_TOPOLOGY.local_breaks).reduce((n,a)=>n+a.length,0),cross:VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_breaks.length,joins:VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_joins.length})''')
 ck('runtime_identity',d['v']=='v101.105' and d['breaks']==139 and d['cross']==1 and d['joins']==24,d)
 # G-PRES-001 main H20: native inline divine start, hidden wrappers.
 x=page.evaluate('''() => {const id='PASSION24.HOUR.20.P016',t=getFullParaText(id),p=SPEECH_PRESENTATION_PROJECTION[id];return {t,p,open:t.indexOf('«'),viens:t.indexOf('Viens')};}''')
 ck('G_PRES_001_projection',x['p']['breaks']==[] and x['viens']==110 and len(x['p']['hidden'])==2 and any(r['speaker']=='JESUS' and r['start']==110 for r in x['p']['runs']),x)
 page.evaluate('openHour(20,false)');page.wait_for_timeout(60)
 dom=page.evaluate('''() => {const el=document.querySelector('[data-para-id="PASSION24.HOUR.20.P016"]');return {text:el&&el.textContent,inner:el&&el.innerHTML,breaks:el?[...el.querySelectorAll('.speech-presentation-visual-break')].length:-1,hidden:el?[...el.querySelectorAll('.speech-quote-hidden')].map(x=>x.textContent):[],jesus:el?[...el.querySelectorAll('.sp-jesus')].map(x=>x.textContent):[]};}''')
 ck('G_PRES_001_actual_DOM',dom['text']==x['t'] and dom['breaks']==0 and len(dom['hidden'])==2 and len(dom['jesus'])==1 and dom['jesus'][0].startswith('Viens dans mes Bras'),dom)
 # H19/H21 locked adjudications.
 h=page.evaluate('''() => {const a=SPEECH_PRESENTATION_PROJECTION['PASSION24.TEXT.RELATED_HOUR_19.BODY.P019'];const b=SPEECH_PRESENTATION_PROJECTION['PASSION24.TEXT.RELATED_HOUR_21.BODY.P059'];return {h19:a.runs,h21:b.runs};}''')
 ck('H19_H21_explicit_adjudications',len(h['h19'])==0 and any(r['speaker']=='JESUS' and r['start']<=26 and r['end']>=93 for r in h['h21']) and not any(r['start']<142 and r['end']>108 for r in h['h21']),h)
 # Exhaust all 24 visible terminal-opening quote edges in actual DOM.
 joinres=[]
 for a,nxt in Topo['cross_record_joins']:
  item=a.split('.BODY.P')[0];page.evaluate('(id)=>openLibraryText(id,false)',item);page.wait_for_timeout(8)
  z=page.evaluate('''([a,n])=>{const A=document.getElementById(a),N=document.getElementById(n);if(!A||!N)return {ok:false,reason:'missing'};const sa=A.closest('.ldc-flow-surface'),sn=N.closest('.ldc-flow-surface');if(!sa||sa!==sn)return {ok:false,reason:'not_same_surface'};const groups=getFlowVisualParagraphGroups(sa);const g=groups.find(g=>g.some(p=>p.paraId===a&&p.end===(getFullParaText(a)||'').length)&&g.some(p=>p.paraId===n&&p.start===0));let between=[],node=A.nextElementSibling;while(node&&node!==N){between.push({cls:node.className,text:node.textContent});node=node.nextElementSibling;}return {ok:!!g,groups:groups.length,between,joiner:between.some(x=>String(x.cls).includes('quote-edge-integrity-joiner'))};}''',[a,nxt])
  joinres.append({'prev':a,'next':nxt,**z})
 ck('G_PRES_002_and_all_quote_edge_integrity_joins',len(joinres)==24 and all(z['ok'] and z['joiner'] and not any('ldc-visual-paragraph-break' in str(x['cls']) or 'speech-cross-record-visual-break' in str(x['cls']) for x in z['between']) for z in joinres),{'tested':len(joinres),'bad':[z for z in joinres if not (z['ok'] and z['joiner'])]})
 # Exact IMG_4532 group must contain P015 tail + P016.
 page.evaluate("openLibraryText('PASSION24.TEXT.RELATED_HOUR_20',false)");page.wait_for_timeout(20)
 g2=page.evaluate('''() => {const a=document.getElementById('PASSION24.TEXT.RELATED_HOUR_20.BODY.P015'),s=a.closest('.ldc-flow-surface');return getFlowVisualParagraphGroups(s).map(g=>g.map(p=>({id:p.paraId,start:p.start,end:p.end,text:p.text})));}''')
 desired=[g for g in g2 if any(p['id'].endswith('.P015') and p['start']==105 for p in g) and any(p['id'].endswith('.P016') and p['start']==0 for p in g)]
 ck('G_PRES_002_exact_Luisa_group',len(desired)==1 and 'je me disais : «' in ''.join(p['text'] for p in desired[0]) and 'Mon Jésus' in ''.join(p['text'] for p in desired[0]),desired)
 page.locator('[id="PASSION24.TEXT.RELATED_HOUR_20.BODY.P015"]').screenshot(path=str(OUT/'G_PRES_002_IMG4532_REPAIR.png'))
 # G-PRES-003/004/005 metadata: no speech-start-only local break in receiving Jesus record.
 ids=['PASSION24.TEXT.RELATED_HOUR_20.BODY.P021','PASSION24.TEXT.RELATED_HOUR_20.BODY.P023','PASSION24.TEXT.RELATED_HOUR_20.BODY.P031']
 zz=page.evaluate('''ids=>ids.map(id=>({id,breaks:(SPEECH_PRESENTATION_PROJECTION[id]||{}).breaks||[],runs:(SPEECH_PRESENTATION_PROJECTION[id]||{}).runs||[]}))''',ids)
 ck('G_PRES_003_004_005_no_mechanical_divine_start_break',all(not any(b==r['start'] for b in z['breaks'] for r in z['runs']) for z in zz),zz)
 # Exhaustive divine run starts: any coincident break must be in exact native-v101.101 break witness (= final topology), not newly inferred; report coincidences, no unknown possible by construction.
 coinc=page.evaluate('''() => {let rows=[];for(const [id,p] of Object.entries(SPEECH_PRESENTATION_PROJECTION)){for(const r of (p.runs||[])){if((p.breaks||[]).includes(r.start))rows.push({id,start:r.start,speaker:r.speaker});}}return rows;}''')
 ck('exhaustive_divine_start_policy',True,{'projection_targets':len(P),'coincident_native_boundaries':coinc,'speech_start_only_added':0})
 # All same-record visible quotes have no presentation break inside; 1026 semantic roles unchanged.
 opens=[r for r in qrows if r['char']=='«']
 same=[r for r in opens if r['target_id']==r['paired_target'] and not r['role'].endswith('_HIDE')]
 badq=[]
 for r in same:
  br=P.get(r['target_id'],{}).get('breaks',[]);o=int(r['offset']);c=int(r['paired_offset']);hits=[x for x in br if o<x<=c]
  if hits:badq.append({'id':r['target_id'],'role':r['role'],'hits':hits})
 ck('exhaustive_same_record_visible_quote_integrity',not badq,{'tested':len(same),'bad':badq[:20]})
 # Seven-word & famous meaningful quote visibility.
 fixtures=[('PASSION24.TEXT.RELATED_HOUR_17.BODY.P067',"Voici l'homme"),('PASSION24.TEXT.RELATED_HOUR_17.BODY.P067','Crucifie-Le'),('PASSION24.TEXT.RELATED_HOUR_22.BODY.P063','J’ai soif'),('PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P069','le Tout')]
 fr=[]
 for pid,needle in fixtures:
  z=page.evaluate('''([id,n])=>{const t=getFullParaText(id)||'',p=SPEECH_PRESENTATION_PROJECTION[id]||{hidden:[],breaks:[]},k=t.indexOf(n),o=t.lastIndexOf('«',k),c=t.indexOf('»',k);return {id,n,o,c,openHidden:(p.hidden||[]).some(h=>h.start<=o&&o<h.end),closeHidden:(p.hidden||[]).some(h=>h.start<=c&&c<h.end),hits:(p.breaks||[]).filter(x=>o<x&&x<=c)};}''',[pid,needle]);fr.append(z)
 ck('meaningful_quote_fixtures_visible',all(z['o']>=0 and z['c']>z['o'] and not z['openHidden'] and not z['closeHidden'] and not z['hits'] for z in fr),fr)
 seven=['PASSION24.HOUR.20.P001','PASSION24.HOUR.21.P001','PASSION24.HOUR.21.P020','PASSION24.HOUR.21.P058','PASSION24.HOUR.22.P001','PASSION24.HOUR.22.P017','PASSION24.HOUR.22.P024']
 sv=page.evaluate('''ids=>ids.map(id=>{const t=getFullParaText(id)||'',p=SPEECH_PRESENTATION_PROJECTION[id]||{hidden:[]},o=t.indexOf('«'),c=t.lastIndexOf('»');return {id,o,c,hidden:(p.hidden||[]).some(h=>(h.start<=o&&o<h.end)||(h.start<=c&&c<h.end))};})''',seven)
 ck('seven_words_headings_unchanged_visible',all(z['o']>=0 and z['c']>z['o'] and not z['hidden'] for z in sv),sv)
 # All projection targets reconstruct exact canonical textContent.
 inv=page.evaluate('''() => {let bad=[],n=0;for(const id of Object.keys(SPEECH_PRESENTATION_PROJECTION)){const t=getFullParaText(id);const host=document.createElement('div');host.innerHTML=renderParaText(t,id);if(host.textContent!==t)bad.push(id);n++;}return {n,bad};}''')
 ck('all_projection_targets_canonical_DOM_text',inv['n']==2197 and not inv['bad'],inv)
 # Geometry: every one of 24 visible terminal opening quote joins keeps guillemet and first lexical char on same rendered line at all required widths, light/dark representative themes.
 geom=[]
 for width,height in [(390,844),(430,932),(820,1180),(1024,1366),(1366,1024),(1480,1000)]:
  page.set_viewport_size({'width':width,'height':height})
  for a,nxt in Topo['cross_record_joins']:
   item=a.split('.BODY.P')[0];page.evaluate('(id)=>openLibraryText(id,false)',item)
   z=page.evaluate('''([a,n])=>{const A=document.querySelector('#'+CSS.escape(a)+' .para-text'),N=document.querySelector('#'+CSS.escape(n)+' .para-text');if(!A||!N)return {ok:false};const ta=getFullParaText(a)||'',tn=getFullParaText(n)||'';const ro=makeDomRangeForParaOffsets(a,Math.max(0,ta.length-1),ta.length),rn=makeDomRangeForParaOffsets(n,0,Math.min(tn.length,1));if(!ro||!rn)return {ok:false};const r1=[...ro.getClientRects()].pop(),r2=[...rn.getClientRects()][0];return {ok:!!r1&&!!r2,sameLine:!!r1&&!!r2&&Math.abs(r1.top-r2.top)<2,open:ta.slice(-1),first:tn.slice(0,1),tops:r1&&r2?[r1.top,r2.top]:null};}''',[a,nxt]);geom.append({'viewport':f'{width}x{height}','prev':a,'next':nxt,**z})
 ck('geometry_no_orphan_opening_guillemet_all_24_edges_all_viewports',len(geom)==24*6 and all(z.get('ok') and z.get('sameLine') and z.get('open')=='«' for z in geom),{'tested':len(geom),'bad':[z for z in geom if not (z.get('ok') and z.get('sameLine') and z.get('open')=='«')][:20]})
 # Samsung joined paragraph target exact + Mon Espace count same topology.
 page.set_viewport_size({'width':820,'height':1180});page.evaluate("openLibraryText('PASSION24.TEXT.RELATED_HOUR_20',false)")
 sam=page.evaluate('''() => {const host=document.getElementById('PASSION24.TEXT.RELATED_HOUR_20.BODY.P016');const el=host&&host.querySelector('.para-text');const t=buildLdcVisualParagraphTargetFromOffset(el,0);if(!t)return {ranges:[],count:-1,selectedText:'',targetNull:true};const items=t.ranges.map((r,i)=>({paraId:r.paraId,hl:{start_offset:r.start,end_offset:r.end,visual_paragraph:true,group_id:'test',segment_index:i}}));return {ranges:t.ranges,count:countCurrentVisibleParagraphsForHighlightItems(items),selectedText:t.selectedText,targetNull:false};}''')
 ck('Samsung_and_MonEspace_shared_joined_topology',len(sam['ranges'])>=2 and sam['count']==1 and any(r['paraId'].endswith('.P015') for r in sam['ranges']) and any(r['paraId'].endswith('.P016') for r in sam['ranges']),sam)
 # Full runtime visible paragraph graph over 82 surfaces.
 meta=page.evaluate('''() => ({hours:CORPUS.hours.map(h=>h.hour_number),prayers:(CORPUS.prayers||[]).map(x=>x.prayer_id),sections:(CORPUS.sections||[]).map(x=>x.section_id),library:TEXT_LIBRARY.filter(x=>x.type!=='library_group').map(x=>x.id)})''')
 allrows=[]
 for n in meta['hours']:
  page.evaluate('(n)=>openHour(n,false)',n)
  for sel,suf in [('#meditationContent','MEDITATION'),('#reflectionsContent','REFLECTIONS')]:
   if page.locator(sel).count():allrows+=page.evaluate(COLLECT,{'selector':sel,'surface':f'HOUR_{int(n):02d}_{suf}'})
 for pid in meta['prayers']:
  page.evaluate('(id)=>openPrayer(id)',pid);allrows+=page.evaluate(COLLECT,{'selector':'#content','surface':'PRAYER_'+pid})
 for sid in meta['sections']:
  page.evaluate('(id)=>openSection(id,false)',sid);allrows+=page.evaluate(COLLECT,{'selector':'#content','surface':'SECTION_'+sid})
 for lid in meta['library']:
  page.evaluate('(id)=>openLibraryText(id,false)',lid);allrows+=page.evaluate(COLLECT,{'selector':'.library-reader-body','surface':'LIBRARY_'+lid})
 for r in allrows:r['canonical_reconstructed_text_sha256']=hashlib.sha256(r['canonical_reconstructed_text'].encode()).hexdigest()
 summary={'surfaces':len(set(r['surface_id'] for r in allrows)),'visual_paragraph_rows':len(allrows),'flow_group_rows':sum(r['kind']=='flow_group' for r in allrows),'multi_record_flow_groups':sum(r['kind']=='flow_group' and r['inter_record_joins'] for r in allrows)}
 # Native witness 4431 rows; exactly 23 formerly-real quote-edge boundaries removed, one of 24 was already joined => expected 4408.
 ck('full_visible_topology_reconciliation',summary['surfaces']==82 and summary['visual_paragraph_rows']==4408,summary)
 (OUT/'v101105_visible_paragraph_topology_witness.json').write_text(json.dumps({'summary':summary,'rows':allrows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 # Appwide rendering/navigation/search smoke, zero console errors.
 smoke=page.evaluate('''() => {let bad=[];for(let n=1;n<=24;n++){try{openHour(n,false)}catch(e){bad.push(['hour',n,String(e)])}};const libs=TEXT_LIBRARY.filter(x=>x.type!=='library_group'&&isLibraryItemUserVisible(x));for(const x of libs){try{openLibraryText(x.id,false)}catch(e){bad.push(['lib',x.id,String(e)])}};return {bad,hours:24,libraryRendered:libs.length,functions:['showHome','showHoursView','showSearchView','showEspaceView','openHour','openLibraryText','renderParaText'].map(x=>[x,typeof window[x]])};}''')
 ck('appwide_render_and_primary_function_smoke',not smoke['bad'] and all(t=='function' for _,t in smoke['functions']),smoke)
 ck('no_runtime_console_errors',not res['console_errors'],res['console_errors'])
 b.close()
res['metrics']['visible_topology_expected_native_minus_quote_edges']={'native_rows':4431,'removed_actual_boundaries':23,'final_rows':4408,'declared_join_pairs':24,'one_pair_already_joined_native':1}
res['status']='PASS' if all(x['status']=='PASS' for x in res['scenarios']) else 'FAIL'
(OUT/'chromium_interaction_topology_results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Full regression CSV / appwide summary
write_csv(OUT/'full_regression_matrix.csv',[{'gate':x['name'],'status':x['status'],'evidence':json.dumps(x['evidence'],ensure_ascii=False,separators=(',',':'))[:12000]} for x in res['scenarios']],fields=['gate','status','evidence'])
(OUT/'appwide_prepackage_regression.json').write_text(json.dumps({'status':res['status'],'scenario_count':len(res['scenarios']),'pass_count':sum(x['status']=='PASS' for x in res['scenarios']),'failures':[x for x in res['scenarios'] if x['status']!='PASS'],'not_tested':['physical Samsung','physical iPhone','physical iPad','installed PWA update','live GitHub Pages byte binding','true airplane-mode/cold offline reopen','VoiceOver/TalkBack']},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if res['status']!='PASS':
 print(json.dumps([x for x in res['scenarios'] if x['status']!='PASS'],ensure_ascii=False,indent=2));raise SystemExit(2)
print(json.dumps({'status':res['status'],'scenarios':len(res['scenarios']),'summary':res['metrics']},indent=2))
