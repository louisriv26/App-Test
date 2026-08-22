from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re,sys,collections
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
H=(ROOT/'index.html').read_text('utf8')
def pc(n):
 m=re.search(r'const\s+'+re.escape(n)+r'\s*=\s*',H);return json.JSONDecoder().raw_decode(H[m.end():])[0]
layout=pc('LDC_LIBRARY_FLOW_LAYOUT');R={'before':{},'after':{},'surfaces':0,'groups':0,'expected_groups':0,'mismatches':[],'errors':[]}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for item in layout:
  pg=b.new_page(viewport={'width':390,'height':844});errs=[];pg.on('pageerror',lambda e,errs=errs:errs.append(str(e)));pg.set_content(H,wait_until='commit')
  o=pg.evaluate("""item=>{openLibraryText(item,false);const ss=[...document.querySelectorAll('.ldc-flow-surface')];const count=()=>[...document.querySelectorAll('.ldc-flow-surface [data-ldc-boundary-action]')].reduce((o,e)=>(o[e.dataset.ldcBoundaryAction]=(o[e.dataset.ldcBoundaryAction]||0)+1,o),{});const before=count();const sb=ss.map(s=>({e:1+[...s.querySelectorAll('[data-ldc-boundary-action=\"paragraph_break\"]')].length,a:getFlowVisualParagraphGroups(s).length}));[...document.querySelectorAll('.ldc-flow-surface .para-text')].forEach(e=>rerenderPara(e.dataset.paraId));return {before,after:count(),sb,sa:ss.map(s=>({e:1+[...s.querySelectorAll('[data-ldc-boundary-action=\"paragraph_break\"]')].length,a:getFlowVisualParagraphGroups(s).length}))}}""",item)
  for k,v in o['before'].items():R['before'][k]=R['before'].get(k,0)+v
  for k,v in o['after'].items():R['after'][k]=R['after'].get(k,0)+v
  for x in o['sb']:R['surfaces']+=1;R['groups']+=x['a'];R['expected_groups']+=x['e'];R['mismatches'] += ([] if x['a']==x['e'] else [x])
  for x in o['sa']:R['mismatches'] += ([] if x['a']==x['e'] else [x])
  R['errors']+=errs;pg.close()
 # representative preserve action geometry + exact selection + samsung same group across preserve break
 pg=b.new_page(viewport={'width':390,'height':844});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.set_content(H,wait_until='commit')
 rep=pg.evaluate("""()=>{const item=Object.keys(LDC_LIBRARY_FLOW_LAYOUT).find(id=>LDC_LIBRARY_FLOW_LAYOUT[id].some(b=>Object.values(b.intra_actions||{}).some(d=>Object.values(d).includes('preserve_break'))||Object.values(b.break_before_actions||{}).includes('preserve_break')));openLibraryText(item,false);const br=document.querySelector('[data-ldc-boundary-action=\"preserve_break\"]');const surf=br.closest('.ldc-flow-surface');const g=getFlowVisualParagraphGroups(surf);const s=getComputedStyle(br);let el=br.closest('.para-text');if(!el){const n=br.nextElementSibling||br.previousElementSibling;el=n&&n.querySelector?n.querySelector('.para-text'):null;}const targetEl=surf.querySelector('.para-text');const pid=targetEl.dataset.paraId,full=getFullParaText(pid)||targetEl.textContent||'';window.commitDurableChange=()=>({ok:true});window.showToast=()=>{};state.textHighlights={};state._pending={paraId:pid,start:10,end:30,text:full.slice(10,30)};document.getElementById('cpRemoveBtn').dataset.hlId='';applyHighlight('yellow');const ar=[...surf.querySelectorAll('[data-ldc-boundary-action]')].map(x=>x.dataset.ldcBoundaryAction);return {item,groups:g.length,geom:{display:s.display,height:s.height,mt:s.marginTop,mb:s.marginBottom},actions:ar,exact:(state.textHighlights[pid]||[])[0]&&[(state.textHighlights[pid][0].start_offset??state.textHighlights[pid][0].start),(state.textHighlights[pid][0].end_offset??state.textHighlights[pid][0].end)]}}""")
 R['representative']=rep;R['errors']+=errs;pg.close()
 pg=b.new_page();pg.set_content(H,wait_until='commit');pg.evaluate("openLibraryText('PASSION24.TEXT.PROMISES_BENEFITS',false)");R['promesses_jesus']=pg.locator('.sp-jesus').count();R['dups']=pg.evaluate("()=>{const a=[...document.querySelectorAll('[id]')].map(x=>x.id);return a.length-new Set(a).size}");pg.close();b.close()
assert R['before']=={'paragraph_break':1518,'preserve_break':100},R['before'];assert R['after']==R['before'];assert R['surfaces']==66 and R['groups']==1584 and R['expected_groups']==1584 and not R['mismatches'];assert R['representative']['geom']['display']=='block' and R['representative']['geom']['height']=='0px' and R['representative']['geom']['mt']=='0px' and R['representative']['geom']['mb']=='0px';assert R['representative']['exact']==[10,30];assert R['promesses_jesus']==145 and R['dups']==0 and not R['errors']
(ROOT/'reports/v10199_runtime_results.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'actions':R['after'],'surfaces':R['surfaces'],'groups':R['groups'],'promesses_jesus':R['promesses_jesus']}))
