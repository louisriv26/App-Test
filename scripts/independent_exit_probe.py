from pathlib import Path
import json,re,hashlib,csv
ROOT=Path('/mnt/data/v101129_exec_strict'); html=(ROOT/'PRISTINE_V101128/index.html').read_text(encoding='utf-8')
def ex(n):
 m=f'const {n} = '; i=html.index(m)+len(m); return json.JSONDecoder().raw_decode(html[i:])[0]
C=ex('CORPUS'); TL=ex('TEXT_LIBRARY'); SD=ex('SPEECH_DATA'); SPP=ex('SPEECH_PRESENTATION_PROJECTION')
# text map same as prior
M={}
for h in C['hours']:
 for p in h.get('paragraphs',[]):M[p['id']]=p['t']
 for p in h.get('reflections',[]):M[p['id']]=p['t']
 for s in h.get('subsections',[]):
  for p in s.get('paragraphs',[]):M[p['id']]=p['t']
for pr in C.get('prayers',[]):
 for p in pr.get('paragraphs',[]):M[p['id']]=p['t']
for sec in C.get('sections',[]):
 for p in sec.get('paragraphs',[]):M[p['id']]=p['t']
for item in TL:
 if not isinstance(item,dict):continue
 iid=item.get('id','')
 if iid.startswith('PASSION24.TEXT.'):
  nums=item.get('body_stable_numbers') or list(range(1,len(item.get('body') or [])+1))
  for n,t in zip(nums,item.get('body') or []):M[f'{iid}.BODY.P{int(n):03d}']=t

def resume_after(text,end):
 j=end
 # inner French spacing before quote close
 while j<len(text) and text[j] in '\u202f\u00a0': j+=1
 while j<len(text) and text[j] in '»”’"':
  j+=1
  while j<len(text) and text[j] in '\u202f\u00a0':j+=1
 # regular spaces
 k=j
 while k<len(text) and text[k].isspace():k+=1
 # lexical if remaining contains letter/digit or opening quote + letters; terminal punctuation alone isn't lexical host material
 rest=text[k:]
 if not re.search(r'[A-Za-zÀ-ÖØ-öø-ÿ0-9«“"]',rest): return None,k,rest
 return k,k,rest
# terminal SD run groups: merge overlapping/adjacent same speaker spans with gaps only wrappers/whitespace
rows=[]
for pid,spans in SD.items():
 text=M.get(pid)
 if text is None: continue
 spans=sorted(spans,key=lambda x:(x['start'],x['end']))
 # create same-speaker merged groups if gap contains only quotes/punct/space and no alphabetic
 groups=[]
 for s in spans:
  s={'speaker':s['speaker'],'start':int(s['start']),'end':int(s['end'])}
  if groups and groups[-1]['speaker']==s['speaker'] and not re.search(r'[A-Za-zÀ-ÖØ-öø-ÿ0-9]',text[groups[-1]['end']:s['start']]):
   groups[-1]['end']=max(groups[-1]['end'],s['end'])
  else:groups.append(s)
 for gi,g in enumerate(groups):
  k,_,rest=resume_after(text,g['end'])
  if k is None: continue
  rows.append((pid,gi,g['speaker'],g['start'],g['end'],k,text[k:k+60]))
print('SD semantic exits with lexical material',len(rows))
# Compare to SPP extracted row keys from evidence
univ=list(csv.DictReader(open(ROOT/'EVIDENCE_V101129/05_DIRECT_SPEECH_EXIT_UNIVERSE.csv',encoding='utf-8')))
spp={(r['paragraph_id'],r['speaker'],int(r['run_start']),int(r['run_end'])) for r in univ if not r.get('orphan_break')}
missing=[r for r in rows if (r[0],r[2],r[3],r[4]) not in spp]
print('SD exits not exact SPP run key',len(missing))
for r in missing[:100]:print(r)
