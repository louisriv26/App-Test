#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');OUT=Path(sys.argv[2]);VER=sys.argv[3] if len(sys.argv)>3 else 'v101.124'
PAIRS=[('PASSION24.HOUR.03.P012','PASSION24.HOUR.03.P013',3),('PASSION24.HOUR.13.P011','PASSION24.HOUR.13.P013',13),('PASSION24.HOUR.15.P014','PASSION24.HOUR.15.P015',15),('PASSION24.HOUR.19.P183','PASSION24.HOUR.19.P184',19),('PASSION24.HOUR.19.P185','PASSION24.HOUR.19.P186',19)]
PROFILES=[('phone',390,844),('ipad_p',820,1180),('ipad_l',1180,820),('desktop',1200,900),('samsung',412,915)]
async def main():
 rows=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for pn,w,h in PROFILES:
   ctx=await b.new_context(viewport={'width':w,'height':h});page=await ctx.new_page();errs=[];page.on('pageerror',lambda e:errs.append(str(e)));await page.set_content(HTML,wait_until='domcontentloaded')
   for a,c,hour in PAIRS:
    await page.evaluate('(h)=>openHour(h,false)',hour);await page.wait_for_timeout(20)
    d=await page.evaluate('''([a,c])=>{const A=document.getElementById(a),C=document.getElementById(c);const s=A&&A.closest('.continuity-flow-surface');const t=s&&s.querySelector('.continuity-flow-text');const j=s&&s.querySelector('.continuity-flow-joiner');const AT=A&&A.querySelector('.para-text'),CT=C&&C.querySelector('.para-text');function edge(el,last){if(!el)return null;const tw=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);const ns=[];while(tw.nextNode())if(tw.currentNode.nodeValue.length)ns.push(tw.currentNode);if(!ns.length)return null;const n=last?ns[ns.length-1]:ns[0],r=document.createRange();if(last){r.setStart(n,Math.max(0,n.nodeValue.length-1));r.setEnd(n,n.nodeValue.length);}else{r.setStart(n,0);r.setEnd(n,Math.min(1,n.nodeValue.length));}const x=r.getBoundingClientRect();return {top:x.top,left:x.left,bottom:x.bottom,right:x.right,height:x.height};}const ar=edge(AT,true),cr=edge(CT,false);return {a:!!A,c:!!C,same:!!s&&s===C.closest('.continuity-flow-surface'),aInline:A?getComputedStyle(A).display:null,cInline:C?getComputedStyle(C).display:null,at:AT?getComputedStyle(AT).display:null,ct:CT?getComputedStyle(CT).display:null,join:j?.textContent,dataA:AT?.dataset.paraId,dataC:CT?.dataset.paraId,numbers:s?s.querySelectorAll('.para-num').length:null,dy:ar&&cr?cr.top-ar.top:null,edgeA:ar,edgeC:cr};}''',[a,c])
    checks=[('stable_ids',d['a'] and d['c']),('same_surface',d['same']),('inline_fragments',d['aInline']=='inline' and d['cInline']=='inline'),('inline_text',d['at']=='inline' and d['ct']=='inline'),('single_space_joiner',d['join']==' '),('data_ids',d['dataA']==a and d['dataC']==c),('single_reperes_number',d['numbers'] in (0,1)),('natural_flow',d['dy'] is not None and d['dy']<70)]
    for name,ok in checks:rows.append({'profile':pn,'pair':a+'→'+c,'check':name,'status':'PASS' if ok else 'FAIL','detail':d})
   rows.append({'profile':pn,'pair':'ALL','check':'page_errors','status':'PASS' if not errs else 'FAIL','detail':errs})
   await ctx.close()
  await b.close()
 out={'schema':'L24H_V101124_INDEPENDENT_CONTINUITY_PROBE_V1','version':VER,'summary':{'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)},'rows':rows};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out['summary']));raise SystemExit(0 if out['summary']['fail']==0 else 2)
asyncio.run(main())
