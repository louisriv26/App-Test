import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH=Path('/mnt/data/L24H_v101111_RA19E2_M2_CANDIDATE_TREE/luisa_24_heures.html')
HTML=HTML_PATH.read_text(encoding='utf-8')
OUT=Path('/mnt/data/L24H_RA19E2_M3_2026-08-25/M3_INDEPENDENT_RUNTIME_RECHECK.json')
MD=Path('/mnt/data/L24H_RA19E2_M3_2026-08-25/M3_INDEPENDENT_RUNTIME_RECHECK.md')
VPS=[('phone',390,844),('tablet',820,1180),('desktop',1200,900)]

async def render_probe(page,pid,offset):
    return await page.evaluate('''([pid,offset])=>{
      const text=getFullParaText(pid);
      if(typeof text!=='string') return {missing:true,reason:'no_text'};
      const host=document.createElement('div');
      host.id='independent-probe';
      host.innerHTML=renderParaText(text,pid);
      document.body.appendChild(host);
      const walker=document.createTreeWalker(host,NodeFilter.SHOW_TEXT);
      let n,base=0,state={missing:false,source:text,rendered:host.textContent,html:host.innerHTML};
      while((n=walker.nextNode())){
        const L=n.nodeValue.length;
        if(offset>=base && offset<base+L){
          const p=n.parentElement;
          Object.assign(state,{char:n.nodeValue[offset-base],jesus:!!p.closest('.sp-jesus'),father:!!p.closest('.sp-father'),mary:!!p.closest('.sp-mary'),hidden:!!p.closest('.speech-quote-hidden'),classes:p.className||'',breaks:host.querySelectorAll('.speech-presentation-visual-break').length});
          break;
        }
        base+=L;
      }
      host.remove(); return state;
    }''',[pid,offset])

async def text_probe(page,pid):
    return await page.evaluate('''pid=>{
      const text=getFullParaText(pid); const host=document.createElement('div');
      host.innerHTML=renderParaText(text,pid); document.body.appendChild(host);
      const out={source:text,rendered:host.textContent,breaks:host.querySelectorAll('.speech-presentation-visual-break').length,hidden:host.querySelectorAll('.speech-quote-hidden').length,jesusSpans:host.querySelectorAll('.sp-jesus').length}; host.remove(); return out;
    }''',pid)

