#!/usr/bin/env python3
import asyncio,csv,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); LEDGER=Path(sys.argv[2]); OUT=Path(sys.argv[3]); VERSION=sys.argv[4]
rows=list(csv.DictReader(LEDGER.open(encoding='utf-8-sig')))
profiles=[
 ('phone',390,844,'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad_portrait',820,1180,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad_landscape',1180,820,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('desktop',1200,900,'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/142.0 Safari/537.36'),
 ('samsung',412,915,'Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 Chrome/142.0 Mobile Safari/537.36 SamsungBrowser/28.0')]
async def main():
 out=[]
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,w,h,ua in profiles:
   ctx=await browser.new_context(viewport={'width':w,'height':h},user_agent=ua)
   page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   await page.set_content(HTML,wait_until='domcontentloaded');await page.wait_for_timeout(80)
   # Batch all target/offset probes. The helper uses the real renderParaText() and computed DOM classes/styles.
   probes=[]
   for r in rows:
    probes += [
      {'span_id':r['span_id'],'part':'opener','target':r['open_target'],'offset':int(r['open_offset']),'expected_class':r['expected_class'],'parent':r['presentation_parent']},
      {'span_id':r['span_id'],'part':'first_lexical','target':r['first_lexical_target'],'offset':int(r['first_lexical_offset']),'expected_class':r['expected_class'],'parent':r['presentation_parent']},
      {'span_id':r['span_id'],'part':'last_lexical','target':r['last_lexical_target'],'offset':int(r['last_lexical_offset']),'expected_class':r['expected_class'],'parent':r['presentation_parent']},
      {'span_id':r['span_id'],'part':'closer','target':r['close_target'],'offset':int(r['close_offset']),'expected_class':r['expected_class'],'parent':r['presentation_parent']},]
   res=await page.evaluate('''probes=>{
    const host=document.createElement('div');host.id='presentation-matrix-host';host.style.position='absolute';host.style.left='8px';host.style.top='8px';host.style.width='700px';document.body.appendChild(host);
    const cache=new Map();
    function build(pid){if(cache.has(pid))return cache.get(pid);const t=getFullParaText(pid)||'';const d=document.createElement('div');d.className='para-text presentation-probe';d.dataset.paraId=pid;d.innerHTML=renderParaText(t,pid);host.appendChild(d);cache.set(pid,{d,t});return {d,t};}
    function nodeAt(root,off){let pos=0;const tw=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while(n=tw.nextNode()){const len=n.nodeValue.length;if(off>=pos && off<pos+len)return {node:n,local:off-pos};pos+=len;}return null;}
    function inspect(p){const x=build(p.target);const hit=nodeAt(x.d,p.offset);if(!hit)return {error:'NO_TEXT_NODE',len:x.t.length,char:x.t[p.offset]||''};let el=hit.node.parentElement;const classes=[];let q=el;while(q&&q!==x.d.parentElement){if(q.classList)classes.push(...q.classList);q=q.parentElement;}const cs=getComputedStyle(el);let speaker='OUTSIDE';if(classes.includes('sp-jesus'))speaker='JESUS';else if(classes.includes('sp-mary'))speaker='MARY';else if(classes.includes('sp-father'))speaker='FATHER';const hidden=classes.includes('speech-quote-hidden');return {char:x.t[p.offset],speaker,hidden,classes:[...new Set(classes)],color:cs.color,fontStyle:cs.fontStyle,display:cs.display,visibility:cs.visibility};}
    return probes.map(p=>({...p,...inspect(p)}));
   }''',probes)
   byspan={}
   for x in res:byspan.setdefault(x['span_id'],{})[x['part']]=x
   for r in rows:
    parts=byspan[r['span_id']];expected=r['expected_class'];parent=r['presentation_parent'];ok=True;why=[]
    if expected=='HIDDEN_OUTER_WRAPPER':
      if not parts['opener'].get('hidden'):ok=False;why.append('opener_not_hidden')
      if not parts['closer'].get('hidden'):ok=False;why.append('closer_not_hidden')
      for p in ('first_lexical','last_lexical'):
       if parts[p].get('speaker') not in ('JESUS','MARY','FATHER'):ok=False;why.append(p+'_not_divine')
    elif expected.startswith('MEANINGFUL_NESTED_QUOTE_INHERITS_'):
      for p in ('opener','first_lexical','last_lexical','closer'):
       if parts[p].get('hidden'):ok=False;why.append(p+'_hidden')
       if parts[p].get('speaker')!=parent:ok=False;why.append(p+f'_speaker_{parts[p].get("speaker")}_expected_{parent}')
    elif expected=='TOP_LEVEL_DIVINE_QUOTE_CONTENT_ONLY':
      # Critical negative control: top-level/source wrapper delimiters remain OUTSIDE.
      # Cross-record wrappers may contain mixed narrator/divine lexical presentation, so do not
      # falsely require the first and last lexical characters of the whole wrapper to be divine.
      if parts['opener'].get('speaker')!='OUTSIDE' or parts['closer'].get('speaker')!='OUTSIDE':ok=False;why.append('top_level_delimiter_overcoloured')
    out.append({'profile':label,'span_id':r['span_id'],'quote_family':r['quote_family'],'expected_class':expected,'presentation_parent':parent,'status':'PASS' if ok else 'FAIL','why':why,'parts':parts})
   if errors: out.append({'profile':label,'span_id':'__PAGE_ERRORS__','status':'FAIL','why':errors})
   await ctx.close()
  await browser.close()
 summary={'profiles':len(profiles),'spans':len(rows),'checks':len(rows)*len(profiles),'pass':sum(x['status']=='PASS' for x in out),'fail':sum(x['status']=='FAIL' for x in out)}
 OUT.write_text(json.dumps({'schema':'L24H_V101119_EXHAUSTIVE_PRESENTATION_MATRIX_V1','version':VERSION,'browser':'system Chromium via Playwright / actual renderParaText DOM','summary':summary,'results':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary))
 if summary['fail']:raise SystemExit(2)
asyncio.run(main())
