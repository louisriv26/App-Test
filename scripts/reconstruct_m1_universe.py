from pathlib import Path
import json,re,csv,hashlib
ROOT=Path('/mnt/data/v101129_exec_strict')
HTML=(ROOT/'PRISTINE_V101128/index.html').read_text(encoding='utf-8')
EV=ROOT/'EVIDENCE_V101129'; EV.mkdir(exist_ok=True)

def ex(name):
    m=f'const {name} = '; i=HTML.index(m)+len(m); return json.JSONDecoder().raw_decode(HTML[i:])[0]
CORPUS=ex('CORPUS'); TEXT_LIBRARY=ex('TEXT_LIBRARY'); SD=ex('SPEECH_DATA'); SEB=ex('SPEECH_END_VISUAL_BREAKS'); SPP=ex('SPEECH_PRESENTATION_PROJECTION'); VPT=ex('VISIBLE_PARAGRAPH_TOPOLOGY')
LB=VPT['local_breaks']

def sha(s): return hashlib.sha256(s.encode()).hexdigest()
# Build target map equivalent for all likely target IDs.
text_map={}; meta={}
def add(pid,text,typ,label=''):
    if pid and isinstance(text,str): text_map[pid]=text; meta[pid]={'type':typ,'label':label}
for h in CORPUS.get('hours',[]):
    for p in h.get('paragraphs',[]): add(p['id'],p['t'],'hour_meditation',f"{h['hour_number']}e Heure — {h['title']}")
    for p in h.get('reflections',[]): add(p['id'],p['t'],'hour_reflection',f"{h['hour_number']}e Heure — Réflexions")
    for sub in h.get('subsections',[]):
        for p in sub.get('paragraphs',[]): add(p['id'],p['t'],'hour_subsection',f"{h['hour_number']}e Heure — {sub.get('title') or h['title']}")
for pr in CORPUS.get('prayers',[]):
    for p in pr.get('paragraphs',[]): add(p['id'],p['t'],'prayer',f"Prière — {pr['title']}")
for sec in CORPUS.get('sections',[]):
    for p in sec.get('paragraphs',[]): add(p['id'],p['t'],'section',f"Complément — {sec['title']}")

def walk(items):
    for item in items:
        if not isinstance(item,dict):
            continue
        yield item
        if isinstance(item.get('items'),list):
            yield from walk(item['items'])
for item in walk(TEXT_LIBRARY):
    iid=item.get('id','')
    if iid.startswith('PASSION24.TEXT.'):
        if isinstance(item.get('title'),str): add(iid+'.TITLE',item['title'],'library_title',f"Titre — {item['title']}")
        body=item.get('body') or []
        nums=item.get('body_stable_numbers') or list(range(1,len(body)+1))
        for n,txt in zip(nums,body): add(f'{iid}.BODY.P{int(n):03d}',txt,'library_text',f"Texte — {item.get('title','')}")
        for j,txt in enumerate(item.get('practice_options') or [],1): add(f'{iid}.PRACTICE_OPTION.P{j:03d}',txt,'library_practice_option',f"Comment pratiquer — {item.get('title','')}")

missing=sorted(pid for pid in SPP if pid not in text_map)
if missing:
    print('WARNING missing texts',len(missing),missing[:30])
