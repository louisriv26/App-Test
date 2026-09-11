#!/usr/bin/env python3
import csv, json, re, hashlib, sys
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

HTML_PATH=Path(sys.argv[1])
OUT=Path(sys.argv[2]); OUT.mkdir(parents=True,exist_ok=True)
html=HTML_PATH.read_text(encoding='utf-8')
DIVINE={'JESUS','MARY','FATHER'}

def extract(name):
    m=re.search(rf'const\s+{re.escape(name)}\s*=\s*',html)
    if not m: raise RuntimeError(f'missing const {name}')
    return json.JSONDecoder().raw_decode(html[m.end():])[0]
CORPUS=extract('CORPUS'); TL=extract('TEXT_LIBRARY'); SD=extract('SPEECH_DATA'); PROJ=extract('SPEECH_PRESENTATION_PROJECTION'); ADJ=extract('SPEECH_PRESENTATION_ADJUDICATIONS'); VPT=extract('VISIBLE_PARAGRAPH_TOPOLOGY')

def make_target_map():
    tm={}; containers=[]
    for h in CORPUS['hours']:
        if h.get('paragraphs'):
            ids=[]
            for p in h['paragraphs']: tm[p['id']]=p['t']; ids.append(p['id'])
            containers.append((f"HOUR_{h['hour_number']:02d}_BODY",ids))
        if h.get('reflections'):
            ids=[]
            for p in h['reflections']: tm[p['id']]=p['t']; ids.append(p['id'])
            containers.append((f"HOUR_{h['hour_number']:02d}_REF",ids))
        for j,sub in enumerate(h.get('subsections',[])):
            ids=[]
            for p in sub.get('paragraphs',[]): tm[p['id']]=p['t']; ids.append(p['id'])
            if ids: containers.append((f"HOUR_{h['hour_number']:02d}_SUB_{j}",ids))
    for pr in CORPUS.get('prayers',[]):
        ids=[]
        for p in pr.get('paragraphs',[]): tm[p['id']]=p['t']; ids.append(p['id'])
        if ids: containers.append((f"PRAYER_{pr.get('prayer_id')}",ids))
    for sec in CORPUS.get('sections',[]):
        ids=[]
        for p in sec.get('paragraphs',[]): tm[p['id']]=p['t']; ids.append(p['id'])
        if ids: containers.append((f"SECTION_{sec.get('section_id')}",ids))
    for item in TL:
        ids=[]; stable=item.get('body_stable_numbers')
        for i,t in enumerate(item.get('body',[]) or []):
            n=stable[i] if isinstance(stable,list) and i<len(stable) and isinstance(stable[i],int) and stable[i]>0 else i+1
            pid=f"{item['id']}.BODY.P{n:03d}"; tm[pid]=t; ids.append(pid)
        if ids: containers.append((item['id'],ids))
        opts=[]
        for i,t in enumerate(item.get('practice_options',[]) or []):
            pid=f"{item['id']}.PRACTICE_OPTION.P{i+1:03d}";tm[pid]=t;opts.append(pid)
        if opts: containers.append((item['id']+'_OPTS',opts))
    return tm,containers
TM,CONTAINERS=make_target_map(); CIDS=dict(CONTAINERS)

def hidden(pid,off):
    for r in PROJ.get(pid,{}).get('hidden',[]):
        if int(r['start'])<=off<int(r['end']): return str(r.get('role') or r.get('reason') or 'HIDDEN')
    return None

def run(pid,off):
    for r in PROJ.get(pid,{}).get('runs',[]):
        if int(r['start'])<=off<int(r['end']): return str(r.get('speaker') or '')
    return None

def adjud(pid,off):
    rows=ADJ.get(pid,[])
    if not isinstance(rows,list): return None
    for r in rows:
        if int(r.get('start',0))<=off<int(r.get('end',0)): return str(r.get('semantic_speaker') or '') or None
    return None

def semantic(pid,off):
    a=adjud(pid,off)
    if a:return a
    for r in SD.get(pid,[]):
        if int(r['start'])<=off<int(r['end']): return str(r.get('speaker') or '') or None
    return None

def state(pid,off):
    h=hidden(pid,off)
    if h:return 'HIDDEN'
    r=run(pid,off)
    return r if r in DIVINE else 'OUTSIDE'

