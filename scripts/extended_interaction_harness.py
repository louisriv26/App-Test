#!/usr/bin/env python3
from pathlib import Path
import json, hashlib
from playwright.sync_api import sync_playwright
ROOT=Path('/mnt/data/v101105_execution/run2/tree')
OUT=ROOT/'reports'
html=(ROOT/'luisa_24_heures.html').read_text(encoding='utf8').lstrip('\ufeff')
res={'harness':'v101105_extended_interaction','scenarios':[],'console_errors':[],'not_tested':['physical Samsung','physical iPhone','physical iPad','installed PWA update','live GitHub Pages byte binding','true airplane-mode/cold offline reopen','VoiceOver/TalkBack']}
def ck(name,ok,evidence):
    res['scenarios'].append({'name':name,'status':'PASS' if ok else 'FAIL','evidence':evidence}); return ok
MOCK="""() => { const __m=new Map(); const mk=()=>({setItem:(k,v)=>__m.set(String(k),String(v)),getItem:k=>__m.has(String(k))?__m.get(String(k)):null,removeItem:k=>__m.delete(String(k)),clear:()=>__m.clear(),key:i=>Array.from(__m.keys())[i]||null,get length(){return __m.size},_dump:()=>Object.fromEntries(__m.entries()),_load:o=>{__m.clear();Object.entries(o||{}).forEach(([k,v])=>__m.set(String(k),String(v)))}}); Object.defineProperty(window,'localStorage',{value:mk(),configurable:true}); Object.defineProperty(window,'sessionStorage',{value:mk(),configurable:true}); }"""
def setup(page, preload=None):
    page.evaluate(MOCK)
    if preload: page.evaluate('(o)=>localStorage._load(o)',preload)
    page.set_content(html,wait_until='load'); page.wait_for_timeout(200)
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=b.new_page(viewport={'width':820,'height':1180}); page.on('console',lambda m: res['console_errors'].append(m.text) if m.type=='error' else None); setup(page)
    # Samsung/Android logical lifecycle on the exact IMG_4532 joined visual paragraph.
    page.evaluate("openLibraryText('PASSION24.TEXT.RELATED_HOUR_20',false)"); page.wait_for_timeout(30)
    target=page.evaluate("""() => {const h=document.getElementById('PASSION24.TEXT.RELATED_HOUR_20.BODY.P016');const el=h&&h.querySelector('.para-text');return buildLdcVisualParagraphTargetFromOffset(el,0)}""")
    ck('android_target_is_joined_visual_paragraph',bool(target) and len(target.get('ranges',[]))>=2 and any(r['paraId'].endswith('.P015') for r in target['ranges']) and any(r['paraId'].endswith('.P016') for r in target['ranges']),target)
    add=page.evaluate("""() => {const h=document.getElementById('PASSION24.TEXT.RELATED_HOUR_20.BODY.P016'),el=h&&h.querySelector('.para-text');const t=buildLdcVisualParagraphTargetFromOffset(el,0);state._pending=contextTargetToPending(t);applyHighlight('yellow');const rows=[];for(const [pid,hs] of Object.entries(state.textHighlights))for(const x of hs)if(x.group_id)rows.push({pid,id:x.id,g:x.group_id,c:x.color,s:x.start_offset,e:x.end_offset,v:x.visual_paragraph});return {rows,count:countCurrentVisibleParagraphsForHighlightItems(rows.map(x=>({paraId:x.pid,hl:{start_offset:x.s,end_offset:x.e,visual_paragraph:true,group_id:x.g}}))),dump:localStorage._dump()};}""")
    ck('android_highlight_add_grouped_and_shared_topology',len(add['rows'])>=2 and len({x['g'] for x in add['rows']})==1 and add['count']==1 and all(x['v'] for x in add['rows']),{'rows':add['rows'],'count':add['count'],'storage_keys':list(add['dump'])})
    first=add['rows'][0]
    recol=page.evaluate("""([pid,id])=>{const aff=updateStoredHighlightColor(pid,id,'green');const rows=[];for(const [p,hs] of Object.entries(state.textHighlights))for(const x of hs)if(x.group_id)rows.push({p,id:x.id,g:x.group_id,c:x.color});return {affected:aff,rows};}""",[first['pid'],first['id']])
    ck('android_highlight_recolour_whole_group',len(recol['affected'])>=2 and recol['rows'] and all(x['c']=='green' for x in recol['rows']),recol)
    # Add again cleanly and capture persistence storage after durable change.
    page.evaluate("""() => {state.textHighlights={};saveState();const h=document.getElementById('PASSION24.TEXT.RELATED_HOUR_20.BODY.P016'),el=h&&h.querySelector('.para-text');state._pending=contextTargetToPending(buildLdcVisualParagraphTargetFromOffset(el,0));applyHighlight('blue');}""")
    persisted=page.evaluate('localStorage._dump()')
    p2=b.new_page(viewport={'width':820,'height':1180}); setup(p2,persisted); p2.evaluate("openLibraryText('PASSION24.TEXT.RELATED_HOUR_20',false)"); p2.wait_for_timeout(30)
    reload_data=p2.evaluate("""() => {const rows=[];for(const [p,hs] of Object.entries(state.textHighlights))for(const x of hs)rows.push({p,id:x.id,g:x.group_id||'',c:x.color,s:x.start_offset,e:x.end_offset,v:!!x.visual_paragraph});return {rows,count:countCurrentVisibleParagraphsForHighlightItems(rows.map(x=>({paraId:x.p,hl:{start_offset:x.s,end_offset:x.e,visual_paragraph:x.v,group_id:x.g}})))};}""")
    ck('android_highlight_reload_persistence',len(reload_data['rows'])>=2 and reload_data['count']==1 and all(x['c']=='blue' for x in reload_data['rows']),reload_data)
    if reload_data['rows']:
        rr=reload_data['rows'][0]
        dele=p2.evaluate("""([p,id])=>{const a=removeStoredHighlightById(p,id);return {affected:a,remaining:Object.values(state.textHighlights).reduce((n,x)=>n+x.length,0)}}""",[rr['p'],rr['id']])
        ck('android_highlight_delete_group',len(dele['affected'])>=2 and dele['remaining']==0,dele)
    else: ck('android_highlight_delete_group',False,reload_data)
    p2.close()
    # Apple/desktop exact-selection path across narration -> Jesus styling in H20.P016.
    page.evaluate('state.textHighlights={};saveState();openHour(20,false)'); page.wait_for_timeout(30)
    apple=page.evaluate("""() => {const id='PASSION24.HOUR.20.P016';const r=makeDomRangeForParaOffsets(id,95,130);const ws=window.getSelection();ws.removeAllRanges();ws.addRange(r);const ok=setPendingSelectionFromRange(r,null,false);const pending=state._pending?{...state._pending}:null;if(ok)applyHighlight('purple');const hs=state.textHighlights[id]||[];const el=document.querySelector('[data-para-id="'+id+'"]');return {ok,pending,hs:hs.map(x=>({s:x.start_offset,e:x.end_offset,c:x.color,t:x.selected_text_snapshot})),marks:el?[...el.querySelectorAll('mark.hl')].map(x=>x.textContent):[]};}""")
    ck('apple_exact_range_selection_add',apple['ok'] and apple['pending']['start']==95 and apple['pending']['end']==130 and len(apple['hs'])==1 and apple['hs'][0]['s']==95 and apple['hs'][0]['e']==130 and apple['hs'][0]['c']=='purple',apple)
    ah=apple['hs'][0] if apple['hs'] else None
    if ah:
        aid=page.evaluate("() => (state.textHighlights['PASSION24.HOUR.20.P016']||[])[0]?.id")
        ar=page.evaluate("""id=>{const a=updateStoredHighlightColor('PASSION24.HOUR.20.P016',id,'pink');rerenderPara('PASSION24.HOUR.20.P016');return {affected:a,color:state.textHighlights['PASSION24.HOUR.20.P016'][0].color,mark:[...document.querySelectorAll('[data-para-id="PASSION24.HOUR.20.P016"] mark.hl')].map(x=>x.textContent)};}""",aid)
        ck('apple_exact_range_recolour_rerender',ar['affected']==['PASSION24.HOUR.20.P016'] and ar['color']=='pink' and bool(ar['mark']),ar)
        ad=page.evaluate("""id=>{const a=removeStoredHighlightById('PASSION24.HOUR.20.P016',id);rerenderPara('PASSION24.HOUR.20.P016');return {affected:a,remaining:(state.textHighlights['PASSION24.HOUR.20.P016']||[]).length,marks:document.querySelectorAll('[data-para-id="PASSION24.HOUR.20.P016"] mark.hl').length};}""",aid)
        ck('apple_exact_range_delete',ad['remaining']==0 and ad['marks']==0,ad)
    # Theme/font/read/notes/search/nav/export core functional checks without claiming device/browser-specific physical behaviour.
    core=page.evaluate("""() => {const startTheme=state.themePreference;setThemePreference('dark');const dark=state.theme==='dark'||document.documentElement.classList.contains('dark');changeFontSize('large');const font=state.fontLevel;toggleRead(20);const read=state.readHours.has(20);return {startTheme,dark,font,read,version:APP_VERSION};}""")
    ck('theme_font_read_state_functions',core['dark'] and core['font']=='large' and core['read'],core)
    # Notes: use direct modal entry on a stable paragraph and save through actual function.
    note=page.evaluate("""() => {const id='PASSION24.HOUR.20.P016';openNoteModal(id);const ta=document.getElementById('noteTextarea');if(!ta)return {ok:false,reason:'no textarea'};ta.value='QA note v101.105';saveNoteFromModal();return {ok:true,notes:(state.notes[id]||[]).map(n=>n.text||n.body||n.note||''),count:(state.notes[id]||[]).length};}""")
    ck('note_add_functional',note.get('ok') and note.get('count',0)>=1,note)
    # Search function and navigation/back-stack stability.
    sr=page.evaluate("""() => {showSearchView(false);const q=document.getElementById('homeSearchInput');q.value='Jésus est couronné d’épines';performSearch(q.value);const n=document.querySelectorAll('.search-result-item, .search-result-card, [data-search-result]').length;showHome(false);openHour(20,false);showEspaceView();goBack();return {results:n,view:state.view,currentHour:state.currentHour,history:state.history.length};}""")
    ck('search_navigation_back_stack_smoke',sr['results']>=1 and sr['view'] in ['reader','hour'] and sr['currentHour']==20,sr)
    # Export payload generation must contain current schema/state without writing a file.
    ex=page.evaluate("""() => {const d=buildPersonalDataExport();return {type:typeof d,keys:d&&typeof d==='object'?Object.keys(d):[],version:d&&d.app_version,format:d&&d.format};}""")
    ck('personal_export_payload_generation',ex['type']=='object' and len(ex['keys'])>0,ex)
    ck('extended_no_console_errors',not res['console_errors'],res['console_errors'])
    b.close()
res['status']='PASS' if all(x['status']=='PASS' for x in res['scenarios']) else 'FAIL'
(OUT/'extended_interaction_results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':res['status'],'scenarios':len(res['scenarios']),'failures':[x['name'] for x in res['scenarios'] if x['status']!='PASS']},indent=2))
raise SystemExit(0 if res['status']=='PASS' else 2)
