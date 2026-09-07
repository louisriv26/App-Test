#!/usr/bin/env python3
from pathlib import Path
import sys,json,copy,re,csv
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');FROZEN=Path(sys.argv[2]);OUT=Path(sys.argv[3]);OUT.parent.mkdir(parents=True,exist_ok=True)
def obj(n):
 st=HTML.index('const '+n+' = ')+len('const '+n+' = ');return json.JSONDecoder().raw_decode(HTML[st:])[0]
SD=obj('SPEECH_DATA');SPP=obj('SPEECH_PRESENTATION_PROJECTION');SE=obj('SPEECH_END_VISUAL_BREAKS');VPT=obj('VISIBLE_PARAGRAPH_TOPOLOGY')
with FROZEN.open(encoding='utf-8-sig',newline='') as f:frozen={r['record_id']:r['text'] for r in csv.DictReader(f)}
# current raw texts from frozen are intentionally authoritative because v101.133 is topology/speaker only.
current=copy.deepcopy(frozen)
expected_spp=copy.deepcopy(SPP);expected_se=copy.deepcopy(SE);expected_vpt=copy.deepcopy(VPT);expected_sd=copy.deepcopy(SD)
def raw_changed(texts):return set(texts)!=set(frozen) or any(texts[k]!=v for k,v in frozen.items())
def metadata_changed(sd,spp,se,vpt):return sd!=expected_sd or spp!=expected_spp or se!=expected_se or vpt!=expected_vpt
def parity(spp,vpt):return {(p,b) for p,x in spp.items() for b in x.get('breaks',[])}.issubset({(p,b) for p,bs in vpt['local_breaks'].items() for b in bs})
rows=[]
def test(code,desc,mut,det):
 texts=copy.deepcopy(current);sd=copy.deepcopy(SD);spp=copy.deepcopy(SPP);se=copy.deepcopy(SE);vpt=copy.deepcopy(VPT);mut(texts,sd,spp,se,vpt);caught=det(texts,sd,spp,se,vpt);rows.append({'mutant':code,'description':desc,'status':'PASS' if caught else 'FAIL','detected':caught})
# A old H08 P009 @42
def A(t,sd,spp,se,vpt):p='PASSION24.HOUR.08.P009';spp[p]['breaks']=sorted(spp[p]['breaks']+[42]);vpt['local_breaks'][p]=sorted(vpt['local_breaks'][p]+[42]);se[p]=sorted(se.get(p,[])+[42])
test('A','reintroduce H08 P009 old @42 false break',A,lambda t,sd,spp,se,vpt:metadata_changed(sd,spp,se,vpt))
# B old RELATED_HOUR_06 P043 @49
def B(t,sd,spp,se,vpt):p='PASSION24.TEXT.RELATED_HOUR_06.BODY.P043';spp[p]['breaks']=[49];vpt['local_breaks'][p]=[49];se[p]=[49]
test('B','reintroduce RELATED_HOUR_06 P043 old @49 false break',B,lambda t,sd,spp,se,vpt:metadata_changed(sd,spp,se,vpt))
# C remove valid H08 P008 break
def C(t,sd,spp,se,vpt):p='PASSION24.HOUR.08.P008';spp[p]['breaks']=[];vpt['local_breaks'].pop(p,None);se.pop(p,None)
test('C','remove valid H08 P008 break',C,lambda t,sd,spp,se,vpt:metadata_changed(sd,spp,se,vpt))
# D direct Jesus quote inserted in previously metadata-unmapped raw record + false break
def D(t,sd,spp,se,vpt):p='PASSION24.TEXT.RELATED_HOUR_21.BODY.P066';t[p]=t[p]+' Jésus me dit : «Ma fille, demeure en Moi.» puis je repris mon récit.';spp[p]={'runs':[],'hidden':[],'breaks':[len(t[p])-25]};vpt['local_breaks'][p]=[len(t[p])-25]
test('D','new direct Jesus quote in metadata-unmapped fixture with host continuation',D,lambda t,sd,spp,se,vpt:raw_changed(t))
# E uppercase host continuation after quote, proving no lowercase-only safety assumption
def E(t,sd,spp,se,vpt):p='PASSION24.TEXT.RELATED_HOUR_21.BODY.P066';t[p]=t[p]+' Jésus dit : «Viens.» Ensuite je poursuivis.';spp[p]={'runs':[],'hidden':[],'breaks':[len(t[p])-20]};vpt['local_breaks'][p]=[len(t[p])-20]
test('E','uppercase host continuation after quote',E,lambda t,sd,spp,se,vpt:raw_changed(t))
# F cross-record new quotation continuation
def F(t,sd,spp,se,vpt):a='PASSION24.TEXT.RELATED_HOUR_21.BODY.P066';b='PASSION24.TEXT.RELATED_HOUR_21.BODY.P067';t[a]+=' Jésus dit : «Commence';t[b]='et continue.» '+t[b]
test('F','cross-record quotation continuation',F,lambda t,sd,spp,se,vpt:raw_changed(t))
# G omit raw direct-Jesus metadata
def G(t,sd,spp,se,vpt):sd.pop('PASSION24.TEXT.RELATED_HOUR_21.BODY.P100',None)
test('G','speaker metadata omits approved raw direct-Jesus quote',G,lambda t,sd,spp,se,vpt:metadata_changed(sd,spp,se,vpt))
# H projection correct but topology stale
def H(t,sd,spp,se,vpt):vpt['local_breaks']['PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P057']=[78]
test('H','projection correct but topology stale',H,lambda t,sd,spp,se,vpt:not parity(spp,vpt) or metadata_changed(sd,spp,se,vpt))
# I move P073 boundary off host-sentence boundary
def I(t,sd,spp,se,vpt):p='PASSION24.TEXT.RELATED_HOUR_21.BODY.P073';spp[p]['breaks']=[270];vpt['local_breaks'][p]=[270];se[p]=[270]
test('I','move approved P073 break to non-host-sentence offset',I,lambda t,sd,spp,se,vpt:metadata_changed(sd,spp,se,vpt))
# J canonical text altered while claiming topology only
def J(t,sd,spp,se,vpt):p='PASSION24.TEXT.RELATED_HOUR_21.BODY.P073';t[p]=t[p].replace('Ensuite','Puis',1)
test('J','alter canonical text while claiming topology-only repair',J,lambda t,sd,spp,se,vpt:raw_changed(t))
sm={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)};OUT.write_text(json.dumps({'schema':'L24H_V101133_GLOBAL_RAW_QUOTE_MUTATION_TESTS_V1','version':'v101.133','summary':sm,'rows':rows},ensure_ascii=False,indent=2)+'\n');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
