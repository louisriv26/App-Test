#!/usr/bin/env python3
from pathlib import Path
import zipfile,hashlib,json,tempfile,shutil,sys,re
EXPECTED_VERSION='v101.130'; EXPECTED_STAGE='FOUR_PASS_FINAL_PACKAGE_METADATA_EVIDENCE_RECONCILIATION_R1'; BASE_SHA='8160f3133eb6d486c2109ea34911dfb13382c08d9f03883e2117cab90f01f6f0'
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY','SPEECH_END_VISUAL_BREAKS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(t,n):
 m=f'const {n} = ';i=t.index(m)+len(m)
 try:
  o,e=json.JSONDecoder().raw_decode(t[i:]);return t[i:i+e]
 except json.JSONDecodeError:
  e=t.index(';',i);return t[i:e]
def add(a,n,ok,d=''):a.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
Z=Path(sys.argv[1]);BASE=Path(sys.argv[2]);OUT=Path(sys.argv[3]); expected_sha=sys.argv[4]
r=[];add(r,'zip_sha',sha(Z)==expected_sha,sha(Z))
with zipfile.ZipFile(Z) as z:
 add(r,'zip_integrity',z.testzip() is None); names=z.namelist();add(r,'no_duplicate_paths',len(names)==len(set(names)),len(names));td=Path(tempfile.mkdtemp());z.extractall(td)
with zipfile.ZipFile(BASE) as z: btd=Path(tempfile.mkdtemp());z.extractall(btd)
h=(td/'index.html').read_text(encoding='utf-8');hb=(btd/'index.html').read_text(encoding='utf-8')
add(r,'html_mirrors',h==(td/'luisa_24_heures.html').read_text(encoding='utf-8'))
add(r,'version_binding',"const APP_VERSION = 'v101.130';" in h)
add(r,'stage_binding',f"const APP_EVIDENCE_STAGE = '{EXPECTED_STAGE}';" in h)
for n in PROTECTED:add(r,'protected_'+n,raw(h,n)==raw(hb,n))
v=json.loads((td/'version.json').read_text());add(r,'release_nonpending',v.get('overall_release_status')=='LIMITED_PASS_STATIC__EXTERNAL_VALIDATION_OPEN');add(r,'external_not_tested','NOT_TESTED' in v.get('real_device_status',''))
root_reports=sorted(p.name for p in (td/'reports').iterdir() if p.is_file());add(r,'report_root_exact',root_reports==['FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md'],str(root_reports))
ari=json.loads((td/'metadata/active_report_inventory.json').read_text());add(r,'active_report_exact',ari.get('source_reports')==['reports/FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md'])
add(r,'scope_current',(td/'metadata/scope_escalation_authority.md').read_text().startswith('# v101.130'))
add(r,'overlay_current',json.loads((td/'metadata/full_build_overlay_manifest.json').read_text()).get('version')=='v101.130')
add(r,'old_metadata_archived',(td/'metadata/historical/v101127/scope_escalation_authority.md').exists() and (td/'metadata/historical/v101128/full_build_overlay_manifest.json').exists())
add(r,'old_reports_archived',all((td/f'reports/historical/{ver}/{fn}').exists() for ver,fn in [('v101126','DUAL_SUCCESSOR_MUTATION_REPORT.md'),('v101127','CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR.md'),('v101128','MEDITEE_RECOVERY_ACCESS.md'),('v101129','QUOTE_HOST_SENTENCE_CONTINUITY.md')]))
# manifests directly
hm=json.loads((td/'metadata/hash_manifest.json').read_text());ex=set(hm['self_exclusion']);actual={p.relative_to(td).as_posix():p for p in td.rglob('*') if p.is_file() and p.relative_to(td).as_posix() not in ex};listed={x['path']:x for x in hm['files']};add(r,'manifest_paths',set(actual)==set(listed));add(r,'manifest_hashes',all(x['sha256']==sha(actual[k]) and x['size']==actual[k].stat().st_size for k,x in listed.items()) if set(actual)==set(listed) else False)
obj={'schema':'L24H_V101130_INDEPENDENT_REOPEN_AUDIT_V1','zip_sha256':sha(Z),'summary':{'pass':sum(x['status']=='PASS' for x in r),'fail':sum(x['status']=='FAIL' for x in r),'total':len(r)},'rows':r}
OUT.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj['summary']))
shutil.rmtree(td);shutil.rmtree(btd)
