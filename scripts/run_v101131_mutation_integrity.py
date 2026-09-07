#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib
BASE=Path(sys.argv[1]); CAND=Path(sys.argv[2]); OUT=Path(sys.argv[3]); OUT.parent.mkdir(parents=True,exist_ok=True)

def text(p): return Path(p).read_text(encoding='utf-8')
def obj(s,n):
 st=s.index('const '+n+' = ')+len('const '+n+' = '); return json.JSONDecoder().raw_decode(s[st:])[0]
def raw(s,n):
 st=s.index('const '+n+' = ')+len('const '+n+' = ')
 try:
  _,e=json.JSONDecoder().raw_decode(s[st:]); return s[st:st+e]
 except json.JSONDecodeError:
  en=s.index(';',st); return s[st:en]
def repl(s,n,o):
 st=s.index('const '+n+' = ')+len('const '+n+' = '); _,e=json.JSONDecoder().raw_decode(s[st:]); return s[:st]+json.dumps(o,ensure_ascii=False,separators=(',',':'))+s[st+e:]
bs=text(BASE); cs=text(CAND)
rows=[]
def add(n,ok,d=None):rows.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
add('candidate_identity',"const APP_VERSION = 'v101.131';" in cs and "const APP_EVIDENCE_STAGE = 'GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR_R1';" in cs)
for n in ['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY']:
 add(n+'_raw_literal_unchanged',raw(bs,n)==raw(cs,n))
BSD=obj(bs,'SPEECH_DATA'); BSPA=obj(bs,'SPEECH_PRESENTATION_ADJUDICATIONS'); BSE=obj(bs,'SPEECH_END_VISUAL_BREAKS'); BSPP=obj(bs,'SPEECH_PRESENTATION_PROJECTION'); BVPT=obj(bs,'VISIBLE_PARAGRAPH_TOPOLOGY')
SD=json.loads(json.dumps(BSD));SPA=json.loads(json.dumps(BSPA));SE=json.loads(json.dumps(BSE));SPP=json.loads(json.dumps(BSPP));VPT=json.loads(json.dumps(BVPT))
def rem(m,p,x):
 v=list(m[p]);v.remove(x); m[p]=v
 if not v: del m[p]
