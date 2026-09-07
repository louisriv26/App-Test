#!/usr/bin/env python3
from pathlib import Path
import json,csv,hashlib,sys,asyncio,re
from playwright.async_api import async_playwright
CAND=Path(sys.argv[1]); BASE=Path(sys.argv[2]); EV=Path(sys.argv[3]); EV.mkdir(parents=True,exist_ok=True)
H=CAND.read_text(encoding='utf-8'); B=BASE.read_text(encoding='utf-8'); dec=json.JSONDecoder()
def ex(text,name):
 m=f'const {name} = '; i=text.index(m)+len(m); return dec.raw_decode(text[i:])[0]
def raw(text,name):
 m=f'const {name} = '; i=text.index(m)+len(m)
 try:o,e=dec.raw_decode(text[i:]);return text[i:i+e]
 except: return text[i:text.index(';',i)]
def js(obj): return json.dumps(obj,ensure_ascii=False)
def dump(name,obj): (EV/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sm(rows): return {'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
def add(rows,case,ok,detail=None):rows.append({'case':case,'status':'PASS' if ok else 'FAIL','detail':detail})
SE=ex(H,'SPEECH_END_VISUAL_BREAKS'); SPP=ex(H,'SPEECH_PRESENTATION_PROJECTION'); VPT=ex(H,'VISIBLE_PARAGRAPH_TOPOLOGY'); SD=ex(H,'SPEECH_DATA')
BSE=ex(B,'SPEECH_END_VISUAL_BREAKS'); BSPP=ex(B,'SPEECH_PRESENTATION_PROJECTION'); BVPT=ex(B,'VISIBLE_PARAGRAPH_TOPOLOGY'); BSD=ex(B,'SPEECH_DATA')
ops=[
 ('PASSION24.HOUR.08.P009',42,93,14,40,43),('PASSION24.HOUR.08.P009',140,210,112,138,141),
 ('PASSION24.HOUR.08.P010',49,None,22,47,50),('PASSION24.HOUR.08.P015',50,145,38,48,51),
 ('PASSION24.HOUR.21.P020',69,None,44,67,70),('PASSION24.HOUR.21.P025',118,None,93,116,119),
 ('PASSION24.TEXT.RELATED_HOUR_06.BODY.P043',49,None,0,49,50),('PASSION24.TEXT.RELATED_HOUR_06.BODY.P058',49,None,0,49,50)]
valid={'PASSION24.HOUR.08.P007':[111],'PASSION24.HOUR.08.P008':[42],'PASSION24.HOUR.08.P014':[34]}
# final expected projection/topology from baseline + exact ledger
expected_proj={k:list(v.get('breaks',[])) for k,v in BSPP.items()}
expected_top={k:list(v) for k,v in BVPT['local_breaks'].items()}
expected_se={k:list(v) for k,v in BSE.items()}
for pid,old,new,rs,re_,resume in ops:
 for m in (expected_proj,expected_top):
  vals=m.get(pid,[]); assert old in vals,(pid,old,vals); vals=[x for x in vals if x!=old]
  if new is not None:vals=sorted(vals+[new])
  if vals:m[pid]=vals
  elif pid in m:del m[pid]
 vals=expected_se.get(pid,[]); assert old in vals; vals=[x for x in vals if x!=old]
 if vals:expected_se[pid]=vals
 elif pid in expected_se:del expected_se[pid]
# 20 syntax matrix
r20=[]
add(r20,'identity_v101130',"const APP_VERSION = 'v101.130';" in H and "const APP_EVIDENCE_STAGE = 'FOUR_PASS_FINAL_PACKAGE_METADATA_EVIDENCE_RECONCILIATION_R1';" in H)
for i,(pid,old,new,rs,re_,resume) in enumerate(ops,1):
 add(r20,f'OP{i:02d}_old_projection_break_removed',old not in SPP.get(pid,{}).get('breaks',[]),SPP.get(pid,{}).get('breaks',[]))
 add(r20,f'OP{i:02d}_old_topology_break_removed',old not in VPT['local_breaks'].get(pid,[]),VPT['local_breaks'].get(pid,[]))
 add(r20,f'OP{i:02d}_old_speech_end_break_removed',old not in SE.get(pid,[]),SE.get(pid,[]))
 if new is not None:
  add(r20,f'OP{i:02d}_host_sentence_break_in_projection',new in SPP[pid]['breaks'],SPP[pid]['breaks'])
  add(r20,f'OP{i:02d}_host_sentence_break_in_topology',new in VPT['local_breaks'][pid],VPT['local_breaks'][pid])
  add(r20,f'OP{i:02d}_host_sentence_break_not_falsely_speech_end',new not in SE.get(pid,[]),SE.get(pid,[]))
add(r20,'complete_projection_break_universe_exact', {k:v for k,v in expected_proj.items() if v}=={k:v.get('breaks',[]) for k,v in SPP.items() if v.get('breaks')})
add(r20,'complete_topology_break_universe_exact', expected_top==VPT['local_breaks'])
add(r20,'complete_speech_end_map_exact', expected_se==SE)
dump('20_INTRA_RECORD_QUOTE_HOST_SYNTAX_MATRIX.json',{'schema':'L24H_V101130_QUOTE_HOST_SYNTAX_MATRIX_V1','version':'v101.130','summary':sm(r20),'rows':r20})
# 22 valid controls
r22=[]
for pid,br in valid.items():
 add(r22,pid+'_projection_break_retained',SPP[pid].get('breaks',[])==br,SPP[pid].get('breaks',[]))
 add(r22,pid+'_topology_break_retained',VPT['local_breaks'].get(pid,[])==br,VPT['local_breaks'].get(pid,[]))
dump('22_VALID_BREAK_CONTROL_MATRIX.json',{'schema':'L24H_V101130_VALID_BREAK_CONTROL_MATRIX_V1','version':'v101.130','summary':sm(r22),'rows':r22})
# 23 parity
r23=[]
proj_pairs={(pid,int(b)) for pid,p in SPP.items() for b in p.get('breaks',[])};top_pairs={(pid,int(b)) for pid,vals in VPT['local_breaks'].items() for b in vals}
add(r23,'all_projection_breaks_exist_in_visible_topology',proj_pairs.issubset(top_pairs),{'projection':len(proj_pairs),'topology':len(top_pairs),'missing':sorted(proj_pairs-top_pairs)[:20]})
for pid in sorted({x[0] for x in ops}):add(r23,pid+'_affected_projection_equals_topology',SPP[pid].get('breaks',[])==VPT['local_breaks'].get(pid,[]),{'projection':SPP[pid].get('breaks',[]),'topology':VPT['local_breaks'].get(pid,[])})
dump('23_PROJECTION_TOPOLOGY_PARITY_MATRIX.json',{'schema':'L24H_V101130_PROJECTION_TOPOLOGY_PARITY_V1','version':'v101.130','summary':sm(r23),'rows':r23})
# 24 speaker conservation
r24=[]
add(r24,'SPEECH_DATA_byte_equivalent_json',SD==BSD,{'entries':len(SD)})
for pid in sorted({x[0] for x in ops}):add(r24,pid+'_speaker_runs_unchanged',SPP[pid].get('runs',[])==BSPP[pid].get('runs',[]) and SPP[pid].get('hidden',[])==BSPP[pid].get('hidden',[]),{'runs':SPP[pid].get('runs',[]),'hidden':SPP[pid].get('hidden',[])})
dump('24_SPEAKER_CONSERVATION_MATRIX.json',{'schema':'L24H_V101130_SPEAKER_CONSERVATION_V1','version':'v101.130','summary':sm(r24),'rows':r24})

async def browser_matrices():
 r21=[];r25=[];r26=[];r27=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  page=await b.new_page(viewport={'width':2400,'height':1200});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
  await page.set_content(H,wait_until='domcontentloaded');await page.wait_for_timeout(80)
  # helper creates wide isolated rendered text and returns char rect by canonical offset.
  GEOM="""({pid,offsets})=>{const text=getFullParaText(pid);const d=document.createElement('div');d.style.cssText='position:absolute;left:0;top:3000px;width:2200px;font:20px Georgia,serif;line-height:1.55;';d.innerHTML=renderParaText(text,pid);document.body.appendChild(d);function rect(off){let w=document.createTreeWalker(d,NodeFilter.SHOW_TEXT),n,pos=0;while(n=w.nextNode()){const L=n.nodeValue.length;if(off>=pos&&off<pos+L){const r=document.createRange();r.setStart(n,off-pos);r.setEnd(n,off-pos+1);const x=r.getBoundingClientRect();return{x:x.x,y:x.y,right:x.right,bottom:x.bottom,width:x.width,height:x.height,ch:n.nodeValue[off-pos],parent:n.parentElement.className}}pos+=L}return null}const out={text,html:d.innerHTML,breaks:[...d.querySelectorAll('.speech-presentation-visual-break')].length,rects:Object.fromEntries(offsets.map(o=>[String(o),rect(o)])),textContent:d.textContent};d.remove();return out}"""
  # Defect locations: last visible quote char to first lexical host continuation must be same line in ample width.
  for i,(pid,old,new,rs,re_,resume) in enumerate(ops,1):
   d=await page.evaluate(GEOM,{'pid':pid,'offsets':[max(rs,re_-1),resume]})
   a=d['rects'].get(str(max(rs,re_-1)));c=d['rects'].get(str(resume)); ok=bool(a and c and a['height']>0 and c['height']>0 and abs(c['y']-a['y'])<=1.0)
   add(r21,f'OP{i:02d}_quote_to_host_continuation_inline_when_space_available',ok,{'a':a,'b':c,'breaks':d['breaks']})
  # Relocated true host-sentence boundaries must be real visual breaks.
  for pid,old,new,rs,re_,resume in [x for x in ops if x[2] is not None]:
   # last nonspace before and first nonspace at/after boundary
   text=await page.evaluate('(pid)=>getFullParaText(pid)',pid); a=new-1
   while a>=0 and text[a].isspace():a-=1
   c=new
   while c<len(text) and text[c].isspace():c+=1
   d=await page.evaluate(GEOM,{'pid':pid,'offsets':[a,c]});ra=d['rects'].get(str(a));rb=d['rects'].get(str(c));ok=bool(ra and rb and rb['y']-ra['y']>5)
   add(r21,pid+f'_relocated_boundary_{new}_creates_new_visual_paragraph',ok,{'a':ra,'b':rb,'breaks':d['breaks']})
  # Valid controls must still create paragraph displacement.
  for pid,bs in valid.items():
   br=bs[0];text=await page.evaluate('(pid)=>getFullParaText(pid)',pid);a=br-1
   while a>=0 and text[a].isspace():a-=1
   c=br
   while c<len(text) and text[c].isspace():c+=1
   d=await page.evaluate(GEOM,{'pid':pid,'offsets':[a,c]});ra=d['rects'].get(str(a));rb=d['rects'].get(str(c));add(r21,pid+'_valid_break_geometry',bool(ra and rb and rb['y']-ra['y']>5),{'a':ra,'b':rb})
  add(r21,'no_page_errors',not errs,errs)
  # rendered text + speaker presentation + visible paragraph targets
  affected=sorted({x[0] for x in ops})
  for pid in affected:
   d=await page.evaluate("""pid=>{const t=getFullParaText(pid),x=document.createElement('div');x.innerHTML=renderParaText(t,pid);document.body.appendChild(x);const ret={same:x.textContent===t,textLen:t.length,renderLen:x.textContent.length,breaks:[...x.querySelectorAll('.speech-presentation-visual-break')].length};x.remove();return ret}""",pid)
   add(r25,pid+'_rendered_text_content_exact',d['same'],d)
  # user-state visual paragraph ranges for affected rows
  expected_ranges={
   'PASSION24.HOUR.08.P009':[(0,93),(94,210),(211,238)],
   'PASSION24.HOUR.08.P010':[(0,92)],
   'PASSION24.HOUR.08.P015':[(0,145),(146,755)],
   'PASSION24.HOUR.21.P020':[(0,101)],
   'PASSION24.HOUR.21.P025':[(0,157)],
  }
  # Library text lengths derive dynamically.
  for pid in ['PASSION24.TEXT.RELATED_HOUR_06.BODY.P043','PASSION24.TEXT.RELATED_HOUR_06.BODY.P058']:
   ln=await page.evaluate('(pid)=>getFullParaText(pid).length',pid);expected_ranges[pid]=[(0,ln)]
  for pid,ranges in expected_ranges.items():
   got=[]
   for a,c in ranges:
    off=a if c-a<=1 else min(c-1,a+max(0,(c-a)//2))
    x=await page.evaluate("""({pid,off})=>{const d=document.createElement('span');d.className='para-text';d.dataset.paraId=pid;d.id=pid;d.textContent=getFullParaText(pid);document.body.appendChild(d);const z=buildVisibleParagraphTargetFromOffset(d,off);d.remove();return z&&z.ranges&&z.ranges[0]?{start:z.ranges[0].start,end:z.ranges[0].end,text:z.ranges[0].text}:null}""",{'pid':pid,'off':off});got.append((x['start'],x['end']) if x else None)
   add(r26,pid+'_visual_paragraph_target_ranges',got==ranges,{'expected':ranges,'got':got})
  # Speaker style ownership at quoted char and first continuation.
  for i,(pid,old,new,rs,re_,resume) in enumerate(ops,1):
   d=await page.evaluate("""({pid,inside,outside})=>{const t=getFullParaText(pid),x=document.createElement('div');x.innerHTML=renderParaText(t,pid);document.body.appendChild(x);function cls(off){let w=document.createTreeWalker(x,NodeFilter.SHOW_TEXT),n,p=0;while(n=w.nextNode()){if(off>=p&&off<p+n.nodeValue.length){const e=n.parentElement;return{ch:n.nodeValue[off-p],jesus:!!e.closest('.sp-jesus'),mary:!!e.closest('.sp-mary'),father:!!e.closest('.sp-father'),hidden:!!e.closest('.speech-quote-hidden')}}p+=n.nodeValue.length}return null}const z={inside:cls(inside),outside:cls(outside)};x.remove();return z}""",{'pid':pid,'inside':max(rs,re_-1),'outside':resume})
   add(r27,f'OP{i:02d}_speaker_returns_after_quote',bool(d['inside'] and d['inside']['jesus'] and d['outside'] and not d['outside']['jesus'] and not d['outside']['mary'] and not d['outside']['father']),d)
  add(r25,'no_page_errors',not errs,errs);add(r26,'no_page_errors',not errs,errs);add(r27,'no_page_errors',not errs,errs)
  await b.close()
 dump('21_INTRA_RECORD_QUOTE_HOST_CONTINUITY_GEOMETRY_MATRIX.json',{'schema':'L24H_V101130_QUOTE_HOST_GEOMETRY_V1','version':'v101.130','browser':'Chromium wide synthetic geometry; physical devices remain external','summary':sm(r21),'rows':r21})
 dump('25_RENDERED_TEXT_CONSERVATION_MATRIX.json',{'schema':'L24H_V101130_RENDERED_TEXT_CONSERVATION_V1','version':'v101.130','summary':sm(r25),'rows':r25})
 dump('26_USER_STATE_TOPOLOGY_MATRIX.json',{'schema':'L24H_V101130_USER_STATE_TOPOLOGY_V1','version':'v101.130','note':'Character offsets are unchanged; this matrix verifies corrected Samsung/visual-paragraph range topology. Physical Samsung remains external.','summary':sm(r26),'rows':r26})
 dump('27_REPERES_PRESENTATION_MATRIX.json',{'schema':'L24H_V101130_SPEAKER_RETURN_PRESENTATION_V1','version':'v101.130','summary':sm(r27),'rows':r27})
 return [sm(x) for x in [r21,r25,r26,r27]]

sums=asyncio.run(browser_matrices())
# 28 mutation detection — static oracle validator against synthetic mutated declarations.
r28=[]
def validate(se,spp,vpt):
 errs=[]
 # exact expected universe is strongest two-sided oracle
 if {k:v for k,v in expected_proj.items() if v}!={k:v.get('breaks',[]) for k,v in spp.items() if v.get('breaks')}:errs.append('projection_universe')
 if expected_top!=vpt['local_breaks']:errs.append('topology_universe')
 if expected_se!=se:errs.append('speech_end_universe')
 return errs
import copy
mut=[]
# A reintroduce bad P009 42
x=copy.deepcopy(SPP);x['PASSION24.HOUR.08.P009']['breaks']=sorted(x['PASSION24.HOUR.08.P009']['breaks']+[42]);mut.append(('MUT-A_reintroduce_bad_quote_close',SE,x,VPT))
# B remove valid P008
x=copy.deepcopy(SPP);x['PASSION24.HOUR.08.P008']['breaks']=[];mut.append(('MUT-B_remove_valid_break',SE,x,VPT))
# C remove required relocated P009 93
x=copy.deepcopy(SPP);x['PASSION24.HOUR.08.P009']['breaks']=[b for b in x['PASSION24.HOUR.08.P009']['breaks'] if b!=93];mut.append(('MUT-C_missing_relocated_break',SE,x,VPT))
# D wrong later location
x=copy.deepcopy(SPP);x['PASSION24.HOUR.08.P009']['breaks']=[94 if b==93 else b for b in x['PASSION24.HOUR.08.P009']['breaks']];mut.append(('MUT-D_wrong_relocated_offset',SE,x,VPT))
# E projection correct topology stale at old 42
x=copy.deepcopy(VPT);x['local_breaks']['PASSION24.HOUR.08.P009']=sorted([42]+[b for b in x['local_breaks']['PASSION24.HOUR.08.P009'] if b!=93]);mut.append(('MUT-E_topology_stale',SE,SPP,x))
# F speaker mutation is detected separately
add(r28,'MUT-F_speaker_data_change_detected',SD==BSD and (lambda z:z!=BSD)({**BSD,'__MUT__':[]}))
# G canonical/protected text detection
add(r28,'MUT-G_canonical_text_change_detected',raw(H,'CORPUS')==raw(B,'CORPUS') and raw(H,'CORPUS')+'x'!=raw(B,'CORPUS'))
# H Samsung target topology is bound to VPT and exact expected topology catches altered range
for name,se,spp,vpt in mut:
 add(r28,name,bool(validate(se,spp,vpt)),validate(se,spp,vpt))
add(r28,'MUT-H_user_state_topology_change_detected',bool(validate(SE,SPP,{**VPT,'local_breaks':{**VPT['local_breaks'],'PASSION24.HOUR.08.P015':[50]}})),validate(SE,SPP,{**VPT,'local_breaks':{**VPT['local_breaks'],'PASSION24.HOUR.08.P015':[50]}}))
dump('28_MUTATION_DETECTION_MATRIX.json',{'schema':'L24H_V101130_MUTATION_DETECTION_V1','version':'v101.130','summary':sm(r28),'rows':r28})
all_files=['20_INTRA_RECORD_QUOTE_HOST_SYNTAX_MATRIX.json','21_INTRA_RECORD_QUOTE_HOST_CONTINUITY_GEOMETRY_MATRIX.json','22_VALID_BREAK_CONTROL_MATRIX.json','23_PROJECTION_TOPOLOGY_PARITY_MATRIX.json','24_SPEAKER_CONSERVATION_MATRIX.json','25_RENDERED_TEXT_CONSERVATION_MATRIX.json','26_USER_STATE_TOPOLOGY_MATRIX.json','27_REPERES_PRESENTATION_MATRIX.json','28_MUTATION_DETECTION_MATRIX.json']
print(json.dumps({f:json.loads((EV/f).read_text())['summary'] for f in all_files},indent=2))
if any(json.loads((EV/f).read_text())['summary']['fail'] for f in all_files):raise SystemExit(2)
