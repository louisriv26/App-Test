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
 results=[]
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,w,h,ua in profiles:
   ctx=await browser.new_context(viewport={'width':w,'height':h},user_agent=ua)
   page=await ctx.new_page(); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   await page.set_content(HTML,wait_until='domcontentloaded');await page.wait_for_timeout(60)
   # Independent approach: group all requested offsets by target, render each target once, then map text-node source ranges to style state.
   req={}
   for r in rows:
    for part,tkey,okey in [('opener','open_target','open_offset'),('first_lexical','first_lexical_target','first_lexical_offset'),('last_lexical','last_lexical_target','last_lexical_offset'),('closer','close_target','close_offset')]:
     req.setdefault(r[tkey],set()).add(int(r[okey]))
   packed={k:sorted(v) for k,v in req.items()}
   states=await page.evaluate('''requests=>{
     const out={}; const host=document.createElement('section'); host.id='independent-presentation-audit'; host.style.cssText='position:absolute;left:0;top:0;width:760px'; document.body.appendChild(host);
     const speakerOf=el=>{if(el.closest('.sp-jesus'))return 'JESUS';if(el.closest('.sp-mary'))return 'MARY';if(el.closest('.sp-father'))return 'FATHER';return 'OUTSIDE'};
     for(const [pid,offsets] of Object.entries(requests)){
       const source=getFullParaText(pid)||''; const d=document.createElement('div');d.dataset.pid=pid;d.innerHTML=renderParaText(source,pid);host.appendChild(d);
       const nodes=[];let base=0;const tw=document.createTreeWalker(d,NodeFilter.SHOW_TEXT);let n;
       while(n=tw.nextNode()){
         const el=n.parentElement,cs=getComputedStyle(el),end=base+n.nodeValue.length;
         nodes.push({start:base,end,node:n,el,speaker:speakerOf(el),hidden:!!el.closest('.speech-quote-hidden'),color:cs.color,fontStyle:cs.fontStyle,display:cs.display,visibility:cs.visibility}); base=end;
       }
       const by={};
       for(const off of offsets){const rec=nodes.find(x=>off>=x.start&&off<x.end);by[off]=rec?{char:source[off]||'',speaker:rec.speaker,hidden:rec.hidden,color:rec.color,fontStyle:rec.fontStyle,display:rec.display,visibility:rec.visibility}:{error:'OFFSET_UNMAPPED',char:source[off]||'',sourceLength:source.length,renderedLength:d.textContent.length};}
       out[pid]={sourceLength:source.length,renderedLength:d.textContent.length,textExact:d.textContent===source,offsets:by}; d.remove();
     }
     host.remove();return out;
   }''',packed)
   for r in rows:
    def st(tk,ok):return states[r[tk]]['offsets'][str(int(r[ok]))]
    parts={'opener':st('open_target','open_offset'),'first_lexical':st('first_lexical_target','first_lexical_offset'),'last_lexical':st('last_lexical_target','last_lexical_offset'),'closer':st('close_target','close_offset')}
    exact=all(states[t]['textExact'] for t in {r['open_target'],r['first_lexical_target'],r['last_lexical_target'],r['close_target']})
    exp=r['expected_class'];parent=r['presentation_parent'];ok=exact;why=[]
    if not exact: why.append('render_text_mismatch')
    if exp=='HIDDEN_OUTER_WRAPPER':
     if not parts['opener'].get('hidden'):ok=False;why.append('opener_not_hidden')
     if not parts['closer'].get('hidden'):ok=False;why.append('closer_not_hidden')
     for p in ('first_lexical','last_lexical'):
      if parts[p].get('speaker') not in ('JESUS','MARY','FATHER'):ok=False;why.append(p+'_not_divine')
    elif exp.startswith('MEANINGFUL_NESTED_QUOTE_INHERITS_'):
     for p in parts:
      if parts[p].get('hidden'):ok=False;why.append(p+'_hidden')
      if parts[p].get('speaker')!=parent:ok=False;why.append(p+'_speaker_'+str(parts[p].get('speaker'))+'_expected_'+parent)
    elif exp=='TOP_LEVEL_DIVINE_QUOTE_CONTENT_ONLY':
     if parts['opener'].get('hidden') or parts['closer'].get('hidden'):ok=False;why.append('top_level_delimiter_hidden')
     if parts['opener'].get('speaker')!='OUTSIDE' or parts['closer'].get('speaker')!='OUTSIDE':ok=False;why.append('top_level_delimiter_overcoloured')
    else:ok=False;why.append('unknown_expected_class')
    results.append({'profile':label,'span_id':r['span_id'],'quote_family':r['quote_family'],'expected_class':exp,'presentation_parent':parent,'cross_record':r['open_target']!=r['close_target'],'status':'PASS' if ok else 'FAIL','why':why,'parts':parts})
   if errors: results.append({'profile':label,'span_id':'__PAGE_ERRORS__','status':'FAIL','why':errors})
   await ctx.close()
  await browser.close()
 summary={'profiles':5,'spans':len(rows),'checks':len(rows)*5,'pass':sum(x['status']=='PASS' for x in results),'fail':sum(x['status']=='FAIL' for x in results),'cross_record_spans':sum(1 for r in rows if r['open_target']!=r['close_target'])}
 obj={'schema':'L24H_V101125_INDEPENDENT_PRESENTATION_MATRIX_V1','version':VERSION,'implementation':'independent grouped-target text-node range mapper using real renderParaText DOM/computed styles','summary':summary,'results':results}
 OUT.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary));raise SystemExit(2 if summary['fail'] else 0)
asyncio.run(main())
