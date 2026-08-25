import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

HTML=Path('/mnt/data/L24H_v101111_RA19E2_M2_CANDIDATE_TREE/luisa_24_heures.html').read_text(encoding='utf-8')
OUT=Path('/mnt/data/L24H_RA19E2_M3_2026-08-25/M3_CHROMIUM_RUNTIME_MATRIX.json')
VIEWPORTS=[('phone',390,844),('tablet',820,1180),('desktop',1200,900)]

async def char_state(page,pid,offset):
    return await page.evaluate('''([pid,offset])=>{
      const root=document.getElementById(pid); if(!root) return {missing:true};
      const el=root.querySelector('.para-text')||root;
      const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT); let n,base=0;
      while((n=w.nextNode())){ const L=n.nodeValue.length; if(offset>=base && offset<base+L){
        const p=n.parentElement; return {missing:false,char:n.nodeValue[offset-base],jesus:!!p.closest('.sp-jesus'),father:!!p.closest('.sp-father'),mary:!!p.closest('.sp-mary'),hidden:!!p.closest('.speech-quote-hidden'),classes:p.className||'',localOffset:offset-base,textNode:n.nodeValue}; }
        base+=L;
      }
      return {missing:false,outOfRange:true,total:base};
    }''',[pid,offset])

async def para_state(page,pid):
    return await page.evaluate('''pid=>{const root=document.getElementById(pid);if(!root)return {missing:true};const el=root.querySelector('.para-text')||root;return {missing:false,text:el.textContent,html:el.innerHTML,jesusSpans:el.querySelectorAll('.sp-jesus').length,hidden:el.querySelectorAll('.speech-quote-hidden').length,breaks:el.querySelectorAll('.speech-presentation-visual-break').length};}''',pid)

async def open_lib(page,item):
    await page.evaluate("id=>openLibraryText(id,false)",item); await page.wait_for_timeout(30)
async def open_section(page,id):
    await page.evaluate("id=>openSection(id,false)",id); await page.wait_for_timeout(30)

