#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2])
APPROVED=[
 ['PASSION24.HOUR.03.P012','PASSION24.HOUR.03.P013'],
 ['PASSION24.HOUR.13.P011','PASSION24.HOUR.13.P013'],
 ['PASSION24.HOUR.15.P014','PASSION24.HOUR.15.P015'],
 ['PASSION24.HOUR.19.P183','PASSION24.HOUR.19.P184'],
 ['PASSION24.HOUR.19.P185','PASSION24.HOUR.19.P186'],]
async def main():
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  p=await b.new_page(); await p.set_content(HTML,wait_until='domcontentloaded')
  d=await p.evaluate('''()=>{
   const strong=[]; const broad=[];
   for(const h of CORPUS.hours||[]){const ps=(h.paragraphs||[]).filter(x=>x&&x.t);for(let i=0;i<ps.length-1;i++){
    const a=ps[i],b=ps[i+1],at=a.t.trim(),bt=b.t.trim();if(!at||!bt)continue;const first=bt[0]||'';const lower=first===first.toLocaleLowerCase('fr-FR')&&first!==first.toLocaleUpperCase('fr-FR');const comma=at.endsWith(',');
    if(comma&&lower)strong.push({hour:h.hour_number,a:a.id,b:b.id,a_tail:at.slice(-180),b_head:bt.slice(0,180)});
    if(/[,:;]$/.test(at)||lower) broad.push({hour:h.hour_number,a:a.id,b:b.id});
   }}
   return {groups:CONTINUITY_GROUPS,strong,broadCount:broad.length};
  }''')
  await b.close()
 strong_pairs=[[x['a'],x['b']] for x in d['strong']]
 expected_strong=APPROVED[:2]+[APPROVED[2]]
 status='PASS' if d['groups']==APPROVED and strong_pairs==expected_strong else 'FAIL'
 out={'schema':'L24H_V101125_CONTINUITY_CANDIDATE_AUDIT_V1','version':'v101.125','status':status,'approved_universe':APPROVED,'broad_punctuation_or_lowercase_candidate_count':d['broadCount'],'strong_comma_to_lowercase_candidates':d['strong'],'strong_candidate_pairs':strong_pairs,'interpretation':'The exhaustive strong grammatical signature finds exactly Hour 3 P012→P013, Hour 13 P011→P013 and Hour 15 P014→P015. The other two approved Hour 19 continuity operations are source/adjudication-backed continuations not expressible by that heuristic. No additional strong ungrouped comma→lowercase candidate remains.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'status':status,'strong':len(strong_pairs),'broad':d['broadCount']})); raise SystemExit(0 if status=='PASS' else 2)
asyncio.run(main())