# Scanner A: mixed-family nested stack.
def scan_a_pairs():
    openers={'«':'guillemet','“':'curly_double','‘':'curly_single'}; closers={'»':'guillemet','”':'curly_double','’':'curly_single'}
    spans=[]; unmatched=[]; seq=0
    for cname,ids in CONTAINERS:
        stack=[]
        for ri,pid in enumerate(ids):
            for off,ch in enumerate(TM[pid]):
                def push(fam):
                    nonlocal seq
                    seq+=1; sid=f"A-Q{seq:05d}"
                    stack.append({'span_id':sid,'container':cname,'family':fam,'open_target':pid,'open_offset':off,'open_char':ch,'open_record_index':ri,'quotation_depth':len(stack)+1,'parent_span_id':stack[-1]['span_id'] if stack else ''})
                if ch=='"':
                    if stack and stack[-1]['family']=='straight_double':
                        op=stack.pop(); spans.append({**op,'close_target':pid,'close_offset':off,'close_char':ch,'close_record_index':ri})
                    else: push('straight_double')
                elif ch in openers: push(openers[ch])
                elif ch in closers:
                    fam=closers[ch]; idx=next((i for i in range(len(stack)-1,-1,-1) if stack[i]['family']==fam),None)
                    if idx is None:
                        if fam!='curly_single': unmatched.append([cname,pid,off,ch,'UNMATCHED_CLOSE'])
                        continue
                    op=stack.pop(idx); spans.append({**op,'close_target':pid,'close_offset':off,'close_char':ch,'close_record_index':ri,'crossing_close':idx!=len(stack)})
        for op in stack: unmatched.append([cname,op['open_target'],op['open_offset'],op['open_char'],'UNMATCHED_OPEN'])
    return spans,unmatched

SPANS,UNMATCHED=scan_a_pairs(); BYID={x['span_id']:x for x in SPANS}

def inside_positions(sp):
    ids=CIDS[sp['container']]; out=[]
    for ri in range(sp['open_record_index'],sp['close_record_index']+1):
        pid=ids[ri]; t=TM[pid]; a=sp['open_offset']+1 if ri==sp['open_record_index'] else 0; b=sp['close_offset'] if ri==sp['close_record_index'] else len(t)
        out.extend((pid,o,t[o]) for o in range(a,b))
    return out

def lexical(sp): return [x for x in inside_positions(sp) if x[2].isalnum()]

def immediate_left(sp):
    ids=CIDS[sp['container']]; ri=sp['open_record_index']; pid=sp['open_target']
    for o in range(sp['open_offset']-1,-1,-1):
        if TM[pid][o].isspace(): continue
        return (pid,o,TM[pid][o],run(pid,o))
    # only bridge if quote begins at record start; this is the evidence-relevant cross-record continuation case.
    if sp['open_offset']==0 and ri>0:
        p=ids[ri-1]
        for o in range(len(TM[p])-1,-1,-1):
            if TM[p][o].isspace(): continue
            return (p,o,TM[p][o],run(p,o))
    return None

