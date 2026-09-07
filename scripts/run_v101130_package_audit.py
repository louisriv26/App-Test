#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,zipfile,csv,sys,re,tempfile,shutil
VERSION='v101.130'; STAGE='FOUR_PASS_FINAL_PACKAGE_METADATA_EVIDENCE_RECONCILIATION_R1'; BASE_SHA='8160f3133eb6d486c2109ea34911dfb13382c08d9f03883e2117cab90f01f6f0'; BASE_MEMBERS=551
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY','SPEECH_END_VISUAL_BREAKS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def raw(text,n):
 m=f'const {n} = ';i=text.index(m)+len(m)
 try:
  o,e=json.JSONDecoder().raw_decode(text[i:]);return text[i:i+e]
 except json.JSONDecodeError:
  e=text.index(';',i);return text[i:e]
def row(rows,name,ok,detail=''): rows.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
def dump(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
C=Path(sys.argv[1]); BZ=Path(sys.argv[2]); OUT=Path(sys.argv[3]); OUT.mkdir(parents=True,exist_ok=True)
if sha(BZ)!=BASE_SHA:raise SystemExit('baseline SHA mismatch')
with zipfile.ZipFile(BZ) as z:
 if len(z.infolist())!=BASE_MEMBERS or z.testzip() is not None:raise SystemExit('baseline invalid')
 td=Path(tempfile.mkdtemp());z.extractall(td)
base=td
# Pass1
r=[]; h=(C/'index.html').read_text(encoding='utf-8'); hb=(base/'index.html').read_text(encoding='utf-8')
row(r,'html_mirrors',h==(C/'luisa_24_heures.html').read_text(encoding='utf-8'),sha(C/'index.html'))
row(r,'app_version',"const APP_VERSION = 'v101.130';" in h)
row(r,'stage',f"const APP_EVIDENCE_STAGE = '{STAGE}';" in h)
row(r,'version_json',load(C/'version.json').get('app_version')==VERSION)
row(r,'release_status_nonpending',load(C/'version.json').get('overall_release_status')=='LIMITED_PASS_STATIC__EXTERNAL_VALIDATION_OPEN')
row(r,'manifest_version',load(C/'manifest.json').get('version')==VERSION)
row(r,'sw_cache',"const CACHE_NAME = 'luisa-24h-v101-130';" in (C/'sw.js').read_text())
for n in PROTECTED:row(r,'protected_'+n,raw(h,n)==raw(hb,n),hashlib.sha256(raw(h,n).encode()).hexdigest())
# manifests
hm=load(C/'metadata/hash_manifest.json'); pm=load(C/'metadata/package_manifest.json');ex=set(hm['self_exclusion'])
actual={p.relative_to(C).as_posix():p for p in C.rglob('*') if p.is_file() and p.relative_to(C).as_posix() not in ex}
listed={x['path']:x for x in hm['files']}
row(r,'hash_manifest_path_universe',set(actual)==set(listed),f'{len(actual)} vs {len(listed)}')
row(r,'hash_manifest_bytes',all(x['size']==actual[k].stat().st_size and x['sha256']==sha(actual[k]) for k,x in listed.items()) if set(actual)==set(listed) else False)
row(r,'package_manifest_count',pm['file_count']==len(actual),f"{pm['file_count']} vs {len(actual)}")
# exact current report root
root_reports=sorted(p.name for p in (C/'reports').iterdir() if p.is_file())
row(r,'current_report_root_exact',root_reports==['FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md'],str(root_reports))
ari=load(C/'metadata/active_report_inventory.json');row(r,'active_report_inventory_exact',ari.get('source_reports')==['reports/FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md'])
# current metadata identities
for rel in ['active_report_inventory.json','build_provenance.json','current_evidence_lineage.json','current_tooling_inventory.json','full_build_overlay_manifest.json','release_evidence_lifecycle.json']:
 d=load(C/'metadata'/rel);row(r,'metadata_current_'+rel,d.get('version')==VERSION and d.get('stage')==STAGE,str((d.get('version'),d.get('stage'))))
row(r,'scope_authority_current',(C/'metadata/scope_escalation_authority.md').read_text().startswith('# v101.130 Scope / Mutation Authority'))
# overlay diff consistency
ov=load(C/'metadata/full_build_overlay_manifest.json'); a={p.relative_to(base).as_posix():p for p in base.rglob('*') if p.is_file()}; b={p.relative_to(C).as_posix():p for p in C.rglob('*') if p.is_file()}
calc_removed=sorted(set(a)-set(b)); calc_changed=sorted([x for x,p in b.items() if x not in a or sha(p)!=sha(a[x])]);
# manifests are generated and overlay manifest describes itself; compare expected with explicit exclusions for self-excluding manifests.
for x in ['metadata/hash_manifest.json','metadata/package_manifest.json']:
 if x in calc_changed: calc_changed.remove(x)
claimed=[x for x in ov['changed_or_added'] if x not in ('metadata/hash_manifest.json','metadata/package_manifest.json')]
row(r,'overlay_removed_exact',calc_removed==ov['removed'],f'{len(calc_removed)}')
row(r,'overlay_changed_exact',calc_changed==claimed,f'{len(calc_changed)} vs {len(claimed)}')
dump(OUT/'PASS1_FILES_VS_BUILD.json',{'version':VERSION,'stage':STAGE,'summary':{'pass':sum(x['status']=='PASS' for x in r),'fail':sum(x['status']=='FAIL' for x in r),'total':len(r)},'rows':r})
# Pass3 active report line by line
report=(C/'reports/FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md').read_text().splitlines(); rr=[]
for no,line in enumerate(report,1):
 if not line.strip():continue
 ok=False;ev=''
 if line.startswith('# v101.130'):ok=True;ev='report heading/current identity'
 elif 'Predecessor:' in line:ok=(BASE_SHA in line and '551 members' in line);ev='baseline exact'
 elif 'Trigger:' in line:ok=True;ev='fresh audit findings bind separately'
 elif 'Functional change' in line:ok=all(raw(h,n)==raw(hb,n) for n in PROTECTED);ev='protected authority byte parity'
 elif 'Canonical devotional text changes' in line:ok=all(raw(h,n)==raw(hb,n) for n in PROTECTED);ev='protected authority byte parity'
 elif 'Repair A:' in line:ok=(root_reports==['FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md']);ev='reports root + historical dirs'
 elif 'Repair B:' in line:ok=(load(C/'metadata/full_build_overlay_manifest.json')['version']==VERSION and (C/'metadata/historical/v101128/full_build_overlay_manifest.json').exists() and (C/'metadata/historical/v101127/scope_escalation_authority.md').exists());ev='metadata current/historical paths'
 elif 'Repair C:' in line:ok=('PENDING_FINAL_REOPEN' not in (C/'version.json').read_text() and 'external' in (C/'metadata/release_evidence_lifecycle.json').read_text().lower());ev='version/lifecycle'
 elif 'eight user-validated' in line:ok=(raw(h,'SPEECH_END_VISUAL_BREAKS')==raw(hb,'SPEECH_END_VISUAL_BREAKS') and raw(h,'SPEECH_PRESENTATION_PROJECTION')==raw(hb,'SPEECH_PRESENTATION_PROJECTION') and raw(h,'VISIBLE_PARAGRAPH_TOPOLOGY')==raw(hb,'VISIBLE_PARAGRAPH_TOPOLOGY'));ev='v101129 topology parity'
 elif 'Physical-device' in line:ok=('NOT_TESTED' in (C/'version.json').read_text());ev='version external gates'
 rr.append({'path':'reports/FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md','line':no,'line_text':line,'status':'PASS' if ok else 'FAIL','evidence':ev})
with (OUT/'PASS3_ACTIVE_REPORT_LINE_RECONCILIATION.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rr[0].keys());w.writeheader();w.writerows(rr)
dump(OUT/'PASS3_SUMMARY.json',{'summary':{'pass':sum(x['status']=='PASS' for x in rr),'fail':sum(x['status']=='FAIL' for x in rr),'total':len(rr)}})
# Pass4 stale/contradiction scan
s=[]
row(s,'no_pending_release_status','PENDING_FINAL_REOPEN' not in (C/'version.json').read_text())
row(s,'only_current_root_report',root_reports==['FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md'])
row(s,'old_root_report_v101125_absent',not any((C/'reports'/x).exists() for x in ['build_script_vs_files_audit.md','current_metadata_semantic_consistency.md','four_pass_deep_audit.md','report_claims_vs_evidence_audit.md']))
row(s,'historical_v101125_present',(C/'reports/historical/v101125/build_script_vs_files_audit.md').exists())
row(s,'historical_v101126_present',(C/'reports/historical/v101126/DUAL_SUCCESSOR_MUTATION_REPORT.md').exists())
row(s,'historical_v101127_present',(C/'reports/historical/v101127/CONTINUITY_GLYPH_FLOW_REGRESSION_REPAIR.md').exists())
row(s,'historical_v101128_present',(C/'reports/historical/v101128/MEDITEE_RECOVERY_ACCESS.md').exists())
row(s,'historical_v101129_present',(C/'reports/historical/v101129/QUOTE_HOST_SENTENCE_CONTINUITY.md').exists())
row(s,'current_scope_not_v101127',not (C/'metadata/scope_escalation_authority.md').read_text().startswith('# v101.127'))
row(s,'current_overlay_not_v101128',load(C/'metadata/full_build_overlay_manifest.json').get('version')==VERSION)
row(s,'historical_old_metadata_present',(C/'metadata/historical/v101127/scope_escalation_authority.md').exists() and (C/'metadata/historical/v101128/full_build_overlay_manifest.json').exists())
row(s,'active_inventory_no_old_report',all('v101.12' not in x for x in ari.get('source_reports',[])))
row(s,'current_evidence_root_v101130',load(C/'metadata/current_evidence_lineage.json').get('current_evidence_root')=='evidence/v101130')
row(s,'no_fail_in_current_report','FAIL' not in (C/'reports/FOUR_PASS_FINAL_PACKAGE_RECONCILIATION.md').read_text())
row(s,'external_gate_not_overclaimed','NOT_TESTED' in (C/'version.json').read_text())
dump(OUT/'PASS4_STALE_CONTRADICTION_SCAN.json',{'version':VERSION,'stage':STAGE,'summary':{'pass':sum(x['status']=='PASS' for x in s),'fail':sum(x['status']=='FAIL' for x in s),'total':len(s)},'rows':s})
shutil.rmtree(td)
print(json.dumps({'pass1':load(OUT/'PASS1_FILES_VS_BUILD.json')['summary'],'pass3':load(OUT/'PASS3_SUMMARY.json')['summary'],'pass4':load(OUT/'PASS4_STALE_CONTRADICTION_SCAN.json')['summary']},indent=2))
