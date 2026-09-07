#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2])
P=[('phone',390,844,'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),('ipad_p',820,1180,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),('ipad_l',1180,820,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),('desktop',1200,900,'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/142.0 Safari/537.36'),('samsung',412,915,'Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 Chrome/142.0 Mobile Safari/537.36 SamsungBrowser/28.0')]
async def main():
 rows=[]
 def add(p,n,ok,d=None):rows.append({'profile':p,'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,w,h,ua in P:
   c=await b.new_context(viewport={'width':w,'height':h},user_agent=ua); pg=await c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); await pg.set_content(HTML,wait_until='domcontentloaded'); await pg.wait_for_timeout(60)
   # Inject a visible real invoker only to test the modal's generic focus-return contract without relying on legacy/hidden toolbar controls.
   await pg.evaluate("""()=>{const b=document.createElement('button');b.id='independentHelpInvoker';b.textContent='Aide';b.style.cssText='position:fixed;top:2px;left:2px;z-index:99999';document.body.appendChild(b);b.focus();showHelp();}"""); await pg.wait_for_timeout(80)
   x=await pg.evaluate("""()=>{const o=document.getElementById('helpModalOverlay'),m=o&&o.querySelector('.help-modal'),s=o&&o.querySelector('.help-modal-scroll'),secs=[...o.querySelectorAll('.help-section')],rows=[...o.querySelectorAll('.help-row')],qs=[...o.querySelectorAll('.help-quick-btn')];const text=o?o.innerText:'';return{role:o&&o.getAttribute('role'),modal:o&&o.getAttribute('aria-modal'),aria:o&&o.getAttribute('aria-label'),sections:secs.length,helpRows:rows.length,quick:qs.length,ids:secs.map(e=>e.id),firstQuick:qs[0]&&qs[0].innerText,attribution:text.includes('sans être attribuée')&&text.includes('directement attribuées'),stale:text.includes('Cela ne signifie pas que le texte de Luisa est signalé comme douteux'),share:text.includes('Réglages → Référence du passage → Partager')&&text.includes('Copier le lien'),overflow:s?Math.max(0,s.scrollWidth-s.clientWidth):999,quickTargets:qs.map(q=>((q.getAttribute('onclick')||'').match(/helpJumpTo\\('([^']+)'\\)/)||[])[1]).filter(Boolean)}}""")
   add(label,'dialog_semantics',x['role']=='dialog' and x['modal']=='true' and x['aria']=='Aide et À propos',x)
   add(label,'structure_12_36_9',x['sections']==12 and x['helpRows']==36 and x['quick']==9,{'sections':x['sections'],'rows':x['helpRows'],'quick':x['quick']})
   add(label,'practice_first',x['ids'][0]=='help-practice' and x['firstQuick']=='Comment pratiquer les 24 Heures',{'first':x['ids'][0],'quick':x['firstQuick']})
   add(label,'attribution_clarity',x['attribution'])
   add(label,'stale_highlight_clarity',x['stale'])
   add(label,'sharing_guidance',x['share'])
   q=await pg.evaluate("""()=>{const bs=[...document.querySelectorAll('#helpModalOverlay .help-quick-btn')];let bad=[];for(const b of bs){const m=(b.getAttribute('onclick')||'').match(/helpJumpTo\('([^']+)'\)/);const id=m&&m[1],e=id&&document.getElementById(id);if(!e||helpJumpTo(id)!==true)bad.push(id||'missing')}return bad}""")
   add(label,'all_quick_targets_resolve',len(q)==0,q)
   add(label,'no_horizontal_help_overflow',x['overflow']<=2,x['overflow'])
   reach=await pg.evaluate("""()=>{const s=document.querySelector('#helpModalOverlay .help-modal-scroll'),last=document.getElementById('help-support');s.scrollTop=s.scrollHeight;const r=last.getBoundingClientRect(),sr=s.getBoundingClientRect();return{bottom:s.scrollTop+s.clientHeight,max:s.scrollHeight,visible:r.top<sr.bottom&&r.bottom>sr.top}}""")
   add(label,'final_section_reachable',reach['bottom']>=reach['max']-3 and reach['visible'],reach)
   await pg.evaluate("closeHelpModal()"); await pg.wait_for_timeout(30); foc=await pg.evaluate("()=>document.activeElement&&document.activeElement.id"); add(label,'close_restores_invoker_and_no_errors',foc=='independentHelpInvoker' and not errs,{'focus':foc,'errors':errs})
   await c.close()
  await b.close()
 sm={'profiles':5,'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
 OUT.write_text(json.dumps({'schema':'L24H_V101121_INDEPENDENT_HELP_BROWSER_V1','implementation':'separately coded modal/quick-link/focus/overflow probe','summary':sm,'results':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
asyncio.run(main())