async def run_view(page,label):
    rows=[]
    def rec(gate,test,target,ok,evidence): rows.append({'viewport':label,'gate':gate,'test':test,'target':target,'status':'PASS' if ok else 'FAIL','evidence':evidence})
    # H06 actions 1/2
    await open_lib(page,'PASSION24.TEXT.RELATED_HOUR_06')
    for pid,off,tid in [('PASSION24.TEXT.RELATED_HOUR_06.BODY.P053',122,'SA001'),('PASSION24.TEXT.RELATED_HOUR_06.BODY.P068',312,'SA002')]:
        st=await char_state(page,pid,off); rec('G17',tid+'_meaningful_open_quote_visible_jesus',pid,st.get('char')=='«' and st.get('jesus') and not st.get('hidden'),st)
    # H13 action3
    await open_lib(page,'PASSION24.TEXT.RELATED_HOUR_13'); pid='PASSION24.TEXT.RELATED_HOUR_13.BODY.P056'; st=await char_state(page,pid,129); ps=await para_state(page,pid); rec('G17','SA003_et_jesus_no_break',pid,st.get('char')=='e' and st.get('jesus') and ps.get('breaks')==0,{'char':st,'breaks':ps.get('breaks')})
    # H15 actions 4-7
    await open_lib(page,'PASSION24.TEXT.RELATED_HOUR_15')
    for pid,off,test,ch in [('PASSION24.TEXT.RELATED_HOUR_15.BODY.P096',225,'SA004_final_open_quote','"'),('PASSION24.TEXT.RELATED_HOUR_15.BODY.P097',0,'SA005_outer_display','C'),('PASSION24.TEXT.RELATED_HOUR_15.BODY.P098',0,'SA006_outer_display','I'),('PASSION24.TEXT.RELATED_HOUR_15.BODY.P099',113,'SA007_final_close_quote','"')]:
        st=await char_state(page,pid,off); rec('G17',test,pid,st.get('char')==ch and st.get('jesus') and not st.get('hidden'),st)
    sem=await page.evaluate('''()=>({p97:SPEECH_DATA['PASSION24.TEXT.RELATED_HOUR_15.BODY.P097']||null,p98:SPEECH_DATA['PASSION24.TEXT.RELATED_HOUR_15.BODY.P098']||null,p99:SPEECH_DATA['PASSION24.TEXT.RELATED_HOUR_15.BODY.P099']||null,a97:SPEECH_PRESENTATION_ADJUDICATIONS['PASSION24.TEXT.RELATED_HOUR_15.BODY.P097'],a98:SPEECH_PRESENTATION_ADJUDICATIONS['PASSION24.TEXT.RELATED_HOUR_15.BODY.P098'],a99:SPEECH_PRESENTATION_ADJUDICATIONS['PASSION24.TEXT.RELATED_HOUR_15.BODY.P099']})''')
    rec('G17','SA005_007_semantic_generic_soul','H15 P097-P099',not sem['p97'] and not sem['p98'] and not sem['p99'] and all(sem[k][0]['semantic_speaker']=='GENERIC_SOUL' for k in ['a97','a98','a99']),sem)
    # Benefits action8
    await open_section(page,'PASSION24.SECTION.BENEFITS'); pid='PASSION24.SECTION.BENEFITS.P139'; q=await char_state(page,pid,76); outer=await char_state(page,pid,77); ps=await para_state(page,pid); rec('G17','SA008_mirror_quote_and_hidden_outer',pid,q.get('char')=='"' and q.get('jesus') and not q.get('hidden') and outer.get('char')=='»' and outer.get('hidden') and ps.get('breaks')==0,{'quote':q,'outer':outer,'breaks':ps.get('breaks')})
    sem139=await page.evaluate("()=>({raw:SPEECH_DATA['PASSION24.SECTION.BENEFITS.P139']||null,adj:SPEECH_PRESENTATION_ADJUDICATIONS['PASSION24.SECTION.BENEFITS.P139']})"); rec('G17','SA008_semantic_generic_soul',pid,sem139['raw'] is None and sem139['adj'][0]['semantic_speaker']=='GENERIC_SOUL',sem139)
    # H21 actions9/10
    await open_lib(page,'PASSION24.TEXT.RELATED_HOUR_21'); p59='PASSION24.TEXT.RELATED_HOUR_21.BODY.P059'; lu=await char_state(page,p59,108); stale=await page.evaluate("()=>SPEECH_PRESENTATION_PROJECTION['PASSION24.TEXT.RELATED_HOUR_21.BODY.P059'].adjudications||null"); rec('G17','SA009_luisa_stays_non_jesus_no_stale_active_adj',p59,lu.get('char')=='N' and not lu.get('jesus') and stale is None,{'char':lu,'adjudications':stale})
    p147='PASSION24.TEXT.RELATED_HOUR_21.BODY.P147'; pv=await char_state(page,p147,167); sem147=await page.evaluate("()=>SPEECH_PRESENTATION_ADJUDICATIONS['PASSION24.TEXT.RELATED_HOUR_21.BODY.P147']"); rec('G17','SA010_personified_semantic_outer_jesus',p147,pv.get('char')=='J' and pv.get('jesus') and sem147[0]['semantic_speaker']=='PERSONIFIED_VOICE' and sem147[0]['start']==167 and sem147[0]['end']==194,{'char':pv,'adj':sem147})
    # G18 regression controls
    # PROMISES P134 exact mirror model
    await open_lib(page,'PASSION24.TEXT.PROMISES_BENEFITS'); p134='PASSION24.TEXT.PROMISES_BENEFITS.BODY.P134'; q=await char_state(page,p134,76); o=await char_state(page,p134,77); rec('G18','P134_existing_mirror_control',p134,q.get('char')=='"' and q.get('jesus') and not q.get('hidden') and o.get('hidden'),{'q':q,'outer':o})
    # H17 nested OTHER remains Jesus display
    await open_lib(page,'PASSION24.TEXT.RELATED_HOUR_17');
    for pid,off in [('PASSION24.TEXT.RELATED_HOUR_17.BODY.P067',43),('PASSION24.TEXT.RELATED_HOUR_17.BODY.P073',55)]:
        st=await char_state(page,pid,off); rec('G18','nested_OTHER_outer_jesus',pid,st.get('jesus') and not st.get('hidden'),st)
    # H21 P094 nested OTHER & P059 Luisa control
    await open_lib(page,'PASSION24.TEXT.RELATED_HOUR_21'); p94='PASSION24.TEXT.RELATED_HOUR_21.BODY.P094'; st=await char_state(page,p94,115); rec('G18','P094_nested_OTHER_outer_jesus',p94,st.get('jesus') and not st.get('hidden'),st); st=await char_state(page,p59,108); rec('G18','P059_Luisa_control',p59,not st.get('jesus') and not st.get('mary') and not st.get('father'),st)
    # H19 P019 Luisa complaint control
    await open_lib(page,'PASSION24.TEXT.RELATED_HOUR_19'); p19='PASSION24.TEXT.RELATED_HOUR_19.BODY.P019'; st=await char_state(page,p19,50); rec('G18','P019_Luisa_control',p19,not st.get('jesus') and not st.get('mary') and not st.get('father'),st)
    # G19: exact text preservation for affected targets and no unexpected visible breaks on changed presentation targets
    targets=['PASSION24.TEXT.RELATED_HOUR_06.BODY.P053','PASSION24.TEXT.RELATED_HOUR_06.BODY.P068','PASSION24.TEXT.RELATED_HOUR_13.BODY.P056','PASSION24.TEXT.RELATED_HOUR_15.BODY.P096','PASSION24.TEXT.RELATED_HOUR_15.BODY.P097','PASSION24.TEXT.RELATED_HOUR_15.BODY.P098','PASSION24.TEXT.RELATED_HOUR_15.BODY.P099','PASSION24.SECTION.BENEFITS.P139','PASSION24.TEXT.RELATED_HOUR_21.BODY.P059','PASSION24.TEXT.RELATED_HOUR_21.BODY.P147']
    groups={'PASSION24.TEXT.RELATED_HOUR_06':[targets[0],targets[1]],'PASSION24.TEXT.RELATED_HOUR_13':[targets[2]],'PASSION24.TEXT.RELATED_HOUR_15':targets[3:7],'SECTION':[targets[7]],'PASSION24.TEXT.RELATED_HOUR_21':targets[8:]}
    for group,pids in groups.items():
        if group=='SECTION': await open_section(page,'PASSION24.SECTION.BENEFITS')
        else: await open_lib(page,group)
        for pid in pids:
            ps=await para_state(page,pid); src=await page.evaluate('pid=>getFullParaText(pid)',pid); rec('G19','rendered_textContent_exact',pid,not ps.get('missing') and ps.get('text')==src,{'render_len':len(ps.get('text','')),'source_len':len(src or '')})
    return rows

