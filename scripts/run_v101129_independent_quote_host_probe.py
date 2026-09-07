#!/usr/bin/env python3
from pathlib import Path
import json, sys, asyncio
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]); OUT=Path(sys.argv[2]); OUT.parent.mkdir(parents=True,exist_ok=True)
html=HTML.read_text(encoding='utf-8'); dec=json.JSONDecoder()
def ex(name):
    marker=f'const {name} = '; i=html.index(marker)+len(marker); return dec.raw_decode(html[i:])[0]
def add(rows,case,ok,detail=None): rows.append({'case':case,'status':'PASS' if ok else 'FAIL','detail':detail})
SPP=ex('SPEECH_PRESENTATION_PROJECTION'); VPT=ex('VISIBLE_PARAGRAPH_TOPOLOGY'); SE=ex('SPEECH_END_VISUAL_BREAKS')
expected={
 'PASSION24.HOUR.08.P009': {'proj':[93,210],'top':[93,210],'forbidden_se':[42,140,93,210]},
 'PASSION24.HOUR.08.P010': {'proj':[],'top':[],'forbidden_se':[49]},
 'PASSION24.HOUR.08.P015': {'proj':[145],'top':[145],'forbidden_se':[50,145]},
 'PASSION24.HOUR.21.P020': {'proj':[],'top':[],'forbidden_se':[69]},
 'PASSION24.HOUR.21.P025': {'proj':[],'top':[],'forbidden_se':[118]},
 'PASSION24.TEXT.RELATED_HOUR_06.BODY.P043': {'proj':[],'top':[],'forbidden_se':[49]},
 'PASSION24.TEXT.RELATED_HOUR_06.BODY.P058': {'proj':[],'top':[],'forbidden_se':[49]},
}
valid={'PASSION24.HOUR.08.P007':[111],'PASSION24.HOUR.08.P008':[42],'PASSION24.HOUR.08.P014':[34]}
rows=[]
add(rows,'release_identity',"const APP_VERSION = 'v101.129';" in html and "const APP_EVIDENCE_STAGE = 'INTRA_RECORD_QUOTE_HOST_SENTENCE_CONTINUITY_R1';" in html)
for pid,e in expected.items():
    p=SPP.get(pid,{}); top=VPT.get('local_breaks',{}).get(pid,[])
    add(rows,pid+'_projection_exact',p.get('breaks',[])==e['proj'],{'actual':p.get('breaks',[]),'expected':e['proj']})
    add(rows,pid+'_topology_exact',top==e['top'],{'actual':top,'expected':e['top']})
    add(rows,pid+'_speech_end_forbidden_offsets_absent',all(x not in SE.get(pid,[]) for x in e['forbidden_se']),{'actual':SE.get(pid,[]),'forbidden':e['forbidden_se']})
    runs=p.get('runs',[])
    add(rows,pid+'_speaker_runs_finite',all(isinstance(r.get('start'),int) and isinstance(r.get('end'),int) and r['start']<r['end'] for r in runs),runs)
for pid,br in valid.items():
    add(rows,pid+'_valid_projection_retained',SPP.get(pid,{}).get('breaks',[])==br,SPP.get(pid,{}).get('breaks',[]))
    add(rows,pid+'_valid_topology_retained',VPT.get('local_breaks',{}).get(pid,[])==br,VPT.get('local_breaks',{}).get(pid,[]))

GEOM_JS=r'''({pid,br})=>{
 const t=getFullParaText(pid),x=document.createElement('div');
 x.style.cssText='position:absolute;left:0;top:3000px;width:2200px;font:20px Georgia,serif;line-height:1.55';
 x.innerHTML=renderParaText(t,pid);document.body.appendChild(x);
 function rect(off){let w=document.createTreeWalker(x,NodeFilter.SHOW_TEXT),n,pos=0;while(n=w.nextNode()){let L=n.nodeValue.length;if(off>=pos&&off<pos+L){let r=document.createRange();r.setStart(n,off-pos);r.setEnd(n,Math.min(off-pos+1,L));let q=r.getBoundingClientRect();return{x:q.x,y:q.y,h:q.height,ch:n.nodeValue[off-pos]}}pos+=L}return null}
 let a=br-1;while(a>=0&&/\s/.test(t[a]))a--;let b=br;while(b<t.length&&/\s/.test(t[b]))b++;
 let A=rect(a),B=rect(b),ret={a:a,b:b,A:A,B:B,dy:(A&&B)?B.y-A.y:null};x.remove();return ret;
}'''
async def browser_checks():
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  page=await b.new_page(viewport={'width':2400,'height':1200}); errs=[]; page.on('pageerror',lambda e:errs.append(str(e)))
  await page.set_content(html,wait_until='domcontentloaded'); await page.wait_for_timeout(100)
  for pid in expected:
   d=await page.evaluate("""pid=>{const t=getFullParaText(pid),x=document.createElement('div');x.innerHTML=renderParaText(t,pid);document.body.appendChild(x);const same=x.textContent===t;x.remove();return{same:same,len:t.length}}""",pid)
   add(rows,pid+'_dom_text_conserved',bool(d['same']),d)
  for pid,bounds in {'PASSION24.HOUR.08.P009':[93,210],'PASSION24.HOUR.08.P015':[145]}.items():
   for br in bounds:
    geo=await page.evaluate(GEOM_JS,{'pid':pid,'br':br})
    add(rows,pid+f'_boundary_{br}_visible_separation',bool(geo['A'] and geo['B'] and geo['dy']>5),geo)
  for pid in valid:
   cnt=await page.evaluate("""pid=>{const x=document.createElement('div');x.innerHTML=renderParaText(getFullParaText(pid),pid);document.body.appendChild(x);const n=x.querySelectorAll('.speech-presentation-visual-break').length;x.remove();return n}""",pid)
   add(rows,pid+'_valid_dom_break_present',cnt==1,{'actual':cnt})
  add(rows,'browser_page_errors_zero',not errs,errs)
  await b.close()
asyncio.run(browser_checks())
obj={'schema':'L24H_V101129_INDEPENDENT_QUOTE_HOST_PROBE_V1','version':'v101.129','implementation':'Independent probe; reads candidate bytes only and does not read primary v101.129 matrix outputs or the mutation ledger.','summary':{'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)},'rows':rows}
OUT.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(obj['summary'],ensure_ascii=False))
if obj['summary']['fail']: raise SystemExit(2)