def addb(m,p,x):m[p]=sorted(list(m.get(p,[]))+[x])
# independent expected mutation application
p='PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P057';SPP[p]={'runs':[{'start':0,'end':114,'speaker':'JESUS'}],'hidden':[],'breaks':[]};rem(SE,p,78);rem(VPT['local_breaks'],p,78);SPA[p]=[{'start':78,'end':113,'semantic_speaker':'OTHER','presentation_speaker':'JESUS','quotation_depth':2,'reason':'v101.131 M1C001 user-approved global raw-quote audit: nested quoted saying remains semantically distinct while inheriting the active outer JESUS presentation; visible straight-quote delimiters remain inline.'}]
p='PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P100';SD[p]=[{'speaker':'JESUS','start':0,'end':38},{'speaker':'JESUS','start':40,'end':98}];SPP[p]={'runs':[{'start':0,'end':99,'speaker':'JESUS'}],'hidden':[],'breaks':[]};rem(SE,p,40);rem(VPT['local_breaks'],p,40)
p67='PASSION24.TEXT.RELATED_HOUR_21.BODY.P067';p68='PASSION24.TEXT.RELATED_HOUR_21.BODY.P068';p69='PASSION24.TEXT.RELATED_HOUR_21.BODY.P069';p70='PASSION24.TEXT.RELATED_HOUR_21.BODY.P070';p71='PASSION24.TEXT.RELATED_HOUR_21.BODY.P071';p72='PASSION24.TEXT.RELATED_HOUR_21.BODY.P072';p73='PASSION24.TEXT.RELATED_HOUR_21.BODY.P073'
SPP[p67]={'runs':[],'hidden':[{'start':47,'end':48,'role':'OUTER_DIVINE_OPEN_WRAPPER_HIDE','reason':'v101.131 M1C003 user-approved FATHER direct-turn wrapper suppression'}],'breaks':[]}
for p,L in [(p68,36),(p69,418),(p70,259),(p71,117),(p72,130)]:SD[p]=[{'speaker':'FATHER','start':0,'end':L}];SPP[p]={'runs':[{'start':0,'end':L,'speaker':'FATHER'}],'hidden':[],'breaks':[]}
SD[p73]=[{'speaker':'FATHER','start':0,'end':259}];SPP[p73]={'runs':[{'start':0,'end':259,'speaker':'FATHER'}],'hidden':[{'start':259,'end':260,'role':'OUTER_DIVINE_CLOSE_WRAPPER_HIDE','reason':'v101.131 M1C003 user-approved FATHER direct-turn wrapper suppression'}],'breaks':[260]};addb(SE,p73,260);addb(VPT['local_breaks'],p73,260)
p='PASSION24.TEXT.RELATED_HOUR_21.BODY.P100';SD[p]=[{'speaker':'JESUS','start':27,'end':55}];SPP[p]={'runs':[{'start':27,'end':55,'speaker':'JESUS'}],'hidden':[],'breaks':[]}
CSD=obj(cs,'SPEECH_DATA');CSPA=obj(cs,'SPEECH_PRESENTATION_ADJUDICATIONS');CSE=obj(cs,'SPEECH_END_VISUAL_BREAKS');CSPP=obj(cs,'SPEECH_PRESENTATION_PROJECTION');CVPT=obj(cs,'VISIBLE_PARAGRAPH_TOPOLOGY')
for n,a,b in [('SPEECH_DATA',CSD,SD),('SPEECH_PRESENTATION_ADJUDICATIONS',CSPA,SPA),('SPEECH_END_VISUAL_BREAKS',CSE,SE),('SPEECH_PRESENTATION_PROJECTION',CSPP,SPP),('VISIBLE_PARAGRAPH_TOPOLOGY',CVPT,VPT)]: add(n+'_equals_independent_expected_mutation',a==b,{'candidate_count':len(a),'expected_count':len(b)} if hasattr(a,'__len__') else None)
# Prove there is no hidden HTML change: revert candidate authorities + release identity and compare exact predecessor HTML.
r=cs
for n,o in [('SPEECH_DATA',BSD),('SPEECH_PRESENTATION_ADJUDICATIONS',BSPA),('SPEECH_END_VISUAL_BREAKS',BSE),('SPEECH_PRESENTATION_PROJECTION',BSPP),('VISIBLE_PARAGRAPH_TOPOLOGY',BVPT)]:r=repl(r,n,o)
r=r.replace("const APP_VERSION = 'v101.131';","const APP_VERSION = 'v101.130';",1).replace("const APP_EVIDENCE_STAGE = 'GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR_R1';","const APP_EVIDENCE_STAGE = 'FOUR_PASS_FINAL_PACKAGE_METADATA_EVIDENCE_RECONCILIATION_R1';",1).replace("const BUILD_DATE = '2026-09-03'; // v101.131 / global raw-quote host-sentence successor; no canonical text mutation","const BUILD_DATE = '2026-09-03'; // v101.130 / four-pass final package metadata/evidence reconciliation; no canonical text mutation",1)
add('candidate_html_reverts_exactly_to_v101130',r==bs,{'base_sha256':hashlib.sha256(bs.encode()).hexdigest(),'reverted_sha256':hashlib.sha256(r.encode()).hexdigest()})
add('p067_p068_cross_record_join_preserved',['PASSION24.TEXT.RELATED_HOUR_21.BODY.P067','PASSION24.TEXT.RELATED_HOUR_21.BODY.P068'] in CVPT['cross_record_joins'])
add('v101129_closed_break_controls_preserved',CSPP['PASSION24.HOUR.08.P009']['breaks']==[93,210] and CSPP['PASSION24.TEXT.RELATED_HOUR_06.BODY.P043']['breaks']==[])
sm={'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'total':len(rows)}
OUT.write_text(json.dumps({'schema':'L24H_V101131_MUTATION_INTEGRITY_V1','version':'v101.131','summary':sm,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
