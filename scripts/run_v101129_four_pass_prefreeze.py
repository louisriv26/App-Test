#!/usr/bin/env python3
from pathlib import Path
import json,csv,hashlib,sys,re

CAND=Path(sys.argv[1]); BASE=Path(sys.argv[2]); EV=Path(sys.argv[3]); EV.mkdir(parents=True,exist_ok=True)
VERSION='v101.129'; STAGE='INTRA_RECORD_QUOTE_HOST_SENTENCE_CONTINUITY_R1'
BASE_SHA='fe6433248c94da3629110976fd190ed0263368ecf9057a437c3d6ef166517c72'; BASE_MEMBERS=486
LEDGER_SHA='c6bf93b6f7af4707f93628ab41dfa02acd89db112a048a8cbd54c0a81acc5341'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ex_raw(txt,name):
    dec=json.JSONDecoder(); marker=f'const {name} = '; i=txt.index(marker)+len(marker)
    try:
        o,e=dec.raw_decode(txt[i:]); return o,txt[i:i+e]
    except json.JSONDecodeError:
        e=txt.index(';',i); return None,txt[i:e]
def add(rows,case,ok,detail=''): rows.append({'case':case,'status':'PASS' if ok else 'FAIL','detail':detail})
def summ(rows): return {'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
H=(CAND/'index.html').read_text(encoding='utf-8'); HM=(CAND/'luisa_24_heures.html').read_text(encoding='utf-8'); B=(BASE/'index.html').read_text(encoding='utf-8')
protected=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','INTERNAL_SUBHEADINGS','SPEECH_DATA','SPEECH_PRESENTATION_ADJUDICATIONS','DISPLAY_SEGMENTS','CONTINUITY_GROUPS','LDC_LIBRARY_FLOW_LAYOUT','LDC_CURRENT_SYNC_AUTHORITY']
mutable=['SPEECH_END_VISUAL_BREAKS','SPEECH_PRESENTATION_PROJECTION','VISIBLE_PARAGRAPH_TOPOLOGY']
# PASS 1
p1=[]
add(p1,'mirrored_html_byte_identical',H==HM,sha(CAND/'index.html'))
add(p1,'version_binding_index',"const APP_VERSION = 'v101.129';" in H)
add(p1,'stage_binding_index',f"const APP_EVIDENCE_STAGE = '{STAGE}';" in H)
v=json.loads((CAND/'version.json').read_text()); m=json.loads((CAND/'manifest.json').read_text()); sw=(CAND/'sw.js').read_text()
add(p1,'version_json_current',v.get('app_version')==VERSION and v.get('build_date')=='2026-09-03',str(v.get('app_version')))
add(p1,'manifest_current',m.get('version')==VERSION,str(m.get('version')))
add(p1,'service_worker_current',sw.startswith('/* v101.129 */') and "const CACHE_NAME = 'luisa-24h-v101-129';" in sw)
add(p1,'ledger_sha_exact',sha(EV/'15_V101129_QUOTE_HOST_TOPOLOGY_MUTATION_LEDGER_FROZEN.csv')==LEDGER_SHA,sha(EV/'15_V101129_QUOTE_HOST_TOPOLOGY_MUTATION_LEDGER_FROZEN.csv'))
ledger=list(csv.DictReader((EV/'15_V101129_QUOTE_HOST_TOPOLOGY_MUTATION_LEDGER_FROZEN.csv').open(encoding='utf-8')))
add(p1,'ledger_exact_8_authorised',len(ledger)==8 and all(x['status']=='FROZEN_AUTHORISED_USER_VALIDATED' for x in ledger),str(len(ledger)))
for n in protected:
    bo,br=ex_raw(B,n); co,cr=ex_raw(H,n); add(p1,'protected_'+n,br==cr,hashlib.sha256(cr.encode()).hexdigest())
for n in mutable:
    bo,br=ex_raw(B,n); co,cr=ex_raw(H,n); add(p1,'authorised_mutable_changed_'+n,br!=cr)
# package manifests self-consistency
hm=json.loads((CAND/'metadata/hash_manifest.json').read_text()); pm=json.loads((CAND/'metadata/package_manifest.json').read_text())
listed={x['path']:x for x in hm['files']}; actual={p.relative_to(CAND).as_posix():p for p in CAND.rglob('*') if p.is_file() and p.relative_to(CAND).as_posix() not in set(hm.get('self_exclusion',[]))}
add(p1,'hash_manifest_path_universe_exact',set(listed)==set(actual),f"listed={len(listed)} actual={len(actual)}")
mis=[]
for rel,p in actual.items():
    x=listed.get(rel)
    if not x or x['size']!=p.stat().st_size or x['sha256']!=sha(p): mis.append(rel)
add(p1,'hash_manifest_bytes_exact',not mis,','.join(mis[:10]))
add(p1,'package_manifest_count_exact',pm.get('file_count')==len(actual),f"{pm.get('file_count')} vs {len(actual)}")
# tooling inventory exists
inv=json.loads((CAND/'metadata/current_tooling_inventory.json').read_text())
missing=[x for x in inv.get('current_tools',[]) if not (CAND/x).is_file()]
add(p1,'current_tooling_inventory_resolves',not missing,','.join(missing))

# PASS 2: all runtime/evidence matrices must be fresh-green.
gate_files=[
'20_INTRA_RECORD_QUOTE_HOST_SYNTAX_MATRIX.json','21_INTRA_RECORD_QUOTE_HOST_CONTINUITY_GEOMETRY_MATRIX.json','22_VALID_BREAK_CONTROL_MATRIX.json','23_PROJECTION_TOPOLOGY_PARITY_MATRIX.json','24_SPEAKER_CONSERVATION_MATRIX.json','25_RENDERED_TEXT_CONSERVATION_MATRIX.json','26_USER_STATE_TOPOLOGY_MATRIX.json','26B_USER_STATE_ANCHOR_APPLE_SELECTION_MATRIX.json','27_REPERES_PRESENTATION_MATRIX.json','28_MUTATION_DETECTION_MATRIX.json','28B_INDEPENDENT_QUOTE_HOST_PROBE.json','29_STRICT_CROSS_RECORD_GLYPH_FLOW_MATRIX.json','30_LEGACY_CONTINUITY_MATRIX.json','31_MEDITEE_V101128_REGRESSION_MATRIX.json','31B_MEDITEE_RESPONSIVE_REGRESSION_MATRIX.json','32_HOUR24_REGRESSION_MATRIX.json','33_HELP_REGRESSION_MATRIX.json','34_PRESENTATION_REGRESSION_MATRIX.json','35_BROAD_RUNTIME_MATRIX.json','36_SERVICE_WORKER_MATRIX.json']
p2=[]
for fn in gate_files:
    p=EV/fn
    if not p.exists(): add(p2,fn,False,'missing'); continue
    d=json.loads(p.read_text())
    s=d.get('summary',{}) if isinstance(d.get('summary'),dict) else {}
    fail=s.get('fail',d.get('fail'))
    passed=s.get('pass',d.get('pass'))
    total=s.get('total',d.get('total',len(d.get('rows',[])) if isinstance(d.get('rows'),list) else None))
    add(p2,fn,fail==0 and passed is not None and (total is None or passed==total),f"pass={passed} fail={fail} total={total}")

# PASS 3: active report line by line with direct current evidence.
report=CAND/'reports/QUOTE_HOST_SENTENCE_CONTINUITY.md'; lines=report.read_text(encoding='utf-8').splitlines(); rec=[]
for i,line in enumerate(lines,1):
    if not line.strip(): continue
    ok=False; evidence=''
    if line.startswith('# v101.129'):
        ok=(VERSION in line and STAGE in v.get('release_scope','') or VERSION in line); evidence='index.html APP_VERSION + version.json'
    elif line.startswith('- Predecessor:'):
        ok=('v101.128' in line and BASE_SHA in line and '486 members' in line); evidence='01_V101128_BASELINE_BINDING.json + immutable predecessor'
    elif line.startswith('- Frozen mutation ledger SHA-256:'):
        ok=(LEDGER_SHA in line and sha(EV/'15_V101129_QUOTE_HOST_TOPOLOGY_MUTATION_LEDGER_FROZEN.csv')==LEDGER_SHA); evidence='15 ledger + 16 SHA sidecar'
    elif line.startswith('- User-authorised topology operations:'):
        reloc=sum(bool(x['new_break_offset']) for x in ledger); rem=len(ledger)-reloc; ok=(len(ledger)==8 and reloc==3 and rem==5 and '**8** = 3 relocations + 5 removals' in line); evidence='frozen ledger rows'
    elif line.startswith('- Governing rule:'):
        d=json.loads((EV/'20_INTRA_RECORD_QUOTE_HOST_SYNTAX_MATRIX.json').read_text()); ok=d['summary']['fail']==0; evidence='20 host syntax + 21 geometry'
    elif line.startswith('- Canonical text changes:'):
        bo,br=ex_raw(B,'CORPUS');co,cr=ex_raw(H,'CORPUS');bs,bss=ex_raw(B,'SPEECH_DATA');cs,css=ex_raw(H,'SPEECH_DATA'); anchor=json.loads((EV/'26B_USER_STATE_ANCHOR_APPLE_SELECTION_MATRIX.json').read_text()); ok=(br==cr and bss==css and anchor['summary']['fail']==0); evidence='protected declarations + 24/25/26B matrices'
    elif line.startswith('- Authorised mutable layers:'):
        ok=all(ex_raw(B,n)[1]!=ex_raw(H,n)[1] for n in mutable); evidence='Pass1 declaration diff'
    elif line.startswith('- Relocated host-sentence breaks'):
        se=ex_raw(H,'SPEECH_END_VISUAL_BREAKS')[0]; ok=all(x not in se.get(pid,[]) for pid,x in [('PASSION24.HOUR.08.P009',93),('PASSION24.HOUR.08.P009',210),('PASSION24.HOUR.08.P015',145)]); evidence='current SPEECH_END_VISUAL_BREAKS + 20 matrix'
    elif line.startswith('- Physical-device/PWA/offline/screen-reader/live-origin'):
        ok=('remains external' in line and bool(v.get('external_open_gates')) and 'NOT_TESTED' in v.get('real_device_status','')); evidence='version.json external_open_gates / real_device_status'
    rec.append({'line':i,'claim':line,'evidence':evidence,'status':'PASS' if ok else 'FAIL'})
with (EV/'38_ACTIVE_REPORT_LINE_RECONCILIATION.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['line','claim','evidence','status']);w.writeheader();w.writerows(rec)
p3=[{'case':f"report_line_{x['line']}",'status':x['status'],'detail':x['claim']} for x in rec]

# PASS 4: stale/contradiction checks.
p4=[]
add(p4,'no_pending_validation_file_in_current_root',not (EV/'15_PROPOSED_MUTATION_LEDGER_PENDING_USER_VALIDATION.csv').exists())
add(p4,'m1_report_authority_current','BLOCKED_PENDING' not in (EV/'14_M1_FIXED_POINT_REPORT.md').read_text() and 'FROZEN — 8 USER-VALIDATED' in (EV/'14_M1_FIXED_POINT_REPORT.md').read_text())
stage_lock=json.loads((EV/'00_CURRENT_STAGE_LOCK.json').read_text()); add(p4,'stage_lock_authority_current',stage_lock.get('mutation_authority')=='FROZEN_8_USER_VALIDATED_TOPOLOGY_OPERATIONS' and stage_lock.get('status')=='M4_PREFREEZE_PASS_READY_FOR_DETERMINISTIC_FREEZE')
# old/new break exactness in all three current authorities
SE=ex_raw(H,'SPEECH_END_VISUAL_BREAKS')[0]; SPP=ex_raw(H,'SPEECH_PRESENTATION_PROJECTION')[0]; VPT=ex_raw(H,'VISIBLE_PARAGRAPH_TOPOLOGY')[0]
ops=[('PASSION24.HOUR.08.P009',42,93),('PASSION24.HOUR.08.P009',140,210),('PASSION24.HOUR.08.P010',49,None),('PASSION24.HOUR.08.P015',50,145),('PASSION24.HOUR.21.P020',69,None),('PASSION24.HOUR.21.P025',118,None),('PASSION24.TEXT.RELATED_HOUR_06.BODY.P043',49,None),('PASSION24.TEXT.RELATED_HOUR_06.BODY.P058',49,None)]
for i,(pid,old,new) in enumerate(ops,1):
    ok=old not in SE.get(pid,[]) and old not in SPP.get(pid,{}).get('breaks',[]) and old not in VPT.get('local_breaks',{}).get(pid,[])
    if new is not None: ok=ok and new not in SE.get(pid,[]) and new in SPP[pid].get('breaks',[]) and new in VPT['local_breaks'].get(pid,[])
    add(p4,f'OP{i:02d}_no_stale_break_authority',ok,repr((pid,old,new)))
# current bindings no false current predecessor
add(p4,'no_stale_app_version_binding',"const APP_VERSION = 'v101.128';" not in H)
add(p4,'no_stale_stage_binding',"const APP_EVIDENCE_STAGE = 'MEDITEE_RECOVERY_ACCESS_AND_SINGLE_STATE_SYNC_R1';" not in H)
add(p4,'no_stale_sw_cache',"const CACHE_NAME = 'luisa-24h-v101-128';" not in sw)
add(p4,'active_report_inventory_current',json.loads((CAND/'metadata/active_report_inventory.json').read_text()).get('source_reports')==['reports/QUOTE_HOST_SENTENCE_CONTINUITY.md'])
add(p4,'external_gate_overclaim_absent','NOT_TESTED' in v.get('real_device_status','') and v.get('overall_release_status')=='LIMITED_PASS_STATIC_PENDING_FINAL_REOPEN_AUDIT')
# current tooling names resolve + independent probe present
add(p4,'independent_probe_current_tooling','scripts/run_v101129_independent_quote_host_probe.py' in inv.get('current_tools',[]) and (CAND/'scripts/run_v101129_independent_quote_host_probe.py').exists())
# historical references are allowed; ensure explicit lineage fields distinguish them.
lin=json.loads((CAND/'metadata/current_evidence_lineage.json').read_text())
add(p4,'predecessor_reference_explicitly_classified',lin.get('predecessor_24h',{}).get('version')=='v101.128' and lin.get('current_evidence_root')=='evidence/v101129')

# stale scan JSON
stale={'schema':'L24H_V101129_STALE_CONTRADICTION_SCAN_V1','version':VERSION,'stage':STAGE,'summary':summ(p4),'checks':p4,'historical_reference_policy':'Explicit v101.128 predecessor/historical lineage references are valid and are not treated as stale current claims.'}
(EV/'39_STALE_CONTRADICTION_SCAN.json').write_text(json.dumps(stale,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# four-pass report
allpasses=[('Pass 1 — files vs build script',p1),('Pass 2 — runtime/package behaviour',p2),('Pass 3 — active report line-by-line',p3),('Pass 4 — stale/contradiction/obsolete evidence',p4)]
lines=['# v101.129 — Four-pass prefreeze audit','',f'Candidate: `{CAND}`','',f'Predecessor: immutable `v101.128` / `{BASE_SHA}` / {BASE_MEMBERS} members.','']
overall=True
for title,rows in allpasses:
    s=summ(rows); overall=overall and s['fail']==0
    lines += [f'## {title}','',f"**Result: {'PASS' if s['fail']==0 else 'FAIL'} — {s['pass']}/{s['total']} checks**",'']
    for r in rows:
        lines.append(f"- `{r['status']}` — {r['case']}" + (f" — {r['detail']}" if r.get('detail') else ''))
    lines.append('')
lines += ['## Decision','',f"**PREFREEZE FOUR-PASS: {'PASS' if overall else 'FAIL'}**",'', 'This PASS is static/prefreeze only. Deterministic Build A/B, immutable ZIP reopen, independent reopened-ZIP audit, final meta-audit and external physical-device gates remain downstream.']
(EV/'37_FOUR_PASS_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'pass1':summ(p1),'pass2':summ(p2),'pass3':summ(p3),'pass4':summ(p4),'overall':'PASS' if overall else 'FAIL'},ensure_ascii=False,indent=2))
if not overall: raise SystemExit(2)