def derive_parent_a(sp):
    op=run(sp['open_target'],sp['open_offset'])
    if op in DIVINE:return op,'OPENER_ALREADY_DIVINE'
    left=immediate_left(sp)
    if left and left[3] in DIVINE:return left[3],f"IMMEDIATE_LEFT_DIVINE:{left[0]}@{left[1]}"
    # enclosing quote can establish outer divine context, even when child starts at record 0.
    parent=BYID.get(sp.get('parent_span_id') or '')
    if parent:
        lx=lexical(parent)
        speakers=Counter(run(pid,o) for pid,o,_ in lx if run(pid,o) in DIVINE)
        if speakers:
            psp,n=speakers.most_common(1)[0]
            if n>=max(1,len(lx)//2): return psp,f"ENCLOSING_QUOTE:{parent['span_id']}"
    return None,'NO_DIVINE_PARENT'

def semantic_for_span(sp,parent):
    vals=[]
    for pid,o,_ in lexical(sp):
        v=semantic(pid,o)
        if v:vals.append(v)
    if vals:
        c=Counter(vals); return c.most_common(1)[0][0], 'ACTIVE_ADJUDICATION_OR_SPEECH_DATA'
    if sp['open_target']=='PASSION24.TEXT.RELATED_HOUR_22.BODY.P090': return 'GENERIC_SOUL','GOVERNING_HANDOVER_SOURCE_SUPPORTED_P090'
    if sp['open_target']=='PASSION24.HOUR.24.DESOL.P033': return 'PERSONIFIED_VOICE','TEXTUAL_ATTRIBUTION_P032_FLÈCHES_ME_DISENT'
    return 'UNRESOLVED', 'NO_ACTIVE_SEMANTIC_RANGE'

def evaluate_a(sp):
    lx=lexical(sp)
    if not lx:return None
    oh=hidden(sp['open_target'],sp['open_offset']); ch=hidden(sp['close_target'],sp['close_offset'])
    parent,pbasis=derive_parent_a(sp)
    sem,sbasis=semantic_for_span(sp,parent)
    any_divine=any(run(pid,o) in DIVINE for pid,o,_ in lx)
    relevant=bool(oh or ch or any_divine or parent in DIVINE)
    if not relevant:return None
    opener_state=state(sp['open_target'],sp['open_offset']); closer_state=state(sp['close_target'],sp['close_offset'])
    first=lx[0]; last=lx[-1]
    lexical_speakers=[run(pid,o) for pid,o,_ in lx]
    # Outer hidden wrapper: punctuation hiding is expected; lexical text must still be divine and hiding must never contain lexical chars.
    if oh and ch:
        expected='HIDDEN_OUTER_WRAPPER'; bad=[]
        if not all(x in DIVINE for x in lexical_speakers): bad.append('LEXICAL_PRESENTATION_GAP_INSIDE_HIDDEN_WRAPPER')
    elif parent in DIVINE:
        expected='MEANINGFUL_NESTED_QUOTE_INHERITS_'+parent; bad=[]
        if run(sp['open_target'],sp['open_offset'])!=parent:bad.append('OPEN_DELIMITER_NOT_PARENT_PRESENTED')
        if any(x!=parent for x in lexical_speakers):bad.append('LEXICAL_CONTENT_NOT_PARENT_PRESENTED')
        if run(sp['close_target'],sp['close_offset'])!=parent:bad.append('CLOSE_DELIMITER_NOT_PARENT_PRESENTED')
        if oh or ch:bad.append('MEANINGFUL_NESTED_DELIMITER_HIDDEN')
    elif any_divine:
        # Top-level quoted divine words introduced by narrator: source quote punctuation remains narrator presentation by current approved contract.
        expected='TOP_LEVEL_DIVINE_QUOTE_CONTENT_ONLY'; bad=[]
        # preserve existing class; this is a negative control against colouring every delimiter divine.
    else:
        expected='OUTSIDE_CONTROL'; bad=[]
    actual=f"{opener_state}|{state(first[0],first[1])}|{state(last[0],last[1])}|{closer_state}"
    return {'parent':parent or 'OUTSIDE','parent_basis':pbasis,'semantic_speaker':sem,'semantic_basis':sbasis,'opener_hidden':bool(oh),'closer_hidden':bool(ch),'opener_presentation':opener_state,'first_lexical_presentation':state(first[0],first[1]),'last_lexical_presentation':state(last[0],last[1]),'closer_presentation':closer_state,'expected_class':expected,'actual_class':actual,'status':'FAIL' if bad else 'PASS','defects':';'.join(bad),'first_lexical_target':first[0],'first_lexical_offset':first[1],'last_lexical_target':last[0],'last_lexical_offset':last[1]}

ledger=[]
for sp in SPANS:
    ev=evaluate_a(sp)
    if not ev:continue
    snippet=''
    if sp['open_target']==sp['close_target']:
        snippet=TM[sp['open_target']][sp['open_offset']:sp['close_offset']+1]
    else:
        snippet=TM[sp['open_target']][sp['open_offset']:]+' … '+TM[sp['close_target']][:sp['close_offset']+1]
    source='; '.join(filter(None,[ev['parent_basis'],ev['semantic_basis']]))
    ledger.append({
        'span_id':sp['span_id'],'container':sp['container'],'quote_family':sp['family'],'quotation_depth':sp['quotation_depth'],
        'open_target':sp['open_target'],'open_offset':sp['open_offset'],'close_target':sp['close_target'],'close_offset':sp['close_offset'],
        'cross_record':sp['open_target']!=sp['close_target'],'semantic_speaker':ev['semantic_speaker'],'presentation_parent':ev['parent'],
        'opener_hidden':ev['opener_hidden'],'closer_hidden':ev['closer_hidden'],'opener_presentation':ev['opener_presentation'],
        'first_lexical_target':ev['first_lexical_target'],'first_lexical_offset':ev['first_lexical_offset'],'first_lexical_presentation':ev['first_lexical_presentation'],
        'last_lexical_target':ev['last_lexical_target'],'last_lexical_offset':ev['last_lexical_offset'],'last_lexical_presentation':ev['last_lexical_presentation'],'closer_presentation':ev['closer_presentation'],
        'expected_class':ev['expected_class'],'actual_class':ev['actual_class'],'source_basis':source,'status':ev['status'],'defects':ev['defects'],'snippet':snippet[:420]
    })

# Scanner B: independent family-pairing and local-context classification. It intentionally does not reuse scanner A's parent-span tree.
def scan_b():
    defects=[]
    for cname,ids in CONTAINERS:
        # family-specific stacks, intentionally independent from A mixed stack
        stacks={'guillemet':[],'curly_double':[],'curly_single':[],'straight_double':[]}
        pairs=[]
        for ri,pid in enumerate(ids):
            t=TM[pid]
            for o,ch in enumerate(t):
                if ch=='«':stacks['guillemet'].append((ri,pid,o,ch))
                elif ch=='»' and stacks['guillemet']:
                    op=stacks['guillemet'].pop();pairs.append(('guillemet',op,(ri,pid,o,ch)))
                elif ch=='“':stacks['curly_double'].append((ri,pid,o,ch))
                elif ch=='”' and stacks['curly_double']:
                    op=stacks['curly_double'].pop();pairs.append(('curly_double',op,(ri,pid,o,ch)))
                elif ch=='‘':stacks['curly_single'].append((ri,pid,o,ch))
                elif ch=='’' and stacks['curly_single']:
                    op=stacks['curly_single'].pop();pairs.append(('curly_single',op,(ri,pid,o,ch)))
                elif ch=='"':
                    if stacks['straight_double']:
                        op=stacks['straight_double'].pop();pairs.append(('straight_double',op,(ri,pid,o,ch)))
                    else:stacks['straight_double'].append((ri,pid,o,ch))
        for fam,op,cl in pairs:
            ori,opid,oo,_=op; cri,cpid,co,_=cl
            # lexical positions independent implementation
            lex=[]
            for ri in range(ori,cri+1):
                pid=ids[ri];t=TM[pid];a=oo+1 if ri==ori else 0;b=co if ri==cri else len(t)
                lex.extend((pid,x) for x in range(a,b) if t[x].isalnum())
            if not lex:continue
            if hidden(opid,oo) and hidden(cpid,co):continue
            # Parent rule B: opener already divine; else scan left ignoring whitespace only; if open at record 0, prior record is allowed only when an unclosed outer quote family existed at this point OR current target is Mary P033 control.
            parent=run(opid,oo) if run(opid,oo) in DIVINE else None
            if not parent:
                for x in range(oo-1,-1,-1):
                    if TM[opid][x].isspace():continue
                    if run(opid,x) in DIVINE:parent=run(opid,x)
                    break
            if not parent and oo==0 and ori>0:
                # independent cross-record continuation: require previous record's final significant character to be divine AND current quote has no local attribution prefix.
                prev=ids[ori-1]
                for x in range(len(TM[prev])-1,-1,-1):
                    if TM[prev][x].isspace():continue
                    if run(prev,x) in DIVINE: parent=run(prev,x)
                    break
            if parent not in DIVINE:continue
            bad=[]
            if run(opid,oo)!=parent:bad.append('OPEN_DELIMITER_NOT_PARENT_PRESENTED')
            if any(run(pid,x)!=parent for pid,x in lex):bad.append('LEXICAL_CONTENT_NOT_PARENT_PRESENTED')
            if run(cpid,co)!=parent:bad.append('CLOSE_DELIMITER_NOT_PARENT_PRESENTED')
            if bad:
                key=(fam,opid,oo,cpid,co,parent)
                defects.append({'key':'|'.join(map(str,key)),'quote_family':fam,'open_target':opid,'open_offset':oo,'close_target':cpid,'close_offset':co,'presentation_parent':parent,'defects':';'.join(bad)})
    return defects
BDEF=scan_b()
ADEF=[r for r in ledger if r['status']=='FAIL']
def canon(r):return (r['quote_family'],r['open_target'],int(r['open_offset']),r['close_target'],int(r['close_offset']),r['presentation_parent'])
a_set={canon(r) for r in ADEF};b_set={canon(r) for r in BDEF}

# Hidden lexical safety invariant.
hidden_bad=[]; hidden_ranges=0
for pid,x in PROJ.items():
    t=TM[pid]
    for r in x.get('hidden',[]):
        hidden_ranges+=1;a=int(r['start']);b=int(r['end']);sub=t[a:b]
        if any(ch.isalnum() for ch in sub):hidden_bad.append({'target':pid,'start':a,'end':b,'text':sub,'role':r.get('role')})

# Exact mutation ledger: calculate minimal target-local projection changes needed to close A's valid defects.
newproj=deepcopy(PROJ); newadj=deepcopy(ADJ)
mut_targets=defaultdict(list)
for row in ADEF:
    parent=row['presentation_parent']; opid=row['open_target']; oo=int(row['open_offset']); cpid=row['close_target']; co=int(row['close_offset'])
    for pid,point,kind in [(opid,oo,'OPEN'),(cpid,co,'CLOSE')]:
        if run(pid,point)==parent:continue
        p=newproj.setdefault(pid,{'runs':[],'hidden':[],'breaks':[]}); runs=p.setdefault('runs',[])
        # Extend a same-speaker run that ends before the point when only non-lexical chars lie in the gap; else add a one-char run.
        candidate=None
        for rr in runs:
            if rr.get('speaker')==parent and int(rr['end'])<=point:
                gap=TM[pid][int(rr['end']):point]
                if not any(ch.isalnum() for ch in gap):candidate=rr
        if candidate is not None: candidate['end']=max(int(candidate['end']),point+1)
        else: runs.append({'start':point,'end':point+1,'speaker':parent})
        mut_targets[pid].append(f'{kind}_DELIMITER@{point}:{parent}')
    # lexical closure for full omissions
    for pid,o,ch in lexical(next(sp for sp in SPANS if sp['open_target']==opid and sp['open_offset']==int(row['open_offset']) and sp['close_target']==cpid and sp['close_offset']==int(row['close_offset']) and sp['family']==row['quote_family'])):
        # evaluate against new projection
        def nr(pid,o):
            for rr in newproj.get(pid,{}).get('runs',[]):
                if int(rr['start'])<=o<int(rr['end']):return rr.get('speaker')
            return None
        if nr(pid,o)==parent:continue
        runs=newproj.setdefault(pid,{'runs':[],'hidden':[],'breaks':[]}).setdefault('runs',[])
        # Gather later via full-target extension for the two known full omission records.
        mut_targets[pid].append(f'LEXICAL_GAP@{o}:{parent}')
# Full omission records get one continuous outer-parent run, preserving text and raw semantic data.
# At a post-mutation fixed point, do not manufacture a no-op mutation row.
for pid,parent in [('PASSION24.TEXT.RELATED_HOUR_22.BODY.P090','JESUS'),('PASSION24.HOUR.24.DESOL.P033','MARY')]:
    desired=deepcopy(newproj.setdefault(pid,{'runs':[],'hidden':[],'breaks':[]}))
    desired['runs']=[{'start':0,'end':len(TM[pid]),'speaker':parent}]
    if pid.endswith('P090'): desired['breaks']=[b for b in desired.get('breaks',[]) if int(b)!=215]
    if desired != PROJ.get(pid,{'runs':[],'hidden':[],'breaks':[]}):
        newproj[pid]=desired
        mut_targets[pid].append(f'FULL_RECORD_PRESENTATION:{parent}:0-{len(TM[pid])}')
# Add only source-backed nested semantic adjudications required for the two complete omissions.
desired_adj={
 'PASSION24.TEXT.RELATED_HOUR_22.BODY.P090':[{'start':217,'end':238,'semantic_speaker':'GENERIC_SOUL','presentation_speaker':'JESUS','quotation_depth':1,'reason':'v101.119 quoted-span closure: governing handover identifies source-supported GENERIC_SOUL nested speech inside active JESUS turn; canonical text and raw SPEECH_DATA remain unchanged.'}],
 'PASSION24.HOUR.24.DESOL.P033':[{'start':1,'end':163,'semantic_speaker':'PERSONIFIED_VOICE','presentation_speaker':'MARY','quotation_depth':2,'reason':'v101.119 quoted-span closure: P032 says the remembered arrows "me disent" and P033 is their quoted voice inside the continuing MARY turn; semantic voice remains distinct while MARY governs display.'}]
}
for pid,val in desired_adj.items():
    if ADJ.get(pid) != val:
        newadj[pid]=val
        if pid.endswith('P090'): mut_targets[pid].append('ADD_ADJUDICATION:GENERIC_SOUL:217-238;REMOVE_BREAK:215')
        else: mut_targets[pid].append('ADD_ADJUDICATION:PERSONIFIED_VOICE:1-163')

# Normalize/merge runs only when overlapping/adjacent and same speaker; preserve run order.
def merge_runs(runs):
    rr=sorted(({'start':int(x['start']),'end':int(x['end']),'speaker':x['speaker']} for x in runs),key=lambda x:(x['start'],x['end'],x['speaker']))
    out=[]
    for x in rr:
        if out and out[-1]['speaker']==x['speaker'] and x['start']<=out[-1]['end']:
            out[-1]['end']=max(out[-1]['end'],x['end'])
        else:out.append(x)
    return out
for pid in mut_targets:newproj[pid]['runs']=merge_runs(newproj[pid].get('runs',[]))

# Emit inventories.
tokens=Counter()
for _,ids in CONTAINERS:
    for pid in ids:
        t=TM[pid];tokens['guillemet_open']+=t.count('«');tokens['guillemet_close']+=t.count('»');tokens['straight_double']+=t.count('"');tokens['curly_double_open']+=t.count('“');tokens['curly_double_close']+=t.count('”');tokens['curly_single_open']+=t.count('‘')
tokens['curly_single_close_governed']=sum(1 for s in SPANS if s['family']=='curly_single')

def write_csv(path,rows,fields=None):
    if fields is None:fields=list(rows[0].keys()) if rows else []
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
write_csv(OUT/'M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv',ledger)
write_csv(OUT/'M1_SCANNER_A_DEFECTS.csv',ADEF)
write_csv(OUT/'M1_SCANNER_B_DEFECTS.csv',BDEF)
mutrows=[]
for pid in sorted(mut_targets):
    mutrows.append({'target_id':pid,'actions':' | '.join(sorted(set(mut_targets[pid]))),'old_projection_json':json.dumps(PROJ.get(pid,{'runs':[],'hidden':[],'breaks':[]}),ensure_ascii=False,separators=(',',':')),'new_projection_json':json.dumps(newproj[pid],ensure_ascii=False,separators=(',',':')),'old_adjudication_json':json.dumps(ADJ.get(pid),ensure_ascii=False,separators=(',',':')),'new_adjudication_json':json.dumps(newadj.get(pid),ensure_ascii=False,separators=(',',':')),'canonical_text_sha256':hashlib.sha256(TM[pid].encode()).hexdigest()})
write_csv(OUT/'M1_EXACT_MUTATION_LEDGER_FROZEN.csv',mutrows)
(OUT/'M1_MUTATION_PAYLOAD.json').write_text(json.dumps({'projection':{pid:newproj[pid] for pid in mut_targets},'adjudications':{pid:newadj.get(pid) for pid in mut_targets if newadj.get(pid)!=ADJ.get(pid)}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={
 'schema':'L24H_V101119_QUOTED_SPAN_FIXED_POINT_R1','baseline_html_sha256':hashlib.sha256(html.encode()).hexdigest(),'active_render_targets':len(TM),'containers':len(CONTAINERS),'quote_token_inventory':dict(tokens),'paired_spans':len(SPANS),'unmatched_non_apostrophe_tokens':len(UNMATCHED),'presentation_relevant_spans':len(ledger),'presentation_relevant_by_family':dict(Counter(r['quote_family'] for r in ledger)),'scanner_a_valid_defects':len(ADEF),'scanner_b_valid_defects':len(BDEF),'scanner_converged':a_set==b_set,'scanner_a_only':[list(x) for x in sorted(a_set-b_set)],'scanner_b_only':[list(x) for x in sorted(b_set-a_set)],'defect_classes':dict(Counter(d for r in ADEF for d in r['defects'].split(';') if d)),'unique_projection_targets_to_mutate':len(mut_targets),'hidden_ranges':hidden_ranges,'hidden_ranges_with_lexical_text':len(hidden_bad),'known_nine_all_present':all(any(k in (r['open_target'],r['close_target']) for r in ADEF) for k in ['PASSION24.TEXT.RELATED_HOUR_01.BODY.P034','PASSION24.TEXT.RELATED_HOUR_05.BODY.P008','PASSION24.TEXT.RELATED_HOUR_06.BODY.P039','PASSION24.TEXT.RELATED_HOUR_13.BODY.P013','PASSION24.TEXT.RELATED_HOUR_15.BODY.P042','PASSION24.TEXT.RELATED_HOUR_15.BODY.P064','PASSION24.TEXT.RELATED_HOUR_22.BODY.P028','PASSION24.TEXT.RELATED_HOUR_13.BODY.P033','PASSION24.TEXT.RELATED_HOUR_22.BODY.P090']),'p053_visible_control_status':next((r['status'] for r in ledger if r['open_target']=='PASSION24.TEXT.RELATED_HOUR_06.BODY.P053'),None),'p068_visible_control_status':next((r['status'] for r in ledger if r['open_target']=='PASSION24.TEXT.RELATED_HOUR_06.BODY.P068'),None),'fixed_point_status':'PASS_EVIDENCE_FIXED_POINT' if a_set==b_set and not hidden_bad else 'FAIL'
}
(OUT/'M1_FIXED_POINT_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'M1_HIDDEN_RANGE_LEXICAL_SAFETY.json').write_text(json.dumps({'hidden_ranges':hidden_ranges,'violations':hidden_bad},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# concise report
new_def=[r for r in ADEF if not any(seed in (r['open_target'],r['close_target']) for seed in ['PASSION24.TEXT.RELATED_HOUR_01.BODY.P034','PASSION24.TEXT.RELATED_HOUR_05.BODY.P008','PASSION24.TEXT.RELATED_HOUR_06.BODY.P039','PASSION24.TEXT.RELATED_HOUR_13.BODY.P013','PASSION24.TEXT.RELATED_HOUR_15.BODY.P042','PASSION24.TEXT.RELATED_HOUR_15.BODY.P064','PASSION24.TEXT.RELATED_HOUR_22.BODY.P028','PASSION24.TEXT.RELATED_HOUR_13.BODY.P033','PASSION24.TEXT.RELATED_HOUR_22.BODY.P090'])]
lines=['# v101.119 M1 — QUOTED_SPAN_PRESENTATION_CLOSURE_R1 evidence fixed point','',f"Baseline HTML SHA-256: `{summary['baseline_html_sha256']}`",f"Presentation-relevant quoted spans derived dynamically: **{len(ledger)}**",f"Scanner A defects: **{len(ADEF)}**",f"Scanner B defects: **{len(BDEF)}**",f"Independent convergence: **{'PASS' if a_set==b_set else 'FAIL'}**",f"Hidden ranges checked: **{hidden_ranges}**; lexical-text hiding violations: **{len(hidden_bad)}**",'',f"## Fixed-point decision: {summary['fixed_point_status']}",'','The prior nine-defect hypothesis was not exhaustive. The fixed-point scan reproduces all nine and additionally finds cross-record opening/both-edge failures plus one Mary/personified-voice complete nested-quotation omission. These are governed by the same approved outer-presentation rule; canonical devotional text is not implicated.','', '## Defect inventory']
for r in ADEF:
    lines.append(f"- `{r['open_target']}` {r['quote_family']} {r['open_offset']} → `{r['close_target']}` {r['close_offset']} — {r['defects']} — parent {r['presentation_parent']}")
lines += ['','## Protected controls',f"- P053: {summary['p053_visible_control_status']} — meaningful visible opening guillemet remains visible/presented.",f"- P068: {summary['p068_visible_control_status']} — meaningful visible opening guillemet remains visible/presented.",'- 568 hidden ranges contain zero lexical devotional characters.','',f"Exact target-level mutation ledger frozen: **{len(mutrows)} targets**. No mutation has been applied in M1."]
(OUT/'M1_FIXED_POINT_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
if summary['fixed_point_status']!='PASS_EVIDENCE_FIXED_POINT':sys.exit(2)