async def main():
  rows=[]
  def add(vp,gate,test,target,ok,evidence): rows.append({'viewport':vp,'gate':gate,'test':test,'target':target,'status':'PASS' if ok else 'FAIL','evidence':evidence})
  async with async_playwright() as p:
    browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for label,w,h in VPS:
      page=await browser.new_page(viewport={'width':w,'height':h})
      errs=[]; page.on('pageerror',lambda e,a=errs:a.append(str(e)))
      await page.set_content(HTML,wait_until='load',timeout=30000)
      # G17 direct-render probes for all ten actions, no view-navigation/openLibraryText use.
      cases=[
        ('SA001','PASSION24.TEXT.RELATED_HOUR_06.BODY.P053',122,'«',True,False),
        ('SA002','PASSION24.TEXT.RELATED_HOUR_06.BODY.P068',312,'«',True,False),
        ('SA003','PASSION24.TEXT.RELATED_HOUR_13.BODY.P056',129,'e',True,False),
        ('SA004','PASSION24.TEXT.RELATED_HOUR_15.BODY.P096',225,'"',True,False),
        ('SA005','PASSION24.TEXT.RELATED_HOUR_15.BODY.P097',0,'C',True,False),
        ('SA006','PASSION24.TEXT.RELATED_HOUR_15.BODY.P098',0,'I',True,False),
        ('SA007','PASSION24.TEXT.RELATED_HOUR_15.BODY.P099',113,'"',True,False),
        ('SA008_Q','PASSION24.SECTION.BENEFITS.P139',76,'"',True,False),
        ('SA009','PASSION24.TEXT.RELATED_HOUR_21.BODY.P059',108,'N',False,False),
        ('SA010','PASSION24.TEXT.RELATED_HOUR_21.BODY.P147',167,'J',True,False),
      ]
      for test,pid,off,ch,jesus,hidden in cases:
        st=await render_probe(page,pid,off)
        ok=(st.get('char')==ch and st.get('jesus')==jesus and st.get('hidden')==hidden and st.get('rendered')==st.get('source'))
        if test=='SA003': ok=ok and st.get('breaks')==0
        add(label,'G17',test,pid,ok,{k:st.get(k) for k in ['char','jesus','hidden','breaks','classes']})
      # SA008 hidden outer quote separately
      st=await render_probe(page,'PASSION24.SECTION.BENEFITS.P139',77)
      add(label,'G17','SA008_hidden_outer','PASSION24.SECTION.BENEFITS.P139',st.get('char')=='»' and st.get('hidden') and st.get('rendered')==st.get('source'),{k:st.get(k) for k in ['char','jesus','hidden','breaks','classes']})
      # Semantic/adjudication postconditions via direct data inspection.
      meta=await page.evaluate('''()=>({
        h15raw:[SPEECH_DATA['PASSION24.TEXT.RELATED_HOUR_15.BODY.P097']||null,SPEECH_DATA['PASSION24.TEXT.RELATED_HOUR_15.BODY.P098']||null,SPEECH_DATA['PASSION24.TEXT.RELATED_HOUR_15.BODY.P099']||null],
        h15adj:['PASSION24.TEXT.RELATED_HOUR_15.BODY.P097','PASSION24.TEXT.RELATED_HOUR_15.BODY.P098','PASSION24.TEXT.RELATED_HOUR_15.BODY.P099'].map(k=>SPEECH_PRESENTATION_ADJUDICATIONS[k]),
        p139raw:SPEECH_DATA['PASSION24.SECTION.BENEFITS.P139']||null,
        p139adj:SPEECH_PRESENTATION_ADJUDICATIONS['PASSION24.SECTION.BENEFITS.P139'],
        p59stale:(SPEECH_PRESENTATION_PROJECTION['PASSION24.TEXT.RELATED_HOUR_21.BODY.P059']||{}).adjudications||null,
        p147adj:SPEECH_PRESENTATION_ADJUDICATIONS['PASSION24.TEXT.RELATED_HOUR_21.BODY.P147'],
        version:APP_VERSION
      })''')
      ok=(all(x is None for x in meta['h15raw']) and all(a and a[0]['semantic_speaker']=='GENERIC_SOUL' and a[0]['presentation_speaker']=='JESUS' for a in meta['h15adj']))
      add(label,'G17','semantic_generic_soul_h15','H15 P097-P099',ok,meta['h15adj'])
      ok=(meta['p139raw'] is None and meta['p139adj'] and meta['p139adj'][0]['semantic_speaker']=='GENERIC_SOUL' and meta['p139adj'][0]['presentation_speaker']=='JESUS')
      add(label,'G17','semantic_generic_soul_p139','BENEFITS P139',ok,meta['p139adj'])
      add(label,'G17','p59_stale_adjudication_absent','H21 P059',meta['p59stale'] is None,meta['p59stale'])
      a=meta['p147adj'][0] if meta['p147adj'] else {}
      add(label,'G17','p147_personified_voice_exact','H21 P147',a.get('semantic_speaker')=='PERSONIFIED_VOICE' and a.get('presentation_speaker')=='JESUS' and a.get('start')==167 and a.get('end')==194,a)
      # G18 independent regression controls using direct renderer only.
      controls=[
        ('P134_mirror','PASSION24.TEXT.PROMISES_BENEFITS.BODY.P134',76,True,False),
        ('H17_P067_other','PASSION24.TEXT.RELATED_HOUR_17.BODY.P067',43,True,False),
        ('H17_P073_other','PASSION24.TEXT.RELATED_HOUR_17.BODY.P073',55,True,False),
        ('H21_P094_other','PASSION24.TEXT.RELATED_HOUR_21.BODY.P094',115,True,False),
        ('H21_P059_luisa','PASSION24.TEXT.RELATED_HOUR_21.BODY.P059',108,False,False),
        ('H19_P019_luisa','PASSION24.TEXT.RELATED_HOUR_19.BODY.P019',50,False,False),
      ]
      for test,pid,off,j,hid in controls:
        st=await render_probe(page,pid,off)
        ok=st.get('jesus')==j and st.get('hidden')==hid and st.get('rendered')==st.get('source')
        add(label,'G18',test,pid,ok,{k:st.get(k) for k in ['char','jesus','father','mary','hidden','classes']})
      # mirror hidden wrapper control
      st=await render_probe(page,'PASSION24.TEXT.PROMISES_BENEFITS.BODY.P134',77)
      add(label,'G18','P134_hidden_outer','PASSION24.TEXT.PROMISES_BENEFITS.BODY.P134',st.get('hidden') and st.get('char')=='»',{'char':st.get('char'),'hidden':st.get('hidden')})
      # G19: text equality and stable version/page errors.
      affected=[c[1] for c in cases]
      for pid in sorted(set(affected)):
        ps=await text_probe(page,pid)
        add(label,'G19','direct_renderer_text_exact',pid,ps['rendered']==ps['source'],{'source_len':len(ps['source']),'rendered_len':len(ps['rendered']),'breaks':ps['breaks'],'hidden':ps['hidden']})
      add(label,'G19','APP_VERSION','global',meta['version']=='v101.111',meta['version'])
      add(label,'G19','PAGE_ERRORS_ZERO','global',not errs,errs)
      await page.close()
    await browser.close()
  gates={g:('PASS' if all(r['status']=='PASS' for r in rows if r['gate']==g) else 'FAIL') for g in ['G17','G18','G19']}
  status='PASS_RUNTIME_PRESENTATION_MATRIX_INDEPENDENT' if all(v=='PASS' for v in gates.values()) else 'FAIL'
  obj={'stage':'RA19E2_M3_INDEPENDENT_DIRECT_RENDERER_RECHECK','contract_origin':'RECONSTRUCTED_NOT_HISTORICALLY_RECOVERED','implementation_independence':'Direct renderParaText/getFullParaText temporary-DOM probes; does not call openLibraryText/openSection or reuse primary para-state helpers.','browser':'system Chromium via Playwright page.set_content','navigation_limitation':'Normal URL/file navigation is blocked by environment policy. This audit does not claim real origin, service-worker, offline, installed-PWA, or physical-device proof.','viewports':VPS,'gates':gates,'rows_total':len(rows),'rows_pass':sum(r['status']=='PASS' for r in rows),'status':status,'rows':rows}
  OUT.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
  MD.write_text(f"# M3 independent direct-renderer runtime recheck\n\n**Status: {status}**\n\n- Implementation: direct `renderParaText()` temporary-DOM probes, independent of the primary navigation-based harness.\n- Browser: system Chromium via Playwright content injection.\n- Viewports: phone, tablet, desktop.\n- G17: {gates['G17']}\n- G18: {gates['G18']}\n- G19: {gates['G19']}\n- Checks: {obj['rows_pass']}/{obj['rows_total']} PASS.\n- Limitation: normal URL navigation is blocked by environment policy; service-worker/offline/PWA/physical-device behaviour is not claimed.\n",encoding='utf-8')
  print(status,gates,obj['rows_pass'],obj['rows_total'])
  for r in rows:
    if r['status']!='PASS': print('FAIL',r)

asyncio.run(main())
