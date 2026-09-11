#!/usr/bin/env python3
import json,re,sys,hashlib
from pathlib import Path
BASE=Path(sys.argv[1]);CAND=Path(sys.argv[2]);OUT=Path(sys.argv[3]);OUT.parent.mkdir(parents=True,exist_ok=True)
STAGE='BOUNDARY_UNIVERSE_EVIDENCE_REPRODUCIBILITY_RECONCILIATION_R1'
def txt(p):return Path(p).read_text(encoding='utf-8')
def raw(s,n):
 m=re.search(rf'const\s+{re.escape(n)}\s*=\s*',s);assert m,n;st=m.end()
 try: _,e=json.JSONDecoder().raw_decode(s[st:]);return s[st:st+e]
 except json.JSONDecodeError:return s[st:s.index(';',st)]
def add(rs,n,ok,d=None):rs.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
b=txt(BASE);c=txt(CAND);rs=[]
add(rs,'baseline_identity',"const APP_VERSION = 'v101.133';" in b and "const APP_EVIDENCE_STAGE = 'VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_R1';" in b)
add(rs,'candidate_identity',"const APP_VERSION = 'v101.134';" in c and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in c)
# Exact full HTML equality after normalising only authorised release-identity fields.
def norm(s,base):
 if base:
  s=s.replace("const APP_VERSION = 'v101.133';","const APP_VERSION = '__VERSION__';",1)
  s=s.replace("const APP_EVIDENCE_STAGE = 'VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_R1';","const APP_EVIDENCE_STAGE = '__STAGE__';",1)
  s=s.replace("const BUILD_DATE = '2026-09-04'; // v101.133 / visual-boundary leading-whitespace alignment repair; no canonical text mutation","const BUILD_DATE = '__DATE__'; // __RELEASE_COMMENT__",1)
 else:
  s=s.replace("const APP_VERSION = 'v101.134';","const APP_VERSION = '__VERSION__';",1)
  s=s.replace(f"const APP_EVIDENCE_STAGE = '{STAGE}';","const APP_EVIDENCE_STAGE = '__STAGE__';",1)
  s=s.replace("const BUILD_DATE = '2026-09-04'; // v101.134 / release-engineering evidence-reproducibility reconciliation; v101.133 renderer behavior unchanged","const BUILD_DATE = '__DATE__'; // __RELEASE_COMMENT__",1)
 return s
add(rs,'full_app_html_functionally_identical_after_release_identity_normalisation',norm(b,True)==norm(c,False))
for n in ['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS']:
 add(rs,'protected_'+n+'_identical',raw(b,n)==raw(c,n))
for marker in ['V101133_SPEECH_BOUNDARY_SPACE_ARM','V101133_LDC_BOUNDARY_SPACE_ARM','.visual-boundary-separator-space{font-size:0!important;line-height:0!important;}']:
 add(rs,'renderer_marker_preserved_'+marker[:28],marker in b and marker in c)
add(rs,'html_mirror_identical',txt(CAND)==txt(CAND.parent/'luisa_24_heures.html'))
bv=json.loads((BASE.parent/'version.json').read_text());cv=json.loads((CAND.parent/'version.json').read_text())
add(rs,'storage_schema_unchanged',bv['storage_schema']==cv['storage_schema'],[bv['storage_schema'],cv['storage_schema']])
add(rs,'personal_snapshot_unchanged',bv['personal_snapshot']==cv['personal_snapshot'],[bv['personal_snapshot'],cv['personal_snapshot']])
keys=['ldc_source_public_version','ldc_source_app_version','ldc_source_package_sha256','ldc_source_alignment_generation','ldc_source_enriched_generation','ldc_source_corpus_manifest_sha256']
add(rs,'ldc_source_bindings_unchanged',all(bv.get(k)==cv.get(k) for k in keys))
add(rs,'release_scope_declared_nonfunctional',cv.get('release_scope','').startswith('Release-engineering-only successor'))
sm={'pass':sum(x['status']=='PASS' for x in rs),'fail':sum(x['status']=='FAIL' for x in rs),'total':len(rs)}
OUT.write_text(json.dumps({'schema':'L24H_V101134_RELEASE_INTEGRITY_V1','version':'v101.134','summary':sm,'rows':rs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
