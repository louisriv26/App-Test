#!/usr/bin/env python3
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path('/mnt/data/v101105_execution/run2/tree'); OUT=ROOT/'reports'; html=(ROOT/'luisa_24_heures.html').read_text(encoding='utf8').lstrip('\ufeff')
R={'harness':'v101105_phaseE_functional','scenarios':[],'console_errors':[]}
def ck(n,o,e):R['scenarios'].append({'name':n,'status':'PASS' if o else 'FAIL','evidence':e})
MOCK="""() => {const a=new Map(),b=new Map();const mk=m=>({setItem:(k,v)=>m.set(String(k),String(v)),getItem:k=>m.has(String(k))?m.get(String(k)):null,removeItem:k=>m.delete(String(k)),clear:()=>m.clear(),key:i=>Array.from(m.keys())[i]||null,get length(){return m.size}});Object.defineProperty(window,'localStorage',{value:mk(a),configurable:true});Object.defineProperty(window,'sessionStorage',{value:mk(b),configurable:true});}"""
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1480,'height':1000});p.on('console',lambda m:R['console_errors'].append(m.text) if m.type=='error' else None);p.evaluate(MOCK);p.set_content(html,wait_until='load');p.wait_for_timeout(150)
 # Exact corpus/data counts fresh runtime.
 counts=p.evaluate("""() => ({hours:CORPUS.hours.length,prayers:(CORPUS.prayers||[]).length,sections:(CORPUS.sections||[]).length,library:TEXT_LIBRARY.length,linked:Object.keys(HOUR_LINKED_TEXTS||{}).length,internal:Object.keys(INTERNAL_SUBHEADINGS||{}).length,speechTargets:Object.keys(SPEECH_DATA).length,speechSegments:Object.values(SPEECH_DATA).reduce((n,a)=>n+a.length,0)})""")
 ck('fresh_runtime_corpus_counts',counts=={'hours':24,'prayers':5,'sections':4,'library':40,'linked':24,'internal':30,'speechTargets':2197,'speechSegments':3293},counts)
 # Library mark add/remove actual functions.
 lm=p.evaluate("""() => {const id='PASSION24.TEXT.RELATED_HOUR_20';openLibraryText(id,false);openLibraryMarkerPicker(id,document.getElementById('libraryTitleMarkBtn'));applyLibraryMarkerColor('yellow');const added=getLibraryMark(id);const removed=removeLibraryMark(id,false);return {added,removed,remaining:getLibraryMark(id)};}""")
 ck('library_mark_add_remove',bool(lm['added']) and lm['added']['color']=='yellow' and lm['removed'] and lm['remaining'] is None,lm)
 # Search matrix, semantic results. Use actual DOM text, not internal index only.
 queries=[('accent_insensitive',"Jesus est couronne d'epines",'couronné'),('linked_ldc','peine, pardon','peine'),('quoted_phrase',"Voici l'homme",'Voici'),('internal_subheading','Jésus est couronné d’épines','couronné')]
 qres=[]
 for name,q,needle in queries:
  z=p.evaluate("""([q,n])=>{showSearchView(false);const el=document.getElementById('homeSearchInput');el.value=q;performSearch(q);const r=document.getElementById('homeSearchResults');return {text:(r&&r.textContent)||'',html:(r&&r.innerHTML)||'',count:r?r.querySelectorAll('button,a,.search-result-item,.search-result-card').length:0,needle:n};}""",[q,needle]);z['name']=name;z['ok']=needle.lower() in z['text'].lower();qres.append(z)
 ck('search_matrix',all(x['ok'] for x in qres),[{k:v for k,v in x.items() if k not in ('html','text')}|{'sample':x['text'][:240]} for x in qres])
 # Navigation exact Hour -> Espace -> Retour should restore same Hour and progress element exists.
 nav=p.evaluate("""() => {showHome(false);openHour(20,false);const before={view:state.view,hour:state.currentHour};showEspaceView();goBack();const prog=document.getElementById('progressWrap');return {before,after:{view:state.view,hour:state.currentHour},progressDisplay:prog&&getComputedStyle(prog).display};}""")
 ck('hour_espace_back_restore',nav['before']['hour']==20 and nav['after']['hour']==20 and nav['after']['view'] in ['reader','hour'] and nav['progressDisplay']!='none',nav)
 # Help/modal state preservation.
 helpz=p.evaluate("""() => {openHour(20,false);const before={view:state.view,hour:state.currentHour};showHelp();const open=document.getElementById('helpModal')?.classList.contains('open')||document.getElementById('helpSheet')?.classList.contains('open')||document.querySelector('.help-modal.open')!==null;closeHelpModal();return {before,after:{view:state.view,hour:state.currentHour},open};}""")
 ck('help_modal_preserves_reader_state',helpz['before']==helpz['after'],helpz)
 # Static accessibility core: required nav labels, dialogs, hidden quote nodes aria-hidden, focusable buttons.
 acc=p.evaluate("""() => ({missingNav:[...document.querySelectorAll('.bottom-nav button')].filter(x=>!x.getAttribute('aria-label')&&!x.textContent.trim()).length,dialogs:document.querySelectorAll('[role="dialog"]').length,hiddenQuoteRender:(()=>{const t=getFullParaText('PASSION24.HOUR.20.P016');const d=document.createElement('div');d.innerHTML=renderParaText(t,'PASSION24.HOUR.20.P016');return [...d.querySelectorAll('.speech-quote-hidden')].every(x=>x.getAttribute('aria-hidden')==='true')&&d.querySelectorAll('.speech-quote-hidden').length===2})()})""")
 ck('accessibility_static_core',acc['missingNav']==0 and acc['dialogs']>=1 and acc['hiddenQuoteRender'],acc)
 ck('phaseE_no_console_errors',not R['console_errors'],R['console_errors']);b.close()
R['status']='PASS' if all(x['status']=='PASS' for x in R['scenarios']) else 'FAIL';(OUT/'phaseE_functional_results.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'status':R['status'],'failures':[x['name'] for x in R['scenarios'] if x['status']!='PASS']},indent=2));raise SystemExit(0 if R['status']=='PASS' else 2)