async def main():
    allrows=[]; errors=[]
    async with async_playwright() as p:
      browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
      for label,w,h in VIEWPORTS:
        page=await browser.new_page(viewport={'width':w,'height':h})
        perr=[]; page.on('pageerror',lambda e,arr=perr: arr.append(str(e)))
        await page.set_content(HTML,wait_until='load',timeout=30000)
        version=await page.evaluate('APP_VERSION'); rows=await run_view(page,label); allrows.extend(rows)
        allrows.append({'viewport':label,'gate':'G19','test':'APP_VERSION','target':'global','status':'PASS' if version=='v101.111' else 'FAIL','evidence':version})
        allrows.append({'viewport':label,'gate':'G19','test':'PAGE_ERRORS_ZERO','target':'global','status':'PASS' if not perr else 'FAIL','evidence':perr})
        errors.extend((label,x) for x in perr); await page.close()
      await browser.close()
    gates={g:('PASS' if all(r['status']=='PASS' for r in allrows if r['gate']==g) else 'FAIL') for g in ['G17','G18','G19']}
    out={'stage':'RA19E2_M3_CHROMIUM_RUNTIME_PRESENTATION_MATRIX','contract_origin':'RECONSTRUCTED_NOT_HISTORICALLY_RECOVERED','browser':'system Chromium / Playwright set_content content-injection harness','navigation_limitation':'Normal URL/file navigation is blocked by environment policy; service-worker/origin behaviour is not claimed here.','viewports':VIEWPORTS,'gates':gates,'rows_total':len(allrows),'rows_pass':sum(r['status']=='PASS' for r in allrows),'status':'PASS_RUNTIME_PRESENTATION_MATRIX' if all(v=='PASS' for v in gates.values()) else 'FAIL','rows':allrows}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(out['status'],out['gates'],out['rows_pass'],out['rows_total'])
    for r in allrows:
      if r['status']!='PASS': print('FAIL',r)

asyncio.run(main())
