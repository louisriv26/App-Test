#!/usr/bin/env python3
import json,re,sys,hashlib
from pathlib import Path
BASE=Path(sys.argv[1]);CAND=Path(sys.argv[2]);OUT=Path(sys.argv[3]);OUT.parent.mkdir(parents=True,exist_ok=True)
def text(p):return Path(p).read_text(encoding='utf-8')
def raw(s,n):
 m=re.search(rf'const\s+{re.escape(n)}\s*=\s*',s);assert m,n;st=m.end()
 try: _,e=json.JSONDecoder().raw_decode(s[st:]); return s[st:st+e]
 except json.JSONDecodeError:return s[st:s.index(';',st)]
def add(rs,n,ok,d=None):rs.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
b=text(BASE);c=text(CAND);rs=[]
add(rs,'baseline_identity',"const APP_VERSION = 'v101.132';" in b and "const APP_EVIDENCE_STAGE = 'DEEP_FOUR_PASS_RELEASE_ENGINEERING_RECONCILIATION_R1';" in b)
add(rs,'candidate_identity',"const APP_VERSION = 'v101.133';" in c and "const APP_EVIDENCE_STAGE = 'VISUAL_BOUNDARY_LEADING_WHITESPACE_ALIGNMENT_REPAIR_R1';" in c)
for n in ['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','SPEECH_END_VISUAL_BREAKS','SPEECH_CROSS_RECORD_VISUAL_BREAKS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY','SPEECH_CROSS_RECORD_OPENING_WRAPPER_SUPPRESSIONS']:
 add(rs,'protected_'+n+'_identical',raw(b,n)==raw(c,n))
add(rs,'dedicated_css_present','.visual-boundary-separator-space' in c)
add(rs,'speech_path_arm_present','V101133_SPEECH_BOUNDARY_SPACE_ARM' in c)
add(rs,'ldc_path_arm_present','V101133_LDC_BOUNDARY_SPACE_ARM' in c)
add(rs,'no_trimStart','.trimStart()' not in c[c.find('function renderQuoteSuppressedChunk'):c.find('function getInternalSubheadingMeta')])
add(rs,'no_global_pre_wrap_removal','white-space: pre-wrap' in c)
add(rs,'html_mirror_identical',text(CAND)==text(CAND.parent/'luisa_24_heures.html'))
bv=json.loads((BASE.parent/'version.json').read_text());cv=json.loads((CAND.parent/'version.json').read_text())
add(rs,'storage_schema_unchanged',bv['storage_schema']==cv['storage_schema'],[bv['storage_schema'],cv['storage_schema']])
add(rs,'personal_snapshot_unchanged',bv['personal_snapshot']==cv['personal_snapshot'],[bv['personal_snapshot'],cv['personal_snapshot']])
add(rs,'ldc_source_bindings_unchanged',all(bv.get(k)==cv.get(k) for k in ['ldc_source_public_version','ldc_source_app_version','ldc_source_package_sha256','ldc_source_alignment_generation','ldc_source_enriched_generation','ldc_source_corpus_manifest_sha256']))
sm={'pass':sum(x['status']=='PASS' for x in rs),'fail':sum(x['status']=='FAIL' for x in rs),'total':len(rs)}
OUT.write_text(json.dumps({'schema':'L24H_V101133_MUTATION_INTEGRITY_V1','version':'v101.133','summary':sm,'rows':rs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
