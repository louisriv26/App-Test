#!/usr/bin/env python3
import csv,json,re,sys
from pathlib import Path
from copy import deepcopy
HTML=Path(sys.argv[1]); LEDGER=Path(sys.argv[2]); MLEDGER=Path(sys.argv[3]); OUT=Path(sys.argv[4])
html=HTML.read_text(encoding='utf-8')

def extract_json(name):
    m=re.search(rf'const\s+{re.escape(name)}\s*=\s*',html); assert m,name
    return json.JSONDecoder().raw_decode(html[m.end():])[0]
proj=extract_json('SPEECH_PRESENTATION_PROJECTION')
rows=list(csv.DictReader(LEDGER.open(encoding='utf-8-sig')))
mutrows={r['target_id']:r for r in csv.DictReader(MLEDGER.open(encoding='utf-8-sig'))}
byid={r['span_id']:r for r in rows}

def state(pj,pid,off):
    x=pj.get(pid,{'runs':[],'hidden':[]})
    hidden=any(int(h.get('start',-1))<=off<int(h.get('end',-1)) for h in x.get('hidden',[]))
    speaker='OUTSIDE'
    for rr in x.get('runs',[]):
        if int(rr['start'])<=off<int(rr['end']): speaker=rr['speaker']; break
    return speaker,hidden

def detect(pj,r):
    exp=r['expected_class']; parent=r['presentation_parent']
    pts=[('opener',r['open_target'],int(r['open_offset'])),('first',r['first_lexical_target'],int(r['first_lexical_offset'])),('last',r['last_lexical_target'],int(r['last_lexical_offset'])),('closer',r['close_target'],int(r['close_offset']))]
    st={k:state(pj,p,o) for k,p,o in pts}
    problems=[]
    if exp=='HIDDEN_OUTER_WRAPPER':
        if not st['opener'][1]: problems.append('opener_not_hidden')
        if not st['closer'][1]: problems.append('closer_not_hidden')
        for k in ('first','last'):
            if st[k][0] not in ('JESUS','MARY','FATHER'): problems.append(k+'_not_divine')
    elif exp.startswith('MEANINGFUL_NESTED_QUOTE_INHERITS_'):
        for k in ('opener','first','last','closer'):
            if st[k][1]: problems.append(k+'_hidden')
            if st[k][0]!=parent: problems.append(k+'_speaker_'+st[k][0]+'_expected_'+parent)
    elif exp=='TOP_LEVEL_DIVINE_QUOTE_CONTENT_ONLY':
        if st['opener'][0]!='OUTSIDE' or st['closer'][0]!='OUTSIDE': problems.append('top_level_delimiter_overcoloured')
    return problems,st

def findrow(**kw):
    for r in rows:
        if all(str(r[k])==str(v) for k,v in kw.items()): return r
    raise KeyError(kw)

tests=[]
# 1 truncate a divine presentation run before a closing delimiter.
r=findrow(close_target='PASSION24.TEXT.RELATED_HOUR_15.BODY.P042')
p=deepcopy(proj); pid=r['close_target']; off=int(r['close_offset'])
for rr in p[pid]['runs']:
    if rr['speaker']==r['presentation_parent'] and int(rr['start'])<=off<int(rr['end']): rr['end']=off; break
problems,st=detect(p,r); tests.append({'test':'TRUNCATE_DIVINE_RUN_BEFORE_CLOSER','span_id':r['span_id'],'target':pid,'detected':bool(problems),'detector_output':problems})
# 2 omit the entire P090 nested generic-soul quotation from JESUS presentation by reverting its projection.
r=findrow(open_target='PASSION24.TEXT.RELATED_HOUR_22.BODY.P090')
p=deepcopy(proj); p[r['open_target']]=json.loads(mutrows[r['open_target']]['old_projection_json'])
problems,st=detect(p,r); tests.append({'test':'OMIT_P090_NESTED_GENERIC_SOUL_FROM_PARENT_PRESENTATION','span_id':r['span_id'],'target':r['open_target'],'detected':bool(problems),'detector_output':problems})
# 3 falsely divine-style the delimiters of a top-level narrator/source wrapper.
r=next(x for x in rows if x['expected_class']=='TOP_LEVEL_DIVINE_QUOTE_CONTENT_ONLY' and x['open_target']==x['close_target'])
p=deepcopy(proj); pid=r['open_target']; a=int(r['open_offset']); b=int(r['close_offset'])+1
old=deepcopy(p.get(pid,{'runs':[],'hidden':[],'breaks':[]})); p[pid]={'runs':[{'speaker':'JESUS','start':a,'end':b}],'hidden':old.get('hidden',[]),'breaks':old.get('breaks',[])}
problems,st=detect(p,r); tests.append({'test':'FALSE_DIVINE_STYLE_NARRATOR_WRAPPER_DELIMITERS','span_id':r['span_id'],'target':pid,'detected':bool(problems),'detector_output':problems})
# 4 hide a meaningful P053 opening delimiter.
r=findrow(open_target='PASSION24.TEXT.RELATED_HOUR_06.BODY.P053')
p=deepcopy(proj); pid=r['open_target']; a=int(r['open_offset']); p[pid].setdefault('hidden',[]).append({'start':a,'end':a+1,'reason':'SYNTHETIC_BAD_HIDE'})
problems,st=detect(p,r); tests.append({'test':'HIDE_MEANINGFUL_P053_OPENING_DELIMITER','span_id':r['span_id'],'target':pid,'detected':bool(problems),'detector_output':problems})
# 5 lose cross-record presentation-parent continuity at the P033 closer by reverting its projection.
r=findrow(close_target='PASSION24.TEXT.RELATED_HOUR_13.BODY.P033')
p=deepcopy(proj); p[r['close_target']]=json.loads(mutrows[r['close_target']]['old_projection_json'])
problems,st=detect(p,r); tests.append({'test':'LOSE_CROSS_RECORD_PARENT_CONTINUITY','span_id':r['span_id'],'target':r['close_target'],'detected':bool(problems),'detector_output':problems})
summary={'tests':len(tests),'detected':sum(t['detected'] for t in tests),'missed':sum(not t['detected'] for t in tests),'status':'PASS' if all(t['detected'] for t in tests) else 'FAIL'}
OUT.write_text(json.dumps({'schema':'L24H_V101119_MUTATION_TESTS_V1','summary':summary,'tests':tests},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
if summary['status']!='PASS': raise SystemExit(2)