# Raw inventories
with (EV/'02_RAW_SPEECH_END_BREAK_UNIVERSE.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['paragraph_id','break_offset','active_in_projection','active_in_topology','text_sha256'])
    for pid,vals in sorted(SEB.items()):
        text=text_map.get(pid,'')
        for b in vals:w.writerow([pid,b,b in SPP.get(pid,{}).get('breaks',[]),b in LB.get(pid,[]),sha(text)])
with (EV/'03_ACTIVE_PROJECTION_BREAK_UNIVERSE.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['paragraph_id','break_offset','in_speech_end_map','in_topology','text_sha256','context'])
    for pid,p in sorted(SPP.items()):
        text=text_map.get(pid,'')
        for b in p.get('breaks',[]):w.writerow([pid,b,b in SEB.get(pid,[]),b in LB.get(pid,[]),sha(text),text[max(0,b-45):min(len(text),b+65)].replace('\n',' ')])
with (EV/'04_VISIBLE_TOPOLOGY_LOCAL_BREAK_UNIVERSE.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['paragraph_id','break_offset','in_projection','in_speech_end_map','text_sha256','context'])
    for pid,vals in sorted(LB.items()):
        text=text_map.get(pid,'')
        for b in vals:w.writerow([pid,b,b in SPP.get(pid,{}).get('breaks',[]),b in SEB.get(pid,[]),sha(text),text[max(0,b-45):min(len(text),b+65)].replace('\n',' ')])
# Direct speech exits: projection runs ending before record end, advancing over any hidden wrapper that starts at/around run end, then whitespace.
rows=[]
for pid,p in sorted(SPP.items()):
    text=text_map.get(pid)
    if text is None: continue
    hidden=[(int(h['start']),int(h['end']),h.get('role','')) for h in p.get('hidden',[])]
    for ri,r in enumerate(p.get('runs',[])):
        rs,re_=int(r['start']),int(r['end']); sp=r['speaker']
        if re_>=len(text): continue
        # Closing wrapper may be governed as hidden metadata or remain visible in canonical text.
        # Consume only quote-wrapper material immediately after the semantic run, not ordinary inter-sentence spaces.
        wrapper_start=wrapper_end=re_
        changed=True
        while changed:
            changed=False
            for hs,he,role in hidden:
                if hs <= wrapper_end <= he and he>wrapper_end and hs>=re_-2:
                    if wrapper_start==re_: wrapper_start=hs
                    wrapper_end=he; changed=True
                elif hs==wrapper_end:
                    if wrapper_start==re_: wrapper_start=hs
                    wrapper_end=he; changed=True
        for hs,he,role in hidden:
            if hs>=re_ and hs<=re_+2 and he>wrapper_end:
                wrapper_start=min(wrapper_start,hs);wrapper_end=he
        # If no/partial hidden wrapper exists, recover canonical closing wrapper: narrow/non-breaking
        # spaces used inside French guillemets followed by one or more quote-closers.
        j=wrapper_end
        while j < len(text) and text[j] in ('\u202f','\u00a0'):
            j += 1
        closers='»”’\"'
        saw=False
        while j < len(text) and text[j] in closers:
            saw=True; j += 1
            while j < len(text) and text[j] in ('\u202f','\u00a0'):
                j += 1
        if saw:
            if wrapper_start==re_: wrapper_start=re_
            wrapper_end=max(wrapper_end,j)
        resume=wrapper_end
        while resume<len(text) and text[resume].isspace(): resume+=1
        if resume>=len(text): continue
        current_breaks=p.get('breaks',[])
        # map break at any position between run end and resume (or exactly resume if break insertion offset after wrapper before lexical)
        nearby=[b for b in current_breaks if re_<=b<=resume]
        rows.append({
            'row_id':f'{pid}#R{ri:02d}', 'paragraph_id':pid,'speaker':sp,'run_index':ri,'run_start':rs,'run_end':re_,
            'wrapper_start':wrapper_start,'wrapper_end':wrapper_end,'resume_lexical_offset':resume,
            'next_char':text[resume:resume+1], 'next_token':re.match(r"[^\s,;:!?\.\)\]\}»]+",text[resume:]).group(0) if re.match(r"[^\s,;:!?\.\)\]\}»]+",text[resume:]) else '',
            'active_breaks_near_exit':'|'.join(map(str,nearby)), 'all_projection_breaks':'|'.join(map(str,current_breaks)),
            'all_topology_breaks':'|'.join(map(str,LB.get(pid,[]))), 'speech_end_map':'|'.join(map(str,SEB.get(pid,[]))),
            'text_sha256':sha(text),'label':meta.get(pid,{}).get('label',''),
            'context_before':text[max(0,rs-80):rs], 'quoted':text[rs:re_], 'context_after':text[wrapper_end:min(len(text),wrapper_end+180)],
            'full_text':text,
        })
# active break rows not near any run exit
mapped={(r['paragraph_id'],int(b)) for r in rows for b in r['active_breaks_near_exit'].split('|') if b}
orph=[]
for pid,p in SPP.items():
    for b in p.get('breaks',[]):
        if (pid,int(b)) not in mapped:
            text=text_map.get(pid,'')
            orph.append({'row_id':f'{pid}#B{b}','paragraph_id':pid,'speaker':'','run_index':'','run_start':'','run_end':'','wrapper_start':'','wrapper_end':'','resume_lexical_offset':b,'next_char':text[b:b+1], 'next_token':'','active_breaks_near_exit':str(b),'all_projection_breaks':'|'.join(map(str,p.get('breaks',[]))),'all_topology_breaks':'|'.join(map(str,LB.get(pid,[]))),'speech_end_map':'|'.join(map(str,SEB.get(pid,[]))),'text_sha256':sha(text),'label':meta.get(pid,{}).get('label',''),'context_before':text[max(0,b-100):b],'quoted':'','context_after':text[b:min(len(text),b+180)],'full_text':text,'orphan_break':True})
combined=rows+orph
# alias key based full text + semantic relative key run or break location. This can merge exact mirrors.
for r in combined:
    key='|'.join([r['text_sha256'],str(r.get('speaker','')),str(r.get('run_start','')),str(r.get('run_end','')),str(r.get('resume_lexical_offset','')),str(r.get('active_breaks_near_exit',''))])
    r['alias_key']=hashlib.sha256(key.encode()).hexdigest()[:16]
from collections import defaultdict
groups=defaultdict(list)
for r in combined: groups[r['alias_key']].append(r['row_id'])
for r in combined:r['alias_group']='|'.join(groups[r['alias_key']])
fields=sorted(set().union(*(r.keys() for r in combined)))
with (EV/'05_DIRECT_SPEECH_EXIT_UNIVERSE.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(combined)
with (EV/'06_QUOTE_HOST_SENTENCE_ALIAS_GRAPH.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['alias_key','members','member_count'])
    for k,v in sorted(groups.items()):w.writerow([k,'|'.join(v),len(v)])
summary={
 'raw_speech_end_positions':sum(len(v) for v in SEB.values()),'raw_speech_end_ids':len(SEB),
 'active_projection_positions':sum(len(p.get('breaks',[])) for p in SPP.values()),'active_projection_ids':sum(bool(p.get('breaks')) for p in SPP.values()),
 'topology_local_break_positions':sum(len(v) for v in LB.values()),'topology_local_break_ids':len(LB),
 'run_exit_rows':len(rows),'orphan_active_break_rows':len(orph),'combined_review_rows':len(combined),'semantic_alias_groups':len(groups),
 'missing_projection_text_ids':len(missing)
}
(EV/'M1_UNIVERSE_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
if orph:
 print('orphans:')
 for r in orph: print(r['row_id'],repr(r['context_before'][-80:]),'|',repr(r['context_after'][:100]))
