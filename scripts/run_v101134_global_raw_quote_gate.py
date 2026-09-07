#!/usr/bin/env python3
from pathlib import Path
import sys,json,re,csv,hashlib
HTML=Path(sys.argv[1]); FROZEN=Path(sys.argv[2]); OUT=Path(sys.argv[3]); OUT.parent.mkdir(parents=True,exist_ok=True)
s=HTML.read_text(encoding='utf-8')
def obj(n):
 m=re.search(rf'const\s+{re.escape(n)}\s*=\s*',s);o,_=json.JSONDecoder().raw_decode(s[m.end():]);return o
def h(t):return hashlib.sha256(t.encode('utf-8')).hexdigest()
C=obj('CORPUS');T=obj('TEXT_LIBRARY');SD=obj('SPEECH_DATA');SP=obj('SPEECH_PRESENTATION_PROJECTION')
records=[];docseq=0
def add(i,t,c,d,do,ro):records.append({'record_id':i,'text':t or '','record_class':c,'doc_id':d,'doc_order':do,'record_order':ro})
for hour in C['hours']:
 hid=hour['hour_id'];docseq+=1
 for i,p in enumerate(hour.get('paragraphs',[]),1):add(p['id'],p.get('t',''),'hour_meditation',hid+'.MEDITATION',docseq,i)
 docseq+=1
 for i,p in enumerate(hour.get('reflections',[]),1):add(p['id'],p.get('t',''),'hour_reflection',hid+'.REFLECTION',docseq,i)
 for sub in hour.get('subsections',[]):
  docseq+=1
  for i,p in enumerate(sub.get('paragraphs',[]),1):add(p['id'],p.get('t',''),'hour_subsection',sub.get('id',hid+'.SUB'),docseq,i)
for pr in C['prayers']:
 docseq+=1
 for i,p in enumerate(pr.get('paragraphs',[]),1):add(p['id'],p.get('t',''),'prayer',pr['prayer_id'],docseq,i)
for sec in C['sections']:
 if sec.get('paragraphs'):
  docseq+=1
  for i,p in enumerate(sec['paragraphs'],1):add(p['id'],p.get('t',''),'section_including_benefits',sec['section_id'],docseq,i)
items=[x for x in T if x.get('type')!='library_group']
for item in items:
 body=item.get('body') or [];stable=item.get('body_stable_numbers');docseq+=1
 for i,t in enumerate(body,1):
  n=int(stable[i-1]) if stable is not None else i;add(f"{item['id']}.BODY.P{n:03d}",t,'library_text',item['id'],docseq,i)
 opts=item.get('practice_options') or []
 if opts:
  docseq+=1
  for i,t in enumerate(opts,1):add(f"{item['id']}.PRACTICE.P{i:03d}",t,'library_practice_option',item['id']+'.PRACTICE',docseq,i)
for item in items:
 docseq+=1;add(item['id']+'.TITLE',item.get('title',''),'library_title_separate',item['id']+'.TITLE',docseq,1)
with FROZEN.open(encoding='utf-8-sig',newline='') as f: frozen={r['record_id']:r['text'] for r in csv.DictReader(f)}
cur={r['record_id']:r['text'] for r in records};quote=set('«»“”"');q=[r for r in records if any(c in r['text'] for c in quote)]
rows=[]
def addc(n,ok,d=None):rows.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
addc('all_text_record_count_4613',len(records)==4613,len(records));addc('raw_record_identity_set_exact',set(cur)==set(frozen),{'current':len(cur),'frozen':len(frozen),'added':sorted(set(cur)-set(frozen))[:5],'missing':sorted(set(frozen)-set(cur))[:5]})
diffs=[k for k in cur if k in frozen and cur[k]!=frozen[k]];addc('raw_text_all_4613_records_byte_character_identical',not diffs,{'diff_count':len(diffs),'sample':diffs[:10]});addc('quote_bearing_record_count_807',len(q)==807,len(q))
# Post-mutation unmapped count is allowed to fall; record it, but require exact expected current count.
unmapped=[r['record_id'] for r in q if r['record_id'] not in SD and r['record_id'] not in SP];addc('postmutation_quote_bearing_unmapped_count_202',len(unmapped)==202,len(unmapped))
# Approved raw-speech completeness loci.
def cov(pid,speaker,start,end):
 return any(x.get('speaker')==speaker and x.get('start')==start and x.get('end')==end for x in SD.get(pid,[]))
addc('M1C002_nested_JESUS_semantic_covered',cov('PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P100','JESUS',40,98),SD.get('PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P100'))
for pid,L in [('PASSION24.TEXT.RELATED_HOUR_21.BODY.P068',36),('PASSION24.TEXT.RELATED_HOUR_21.BODY.P069',418),('PASSION24.TEXT.RELATED_HOUR_21.BODY.P070',259),('PASSION24.TEXT.RELATED_HOUR_21.BODY.P071',117),('PASSION24.TEXT.RELATED_HOUR_21.BODY.P072',130),('PASSION24.TEXT.RELATED_HOUR_21.BODY.P073',259)]:addc(pid+'_FATHER_semantic_covered',cov(pid,'FATHER',0,L),SD.get(pid))
addc('M1C004_nested_JESUS_semantic_covered',cov('PASSION24.TEXT.RELATED_HOUR_21.BODY.P100','JESUS',27,55),SD.get('PASSION24.TEXT.RELATED_HOUR_21.BODY.P100'))
# Frozen raw-text hash is the first-class completeness authority: any corpus/library text change forces re-adjudication.
aggregate=h('\n'.join(k+'\0'+cur[k] for k in sorted(cur)));fagg=h('\n'.join(k+'\0'+frozen[k] for k in sorted(frozen)));addc('raw_text_aggregate_hash_equals_frozen_M1_universe',aggregate==fagg,{'current':aggregate,'frozen':fagg})
sm={'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'total':len(rows)}
OUT.write_text(json.dumps({'schema':'L24H_V101134_GLOBAL_RAW_TEXT_COMPLETENESS_GATE_V1','version':'v101.134','method':'Reconstruct every raw CORPUS/TEXT_LIBRARY record independently of speech metadata, compare all 4,613 record texts to the M1 frozen raw universe, then assert approved divine-speech coverage. Any raw text insertion/change invalidates the gate before metadata consistency is considered.','summary':sm,'postmutation_unmapped_quote_records':len(unmapped),'raw_aggregate_sha256':aggregate,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
