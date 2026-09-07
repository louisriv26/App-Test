#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');OUT=Path(sys.argv[2]);OUT.parent.mkdir(parents=True,exist_ok=True)
async def main():
 rows=[]
 def add(n,ok,d=None):rows.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  p=await b.new_page(viewport={'width':1800,'height':1000});errs=[];p.on('pageerror',lambda e:errs.append(str(e)))
  await p.set_content(HTML,wait_until='domcontentloaded');await p.wait_for_timeout(100)
  ident=await p.evaluate("()=>({v:APP_VERSION,s:APP_EVIDENCE_STAGE})");add('identity',ident=={'v':'v101.133','s':'VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_R1'},ident)
  helper='''({pid,offset})=>{const t=getFullParaText(pid),d=document.createElement('div');d.innerHTML=renderParaText(t,pid);document.body.appendChild(d);let w=document.createTreeWalker(d,NodeFilter.SHOW_TEXT),n,b=0,res=null;while(n=w.nextNode()){let e=n.nodeValue.length;if(offset>=b&&offset<b+e){let el=n.parentElement;res={ch:t[offset],jesus:!!el.closest('.sp-jesus'),father:!!el.closest('.sp-father'),mary:!!el.closest('.sp-mary'),hidden:!!el.closest('.speech-quote-hidden'),className:el.className};break}b+=e}const txt=d.textContent,breaks=d.querySelectorAll('.speech-presentation-visual-break').length;d.remove();return{res,textConserved:txt===t,breaks,raw:t}}'''
  async def at(pid,off):return await p.evaluate(helper,{'pid':pid,'offset':off})
  p57='PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P057';x=await at(p57,78);q=await at(p57,77);z=await at(p57,113);br=await p.evaluate('(pid)=>getPresentationLocalBreaks(pid)',p57)
  add('M1C001_nested_text_JESUS',x['res']['jesus'] and not x['res']['hidden'],x);add('M1C001_open_quote_visible_JESUS',q['res']['jesus'] and not q['res']['hidden'],q);add('M1C001_close_quote_visible_JESUS',z['res']['jesus'] and not z['res']['hidden'],z);add('M1C001_no_break',br==[],br);add('M1C001_text_conserved',x['textConserved'],len(x['raw']))
  p100='PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P100';a=await at(p100,40);o=await at(p100,39);c=await at(p100,98);br=await p.evaluate('(pid)=>getPresentationLocalBreaks(pid)',p100)
  add('M1C002_nested_direct_JESUS',a['res']['jesus'] and not a['res']['hidden'],a);add('M1C002_quotes_visible_and_JESUS',o['res']['jesus'] and c['res']['jesus'] and not o['res']['hidden'] and not c['res']['hidden'],{'open':o,'close':c});add('M1C002_no_break',br==[],br);add('M1C002_text_conserved',a['textConserved'],len(a['raw']))
  p67='PASSION24.TEXT.RELATED_HOUR_21.BODY.P067';p68='PASSION24.TEXT.RELATED_HOUR_21.BODY.P068';p73='PASSION24.TEXT.RELATED_HOUR_21.BODY.P073'
  o=await at(p67,47);f=await at(p68,0);last=await at(p73,258);cl=await at(p73,259);nar=await at(p73,261);br=await p.evaluate('(pid)=>getPresentationLocalBreaks(pid)',p73);join=await p.evaluate("()=>hasQuoteEdgeIntegrityJoin('PASSION24.TEXT.RELATED_HOUR_21.BODY.P067','PASSION24.TEXT.RELATED_HOUR_21.BODY.P068')")
  add('M1C003_open_wrapper_hidden',o['res']['hidden'],o);add('M1C003_FATHER_starts_P068',f['res']['father'] and not f['res']['hidden'],f);add('M1C003_FATHER_through_P073_258',last['res']['father'] and not last['res']['hidden'],last);add('M1C003_close_wrapper_hidden',cl['res']['hidden'],cl);add('M1C003_narration_resumes_not_FATHER',not nar['res']['father'] and not nar['res']['hidden'],nar);add('M1C003_break_260_exact',br==[260],br);add('M1C003_P067_P068_join_preserved',join,join);add('M1C003_text_conserved',all(x['textConserved'] for x in [o,f,last,cl,nar]))
  # geometry around @260 must visibly separate speech and narration
  geo=await p.evaluate('''()=>{const pid='PASSION24.TEXT.RELATED_HOUR_21.BODY.P073',t=getFullParaText(pid),d=document.createElement('div');d.style.width='800px';d.innerHTML=renderParaText(t,pid);document.body.appendChild(d);function rect(off){let w=document.createTreeWalker(d,NodeFilter.SHOW_TEXT),n,b=0;while(n=w.nextNode()){if(off>=b&&off<b+n.nodeValue.length){const r=document.createRange();r.setStart(n,off-b);r.setEnd(n,Math.min(off-b+1,n.nodeValue.length));let q=r.getBoundingClientRect();return{x:q.x,y:q.y}}b+=n.nodeValue.length}return null}let A=rect(258),B=rect(261);const out={A,B,dy:A&&B?B.y-A.y:null};d.remove();return out}''');add('M1C003_break_260_visible_geometry',bool(geo['A'] and geo['B'] and geo['dy']>5),geo)
  rp='PASSION24.TEXT.RELATED_HOUR_21.BODY.P100';j=await at(rp,27);oq=await at(rp,26);cq=await at(rp,55);outside=await at(rp,20);br=await p.evaluate('(pid)=>getPresentationLocalBreaks(pid)',rp)
  add('M1C004_nested_JESUS_27_55',j['res']['jesus'] and not j['res']['hidden'],j);add('M1C004_quote_delimiters_visible_default',not oq['res']['jesus'] and not cq['res']['jesus'] and not oq['res']['hidden'] and not cq['res']['hidden'],{'open':oq,'close':cq});add('M1C004_outer_Luisa_default',not outside['res']['jesus'] and not outside['res']['father'] and not outside['res']['mary'],outside);add('M1C004_no_break',br==[],br);add('M1C004_text_conserved',j['textConserved'],len(j['raw']))
  # User-state offset preservation on all four loci with representative ranges.
  tests=[(p57,70,90),(p100,30,60),(p73,250,280),(rp,20,56)]
  for i,(pid,st,en) in enumerate(tests,1):
   d=await p.evaluate('''({pid,st,en,i})=>{const t=getFullParaText(pid),hl={id:'m1_'+i,target_id:pid,target_type:getHighlightTargetType(pid),start_offset:st,end_offset:en,start:st,end:en,color:'yellow',text:t.slice(st,en),selected_text_snapshot:t.slice(st,en),text_hash:stableTextHash(t),paragraph_fingerprint:stableTextHash(t),para_hash:stableTextHash(t.slice(st,en)),schema_version:STORAGE_SCHEMA_VERSION,created_at:'2026-09-03T00:00:00Z',updated_at:'2026-09-03T00:00:00Z'};state.textHighlights={[pid]:[hl]};state.notes={[pid]:[{id:'n'+i,text:'qa',ts:1}]};const status=currentHighlightStatus(pid,hl);const snap=buildPersonalSnapshotFromState(),clean=sanitizePersonalSnapshot(snap);state.textHighlights={};state.notes={};applyPersonalSnapshot(clean);const rh=state.textHighlights[pid][0],rn=state.notes[pid][0];return{fresh:status.fresh,start:rh.start_offset,end:rh.end_offset,text:rh.selected_text_snapshot,expected:t.slice(st,en),note:rn.text,hash:rh.text_hash,currentHash:stableTextHash(t)}}''',{'pid':pid,'st':st,'en':en,'i':i})
   add(f'user_state_anchor_{i}',d['fresh'] and d['start']==st and d['end']==en and d['text']==d['expected'] and d['hash']==d['currentHash'] and d['note']=='qa',d)
  add('browser_page_errors_zero',not errs,errs);await b.close()
 sm={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)};OUT.write_text(json.dumps({'schema':'L24H_V101133_RUNTIME_PRESENTATION_MATRIX_V1','version':'v101.133','summary':sm,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));
 if sm['fail']:
  print([r for r in rows if r['status']=='FAIL']);raise SystemExit(2)
asyncio.run(main())
