import asyncio, json, sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); VERSION=sys.argv[2]; OUT=Path(sys.argv[3])
profiles=[
 ('phone',390,844,'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad',820,1180,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('samsung',412,915,'Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 Chrome/142.0 Mobile Safari/537.36 SamsungBrowser/28.0'),
 ('desktop',1200,900,'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/142.0 Safari/537.36')]
async def main():
 results=[]
 def add(profile,name,ok,detail=None):results.append({'profile':profile,'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,w,h,ua in profiles:
   ctx=await browser.new_context(viewport={'width':w,'height':h},user_agent=ua)
   page=await ctx.new_page();errors=[];consoles=[]
   await page.evaluate("""() => { const mem=new Map(); const ls={getItem:k=>mem.has(String(k))?mem.get(String(k)):null,setItem:(k,v)=>mem.set(String(k),String(v)),removeItem:k=>mem.delete(String(k)),clear:()=>mem.clear(),key:i=>Array.from(mem.keys())[i]||null,get length(){return mem.size}}; try{Object.defineProperty(window,'localStorage',{value:ls,configurable:true});}catch(e){} }""")
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('console',lambda m:consoles.append((m.type,m.text)) if m.type in ('error','warning') else None)
   await page.set_content(HTML,wait_until='domcontentloaded');await page.wait_for_timeout(100)
   init=await page.evaluate("() => ({ver:APP_VERSION,stage:APP_EVIDENCE_STAGE,view:state.view,content:document.getElementById('content').innerText.length,bodyWidth:document.body.scrollWidth,innerWidth:innerWidth})")
   add(label,'init_version',init['ver']==VERSION,init)
   add(label,'init_home_content',init['content']>200,init['content'])
   add(label,'no_horizontal_overflow',init['bodyWidth']<=init['innerWidth']+2,{'body':init['bodyWidth'],'inner':init['innerWidth']})
   val=await page.evaluate('''() => {const errors=[];let speechSegments=0,projectionRuns=0,hiddenRanges=0,displayTargets=0,topoTargets=0;function tt(id){try{return getFullParaText(id)||''}catch(e){return ''}}
   for(const [id,segs] of Object.entries(SPEECH_DATA||{})){const t=tt(id);if(!t)errors.push(['speech_missing',id]);let last=-1;for(const s of segs){speechSegments++;if(!(Number.isInteger(s.start)&&Number.isInteger(s.end)&&s.start>=0&&s.end>s.start&&s.end<=t.length))errors.push(['speech_range',id,s.start,s.end,t.length]);if(s.start<last)errors.push(['speech_overlap',id,s.start,last]);last=Math.max(last,s.end)}}
   for(const [id,rows] of Object.entries(SPEECH_PRESENTATION_ADJUDICATIONS||{})){const t=tt(id);if(!t)errors.push(['adj_missing',id]);for(const r of rows){if(!(r.start>=0&&r.end>r.start&&r.end<=t.length))errors.push(['adj_range',id,r.start,r.end,t.length])}}
   for(const [id,x] of Object.entries(SPEECH_PRESENTATION_PROJECTION||{})){const t=tt(id);if(!t)errors.push(['proj_missing',id]);for(const r of (x.runs||[])){projectionRuns++;if(!(r.start>=0&&r.end>r.start&&r.end<=t.length))errors.push(['proj_run',id,r.start,r.end,t.length])}for(const r of (x.hidden||[])){hiddenRanges++;if(!(r.start>=0&&r.end>r.start&&r.end<=t.length))errors.push(['proj_hidden',id,r.start,r.end,t.length])}for(const b of (x.breaks||[])){if(!(Number.isInteger(b)&&b>0&&b<t.length))errors.push(['proj_break',id,b,t.length])}}
   for(const [id,segs] of Object.entries(DISPLAY_SEGMENTS||{})){displayTargets++;const t=tt(id);if(!t)errors.push(['display_missing',id]);if(!Array.isArray(segs)||!segs.length){errors.push(['display_empty',id]);continue}let prev=0;for(let i=0;i<segs.length;i++){const s=segs[i];if(!(s.start===prev&&s.end>=s.start&&s.end<=t.length))errors.push(['display_range',id,i,s.start,s.end,prev,t.length]);prev=s.end}if(prev!==t.length)errors.push(['display_end',id,prev,t.length])}
   for(const [id,cuts] of Object.entries((VISIBLE_PARAGRAPH_TOPOLOGY||{}).local_breaks||{})){topoTargets++;const t=tt(id);if(!t)errors.push(['topo_missing',id]);for(const b of cuts){if(!(Number.isInteger(b)&&b>0&&b<t.length))errors.push(['topo_cut',id,b,t.length])}}
   for(const [id,rows] of Object.entries(SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS||{})){const t=tt(id);if(!t)errors.push(['supp_missing',id]);for(const r of rows){if(!(r.start>=0&&r.end>r.start&&r.end<=t.length))errors.push(['supp_range',id,r.start,r.end,t.length])}}
   return {errors,speechTargets:Object.keys(SPEECH_DATA).length,speechSegments,projectionTargets:Object.keys(SPEECH_PRESENTATION_PROJECTION).length,projectionRuns,hiddenRanges,displayTargets,topoTargets}}''')
   add(label,'runtime_target_map_integrity',not val['errors'],{k:v for k,v in val.items() if k!='errors'} if not val['errors'] else val)
   he=[]
   for n in range(1,25):
    r=await page.evaluate("n=>{try{openHour(n,false);const root=document.getElementById('content');const ids=[...root.querySelectorAll('[id]')].map(x=>x.id);return{ok:true,text:root.innerText.length,dups:ids.length-new Set(ids).size}}catch(e){return{ok:false,err:String(e)}}}",n)
    if not r.get('ok') or r.get('text',0)<1000 or r.get('dups',0):he.append([n,r])
   add(label,'render_all_24_hours',not he,he[:5])
   sr=await page.evaluate("() => {try{showSearchView(false);performSearch('âme');const r=document.getElementById('homeSearchResults');return{ok:true,count:r.querySelectorAll('.search-result-item').length}}catch(e){return{ok:false,err:String(e)}}}")
   add(label,'search_ame_results',sr.get('ok') and sr.get('count',0)>0,sr)
   es=await page.evaluate("() => {try{showEspaceView(false);return{ok:true,text:document.getElementById('content').innerText.length}}catch(e){return{ok:false,err:String(e)}}}")
   add(label,'mon_espace_renders',es.get('ok') and es.get('text',0)>100,es)
   tf=await page.evaluate("() => {try{setThemePreference('dark');changeFontSize(3);return{ok:true,dark:document.documentElement.getAttribute('data-theme')==='dark'||document.documentElement.classList.contains('dark'),font:state.fontSize}}catch(e){return{ok:false,err:String(e)}}}")
   add(label,'theme_font_controls',tf.get('ok') and tf.get('dark') and tf.get('font')==3,tf)
   fix=await page.evaluate('''() => {openHour(3,false);const h3=document.getElementById('content').innerText;openHour(22,false);const ids=['PASSION24.HOUR.22.P048','PASSION24.HOUR.22.P050','PASSION24.HOUR.22.P052','PASSION24.HOUR.22.P054','PASSION24.HOUR.22.P056','PASSION24.HOUR.22.P059','PASSION24.HOUR.22.P061','PASSION24.HOUR.22.P063','PASSION24.HOUR.22.P065'];const rows={};for(const id of ids){const el=document.getElementById(id);rows[id]={segs:el?[...el.querySelectorAll('.para-seg')].map(x=>x.innerText):[],cuts:getPresentationLocalBreaks(id)}}return{h3count:(h3.match(/Le monde des réprouvés est représenté par Judas/g)||[]).length,rows,p70:document.getElementById('PASSION24.HOUR.22.P070').innerText,p71:document.getElementById('PASSION24.HOUR.22.P071').innerText}}''')
   ok=fix['h3count']==1 and fix['p70'].rstrip().endswith('».') and fix['p71'].startswith('Jésus,')
   for x in fix['rows'].values():ok=ok and len(x['segs'])==2 and x['segs'][0].rstrip().endswith('».') and x['segs'][1].startswith('Jésus,') and len(x['cuts'])==1
   add(label,'v101112_user_fixes_preserved',ok,{'h3count':fix['h3count'],'h22rows':len(fix['rows'])})
   if label=='samsung':
    hr=await page.evaluate("""() => {try{document.documentElement.classList.add('android-scroll-fix');openHour(22,false);toggleAndroidHighlightMode(true);const block=document.getElementById('PASSION24.HOUR.22.P048');const surface=block.querySelector('.para-text')||block.querySelector('.para-seg');const ok=stage6hPrepareAndroidParagraphPending(surface);const p=state._pending?{start:state._pending.start,end:state._pending.end,whole:state._pending.whole_paragraph,android:state._pending.android_paragraph_mode}:null;return{ok,p,len:getFullParaText('PASSION24.HOUR.22.P048').length}}catch(e){return{ok:false,err:String(e)}}}""")
    add(label,'samsung_paragraph_pending',hr.get('ok') and hr.get('p',{}).get('start')==0 and hr.get('p',{}).get('end')==hr.get('len') and hr.get('p',{}).get('whole') and hr.get('p',{}).get('android'),hr)
   else:
    hi=await page.evaluate("""() => {try{openHour(3,false);const id='PASSION24.HOUR.03.P006',t=getFullParaText(id);state._pending={paraId:id,start:0,end:12,text:t.slice(0,12)};applyHighlight('yellow');const a=state.textHighlights[id]||[],h=a[a.length-1];return{ok:!!h,start:h&&h.start_offset,end:h&&h.end_offset,whole:h&&!!h.whole_paragraph,android:h&&!!h.android_paragraph_mode}}catch(e){return{ok:false,err:String(e)}}}""")
    add(label,'exact_text_highlight_model',hi.get('ok') and hi.get('start')==0 and hi.get('end')==12 and not hi.get('whole') and not hi.get('android'),hi)
   bad=await page.evaluate("() => {const a=[];for(const b of document.querySelectorAll('button:not([hidden])')){const c=getComputedStyle(b);if(c.display==='none'||c.visibility==='hidden')continue;const n=(b.getAttribute('aria-label')||b.innerText||b.textContent||'').trim();if(!n)a.push(b.id||b.className)}return a}")
   add(label,'visible_buttons_named',not bad,bad)
   add(label,'no_page_errors',not errors,errors)
   cerr=[x for x in consoles if x[0]=='error' and 'Content Security Policy' not in x[1]]
   add(label,'no_console_errors',not cerr,cerr[:10])
   await ctx.close()
  await browser.close()
 summary={'pass':sum(r['status']=='PASS' for r in results),'fail':sum(r['status']=='FAIL' for r in results),'total':len(results)}
 OUT.write_text(json.dumps({'schema':'L24H_BROAD_RUNTIME_MATRIX_V1','version':VERSION,'browser':'system Chromium via Playwright content injection','origin_limitation':'real URL/service-worker origin not claimed','summary':summary,'results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 if summary['fail']:raise SystemExit(2)
 print(json.dumps(summary))
asyncio.run(main())
