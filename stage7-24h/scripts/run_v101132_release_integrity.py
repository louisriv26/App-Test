#!/usr/bin/env python3
from pathlib import Path
import sys,json,re,hashlib
BASE=Path(sys.argv[1]); CAND=Path(sys.argv[2]); OUT=Path(sys.argv[3]); OUT.parent.mkdir(parents=True,exist_ok=True)
def text(p): return Path(p).read_text(encoding='utf-8')
def obj(s,n):
 m=re.search(rf'const\s+{re.escape(n)}\s*=\s*',s); o,_=json.JSONDecoder().raw_decode(s[m.end():]); return o
def raw(s,n):
 m=re.search(rf'const\s+{re.escape(n)}\s*=\s*',s); st=m.end()
 try:
  _,e=json.JSONDecoder().raw_decode(s[st:]); return s[st:st+e]
 except json.JSONDecodeError:
  en=s.index(';',st); return s[st:en]
def add(rows,n,ok,d=None): rows.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
bs=text(BASE); cs=text(CAND); rows=[]
add(rows,'predecessor_identity',"const APP_VERSION = 'v101.131';" in bs and "const APP_EVIDENCE_STAGE = 'GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR_R1';" in bs)
add(rows,'candidate_identity',"const APP_VERSION = 'v101.132';" in cs and "const APP_EVIDENCE_STAGE = 'DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION_R1';" in cs)
raw_names=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY']
for n in raw_names: add(rows,'protected_'+n+'_identical',raw(bs,n)==raw(cs,n))
func_names=['SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_END_VISUAL_BREAKS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY']
for n in func_names: add(rows,'functional_'+n+'_identical',raw(bs,n)==raw(cs,n))
# Normalize only release identity/comment; everything else in app HTML must be byte-identical.
norm=cs.replace("const APP_VERSION = 'v101.132';","const APP_VERSION = 'v101.131';").replace("const APP_EVIDENCE_STAGE = 'DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION_R1';","const APP_EVIDENCE_STAGE = 'GLOBAL_RAW_QUOTE_HOST_SENTENCE_SUCCESSOR_R1';").replace("const BUILD_DATE = '2026-09-03'; // v101.132 / deep four-pass release-engineering reconciliation; no functional or canonical text mutation","const BUILD_DATE = '2026-09-03'; // v101.131 / global raw-quote host-sentence successor; no canonical text mutation")
add(rows,'html_diff_release_identity_only',norm==bs)
add(rows,'candidate_html_mirror_identical',text(CAND)==text(CAND.parent/'luisa_24_heures.html'))
bv=json.loads((BASE.parent/'version.json').read_text());cv=json.loads((CAND.parent/'version.json').read_text())
add(rows,'storage_schema_unchanged',bv.get('storage_schema')==cv.get('storage_schema'),[bv.get('storage_schema'),cv.get('storage_schema')])
add(rows,'personal_snapshot_unchanged',bv.get('personal_snapshot')==cv.get('personal_snapshot'),[bv.get('personal_snapshot'),cv.get('personal_snapshot')])
add(rows,'ldc_source_bindings_unchanged',all(bv.get(k)==cv.get(k) for k in ['ldc_source_public_version','ldc_source_app_version','ldc_source_package_sha256','ldc_source_alignment_generation','ldc_source_enriched_generation','ldc_source_corpus_manifest_sha256']))
bm=json.loads((BASE.parent/'manifest.json').read_text());cm=json.loads((CAND.parent/'manifest.json').read_text())
add(rows,'manifest_functional_contract_unchanged',all(bm.get(k)==cm.get(k) for k in ['name','short_name','start_url','display','orientation','scope','id','icons']))
sm={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
OUT.write_text(json.dumps({'schema':'L24H_V101132_RELEASE_INTEGRITY_V1','version':'v101.132','summary':sm,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
