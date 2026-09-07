#!/usr/bin/env python3
import asyncio,csv,json,sys,tempfile
from pathlib import Path
from playwright.async_api import async_playwright
SRC=Path(sys.argv[1]).read_text(encoding='utf-8'); LEDGER=Path(sys.argv[2]); OUT=Path(sys.argv[3]); rows=list(csv.DictReader(LEDGER.open(encoding='utf-8-sig')))
SPEECH=[r for r in rows if r['renderer_family']=='speech_break']; LDC=[r for r in rows if r['renderer_family']=='ldc_intra_break']
async def count_fail(html, subset):
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=await b.new_page(viewport={'width':1200,'height':900});await p.set_content(html,wait_until='domcontentloaded')
  x=await p.evaluate('''rows=>rows.map(r=>{const t=getFullParaText(r.record_id)||'',off=Number(r.source_offset),d=document.createElement('div');d.className='para-text';d.style.cssText='position:absolute;left:40px;top:20px;width:700px';d.innerHTML=r.renderer_family==='ldc_intra_break'?renderLdcFlowFragmentText(t,r.record_id,[off],{[String(off)]:'paragraph_break'}):renderParaText(t,r.record_id);document.body.appendChild(d);function at(o){let b=0,w=document.createTreeWalker(d,NodeFilter.SHOW_TEXT),n;while(n=w.nextNode()){if(o>=b&&o<b+n.data.length){let q=document.createRange();q.setStart(n,o-b);q.setEnd(n,o-b+1);return q.getBoundingClientRect().x}b+=n.data.length}return null}const x=at(off+1)-d.getBoundingClientRect().x,exact=d.textContent===t,hidden=[...d.querySelectorAll('.visual-boundary-separator-space')].some(z=>z.getAttribute('aria-hidden')==='true');d.remove();return{x,exact,hidden}})''',subset)
  await b.close();return x
async def main():
 rs=[]
 def add(n,o,d=None):rs.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
 # A: disable speech arm only
 a=SRC.replace('/* V101133_SPEECH_BOUNDARY_SPACE_ARM */ zeroBoundarySpacePending = true;','/* V101133_SPEECH_BOUNDARY_SPACE_ARM */ zeroBoundarySpacePending = false;',1)
 xa=await count_fail(a,SPEECH);add('mutant_A_speech_path_detected',sum(z['x']>1 for z in xa)==78,{'failures':sum(z['x']>1 for z in xa)})
 # B: disable LDC arm only
 bb=SRC.replace("/* V101133_LDC_BOUNDARY_SPACE_ARM */ zeroLeadingBoundarySpace = action !== 'preserve_break';","/* V101133_LDC_BOUNDARY_SPACE_ARM */ zeroLeadingBoundarySpace = false;",1)
 xb=await count_fail(bb,LDC);add('mutant_B_ldc_path_detected',sum(z['x']>1 for z in xb)==4,{'failures':sum(z['x']>1 for z in xb)})
 # C: disable zero width CSS
 c=SRC.replace('font-size:0!important;line-height:0!important;','font-size:inherit!important;line-height:inherit!important;',1)
 xc=await count_fail(c,rows);add('mutant_C_css_detected',sum(z['x']>1 for z in xc)==82,{'failures':sum(z['x']>1 for z in xc)})
 # D: delete source separator content
 d=SRC.replace('${escHtml(text[from])}</span>','</span>',1)
 xd=await count_fail(d,rows[:10]);add('mutant_D_source_deletion_detected',any(not z['exact'] for z in xd),{'text_mismatches':sum(not z['exact'] for z in xd)})
 # E: aria-hide wrapper
 e=SRC.replace('data-visual-boundary-separator="u0020"','aria-hidden="true" data-visual-boundary-separator="u0020"',1)
 xe=await count_fail(e,rows[:10]);add('mutant_E_aria_hidden_detected',any(z['hidden'] for z in xe),{'aria_hidden':sum(z['hidden'] for z in xe)})
 sm={'pass':sum(x['status']=='PASS' for x in rs),'fail':sum(x['status']=='FAIL' for x in rs),'total':len(rs)};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps({'schema':'L24H_V101135_MUTANT_SENSITIVITY_V1','summary':sm,'rows':rs},indent=2)+'\n');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
asyncio.run(main())
