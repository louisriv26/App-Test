#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2]); VERSION='v101.123'; STAGE='FOUR_PASS_BUILD_REPRODUCIBILITY_AND_SELF_AUDIT_RECONCILIATION_R1'
profiles=[
 ('phone',390,844,'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad_portrait',820,1180,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad_landscape',1180,820,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('desktop',1200,900,'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/142.0 Safari/537.36'),
 ('samsung',412,915,'Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 Chrome/142.0 Mobile Safari/537.36 SamsungBrowser/28.0')]
async def main():
 rows=[]
 def add(profile,check,ok,detail=None): rows.append({'profile':profile,'check':check,'status':'PASS' if ok else 'FAIL','detail':detail})
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,w,h,ua in profiles:
   ctx=await browser.new_context(viewport={'width':w,'height':h},user_agent=ua)
   page=await ctx.new_page(); errors=[]; page.on('pageerror',lambda e: errors.append(str(e)))
   await page.set_content(HTML,wait_until='domcontentloaded'); await page.wait_for_timeout(80)
   base=await page.evaluate("() => ({version:APP_VERSION,stage:APP_EVIDENCE_STAGE})")
   add(label,'version_stage',base['version']==VERSION and base['stage']==STAGE,base)
   opened=await page.evaluate('''() => { try { let inv=document.getElementById('__helpTestInvoker'); if(!inv){inv=document.createElement('button');inv.id='__helpTestInvoker';inv.textContent='Aide test';document.body.appendChild(inv);} inv.focus(); showHelp(); const o=document.getElementById('helpModalOverlay'); const m=o&&o.querySelector('.help-modal'); const sc=o&&o.querySelector('.help-modal-scroll'); const secs=o?[...o.querySelectorAll('.help-section')]:[]; const qs=o?[...o.querySelectorAll('.help-quick-btn')]:[]; return {ok:!!o&&!!m&&!!sc,role:o&&o.getAttribute('role'),modal:o&&o.getAttribute('aria-modal'),sections:secs.length,rows:o?o.querySelectorAll('.help-row').length:0,quick:qs.length,sectionIds:secs.map(x=>x.id),quickText:qs.map(x=>x.innerText.trim()),text:o?o.innerText:'',hOverflow:sc?sc.scrollWidth-sc.clientWidth:null}; } catch(e){return {ok:false,error:String(e)}} }''')
   add(label,'help_opens_semantic_dialog',opened.get('ok') and opened.get('role')=='dialog' and opened.get('modal')=='true',opened)
   add(label,'help_structure_12_36_9',opened.get('sections')==12 and opened.get('rows')==36 and opened.get('quick')==9,{'sections':opened.get('sections'),'rows':opened.get('rows'),'quick':opened.get('quick')})
   expected=['help-practice','help-navigation','help-reading','help-actions','help-espace','help-reperes','help-search','help-samsung','help-share','help-backup','help-update','help-support']
   add(label,'help_section_order',opened.get('sectionIds')==expected,opened.get('sectionIds'))
   add(label,'practice_first_quick',bool(opened.get('quickText')) and opened['quickText'][0]=='Comment pratiquer les 24 Heures',opened.get('quickText'))
   text=opened.get('text','')
   add(label,'attribution_clarity',('sans être attribuée' in text and 'Badges Jésus / Père / Marie' in text and 'Paroles directes' in text),None)
   add(label,'stale_highlight_clarity',('Cela ne signifie pas que le texte de Luisa est signalé comme douteux' in text),None)
   add(label,'sharing_guidance',('Réglages → Référence du passage → Partager' in text and 'Copier le lien' in text),None)
   add(label,'misleading_old_wording_absent',('Trois usages distincts' not in text and 'sans perdre volontairement' not in text),None)
   add(label,'no_help_horizontal_overflow',opened.get('hOverflow') is not None and opened.get('hOverflow')<=2,opened.get('hOverflow'))
   jumps=await page.evaluate('''async () => { const btn=[...document.querySelectorAll('#helpModalOverlay .help-quick-btn')]; const out=[]; for(const b of btn){ const m=(b.getAttribute('onclick')||'').match(/helpJumpTo\('([^']+)'\)/); const id=m&&m[1]; const ok=id?helpJumpTo(id):false; await new Promise(r=>setTimeout(r,260)); const target=id&&document.getElementById(id); const hd=target&&target.querySelector('.help-section-hd'); out.push({id,ok,exists:!!target,focused:document.activeElement===hd}); } return out; }''')
   add(label,'all_quick_links_resolve_and_focus',len(jumps)==9 and all(x['ok'] and x['exists'] and x['focused'] for x in jumps),jumps)
   bottom=await page.evaluate('''() => { const sc=document.querySelector('#helpModalOverlay .help-modal-scroll'); sc.scrollTop=sc.scrollHeight; const max=sc.scrollHeight-sc.clientHeight; const sup=document.getElementById('help-support'); const r=sup.getBoundingClientRect(), sr=sc.getBoundingClientRect(); return {atBottom:Math.abs(sc.scrollTop-max)<=2,supportVisible:r.top<sr.bottom && r.bottom>sr.top,scrollTop:sc.scrollTop,max}; }''')
   add(label,'help_reaches_final_section',bottom['atBottom'] and bottom['supportVisible'],bottom)
   await page.evaluate("() => closeHelpModal()")
   await page.wait_for_timeout(50)
   focus=await page.evaluate("() => ({closed:!document.getElementById('helpModalOverlay'), active:document.activeElement&&document.activeElement.id})")
   add(label,'help_close_restores_focus',focus['closed'] and focus['active']=='__helpTestInvoker',focus)
   add(label,'no_page_errors',not errors,errors)
   await ctx.close()
  await browser.close()
 summary={'profiles':len(profiles),'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
 OUT.write_text(json.dumps({'schema':'L24H_V101121_HELP_BROWSER_MATRIX_V1','version':VERSION,'browser':'system Chromium via Playwright content injection','real_device_limitation':'Not physical Safari/Samsung/TalkBack/VoiceOver evidence','summary':summary,'results':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary))
 if summary['fail']:
  for r in rows:
   if r['status']=='FAIL': print('FAIL',r)
  raise SystemExit(2)
asyncio.run(main())
