#!/usr/bin/env python3
import asyncio,csv,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');LEDGER=Path(sys.argv[2]);OUT=Path(sys.argv[3]);BASE=Path(sys.argv[4]).read_text(encoding='utf-8') if len(sys.argv)>4 else None
rows=list(csv.DictReader(LEDGER.open(encoding='utf-8-sig')))
reps=[]
for surf in ['Main Hour meditation text','Réflexions et pratiques','Promesses et bienfaits — main section','Promesses et bienfaits — Library mirror','Linked Livre du Ciel — Hours 1–24','Part III Livre du Ciel']:
 r=next((x for x in rows if x['surface']==surf),None)
 if r: reps.append(r)
JS='''r=>{const pid=r.record_id,off=Number(r.source_offset),t=getFullParaText(pid)||'',host=document.createElement('div');host.className='para-text';host.innerHTML=r.renderer_family==='ldc_intra_break'?renderLdcFlowFragmentText(t,pid,[off],{[String(off)]:'paragraph_break'}):renderParaText(t,pid);document.body.appendChild(host);const tw=document.createTreeWalker(host,NodeFilter.SHOW_TEXT);let n,b=0,a=null,z=null;while(n=tw.nextNode()){const e=b+n.data.length;if(off-2>=b&&off-2<e)a={n,o:off-2-b};if(off+3>=b&&off+3<e)z={n,o:off+3-b};b=e}let sel='';if(a&&z){const rg=document.createRange();rg.setStart(a.n,a.o);rg.setEnd(z.n,z.o);const s=getSelection();s.removeAllRanges();s.addRange(rg);sel=s.toString();s.removeAllRanges()}const wrapper=host.querySelector('.visual-boundary-separator-space');const tc=host.textContent;host.remove();return{pid,off,textExact:tc===t,selection:sel,wrapperText:wrapper?wrapper.textContent:null,wrapperAria:wrapper?wrapper.getAttribute('aria-hidden'):null}}'''
async def render(p,html,r):
 await p.goto('about:blank'); await p.set_content(html,wait_until='domcontentloaded');return await p.evaluate(JS,r)
async def main():
 rs=[]
 def add(n,o,d=None):rs.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=await b.new_page()
  for i,r in enumerate(reps):
   base=await render(p,BASE,r) if BASE else None
   d=await render(p,HTML,r)
   add('text_exact_'+str(i),d['textExact'],d)
   add('selection_preserved_vs_v101132_'+str(i),(not base) or d['selection']==base['selection'],{'baseline':base and base['selection'],'candidate':d['selection']})
   add('wrapper_preserves_space_'+str(i),d['wrapperText']==' ' and d['wrapperAria'] is None,d)
   await p.goto('about:blank'); await p.set_content(HTML,wait_until='domcontentloaded')
   x=await p.evaluate('''({pid,off,i})=>{const t=getFullParaText(pid),st=Math.max(0,off-2),en=Math.min(t.length,off+3),hl={id:'v133_'+i,target_id:pid,target_type:getHighlightTargetType(pid),start_offset:st,end_offset:en,start:st,end:en,color:'yellow',text:t.slice(st,en),selected_text_snapshot:t.slice(st,en),text_hash:stableTextHash(t),paragraph_fingerprint:stableTextHash(t),para_hash:stableTextHash(t.slice(st,en)),schema_version:STORAGE_SCHEMA_VERSION,created_at:'2026-09-04T00:00:00Z',updated_at:'2026-09-04T00:00:00Z'};state.textHighlights={[pid]:[hl]};state.notes={[pid]:[{id:'n'+i,text:'qa',ts:1}]};const snap=buildPersonalSnapshotFromState(),clean=sanitizePersonalSnapshot(snap);state.textHighlights={};state.notes={};applyPersonalSnapshot(clean);const rh=state.textHighlights[pid]?.[0],rn=state.notes[pid]?.[0];return{start:rh?.start_offset,end:rh?.end_offset,text:rh?.selected_text_snapshot,expected:t.slice(st,en),note:rn?.text,st,en}}''',{'pid':r['record_id'],'off':int(r['source_offset']),'i':i})
   add('highlight_note_roundtrip_'+str(i),x['start']==x['st'] and x['end']==x['en'] and x['text']==x['expected'] and x['note']=='qa',x)
  await b.close()
 sm={'pass':sum(x['status']=='PASS' for x in rs),'fail':sum(x['status']=='FAIL' for x in rs),'total':len(rs)};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps({'schema':'L24H_V101134_SOURCE_SELECTION_STATE_V2','summary':sm,'rows':rs},ensure_ascii=False,indent=2)+'\n');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
asyncio.run(main())
