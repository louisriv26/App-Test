#!/usr/bin/env python3
from pathlib import Path
import sys,zipfile,hashlib,json,re,csv,subprocess,tempfile,shutil,os,signal,time
BASE=Path(sys.argv[1]);ROOT=Path(sys.argv[2]);OJ=Path(sys.argv[3]);OM=Path(sys.argv[4])
VER='v101.125';STAGE='FOUR_PASS_EVIDENCE_SCHEMA_AND_DIRECT_REPORT_BINDING_RECONCILIATION_R1';BASE_SHA='15b9fdb66fb07617ac8078fddb3e4076347390252a510c6eeb4b613f4a06d3ac';CACHE='luisa-24h-v101-125'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest(); C=[]
def ck(n,o,d=''):
 status='PASS' if o else 'FAIL';C.append({'check':n,'status':status,'detail':d});print(f'{n}: {status}',flush=True)

def cleanup_audit_browser_processes():
 # Chromium crashpad handlers can daemonize outside the probe process group.
 # This audit runs in isolation; clean only Chromium/crashpad test processes
 # between probes so repeated browser launches remain bounded.
 victims=[]
 try:
  for ent in os.listdir('/proc'):
   if not ent.isdigit() or int(ent)==os.getpid(): continue
   try:
    exe=os.readlink(f'/proc/{ent}/exe')
   except Exception:
    continue
   if exe.endswith('/chromium') or exe.endswith('/chrome_crashpad_handler'):
    victims.append(int(ent))
  for pid in victims:
   try: os.kill(pid,signal.SIGTERM)
   except ProcessLookupError: pass
  if victims: time.sleep(0.25)
  for pid in victims:
   try: os.kill(pid,0); os.kill(pid,signal.SIGKILL)
   except (ProcessLookupError,PermissionError): pass
 except Exception:
  pass

class RunResult:
 def __init__(self,returncode,timed_out=False):self.returncode=returncode;self.timed_out=timed_out

def run(cmd,timeout=75):
 cleanup_audit_browser_processes()
 p=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,text=True,start_new_session=True)
 try:
  p.wait(timeout=timeout)
  rc=p.returncode
  # Kill any descendants that failed to exit with their parent.  Each probe has
  # its own process group, so this cannot touch another audit task.
  try: os.killpg(p.pid,signal.SIGTERM)
  except ProcessLookupError: pass
  time.sleep(0.15)
  cleanup_audit_browser_processes()
  return RunResult(rc,False)
 except subprocess.TimeoutExpired:
  try: os.killpg(p.pid,signal.SIGTERM)
  except ProcessLookupError: pass
  try: p.wait(timeout=3)
  except subprocess.TimeoutExpired:
   try: os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError: pass
   try: p.wait(timeout=3)
   except Exception: pass
  cleanup_audit_browser_processes()
  return RunResult(124,True)
ck('baseline_hash',sha(BASE)==BASE_SHA,sha(BASE));html=(ROOT/'index.html').read_text();html2=(ROOT/'luisa_24_heures.html').read_text();ck('root_twins',html==html2);ck('identity',f"const APP_VERSION = '{VER}';" in html and f"const APP_EVIDENCE_STAGE = '{STAGE}';" in html)
# protected declaration parity and exact continuity delta from current evidence
par=json.loads((ROOT/'evidence/v101125/PROTECTED_DECLARATION_PARITY.json').read_text());ck('protected_14_of_14',par.get('unchanged')==14 and par.get('changed')==0,{'unchanged':par.get('unchanged'),'changed':par.get('changed')})
fp=json.loads((ROOT/'evidence/v101125/FUNCTIONAL_HTML_PARITY.json').read_text());ck('functional_html_parity',fp.get('normalized_equals_baseline') is True and fp.get('showHelp_byte_identical') is True and fp.get('governed_declarations_unchanged')==14,fp)
v=json.loads((ROOT/'version.json').read_text());m=json.loads((ROOT/'manifest.json').read_text());sw=(ROOT/'sw.js').read_text();ck('release_metadata',v['app_version']==VER and m['version']==VER and CACHE in sw and v['storage_schema']==8 and v['personal_snapshot']==5)
# current tools all exist
ct=json.loads((ROOT/'metadata/current_tooling_inventory.json').read_text());ck('current_tools_exist',all((ROOT/x).is_file() for x in ct['current_tools']),len(ct['current_tools']))
# active report universe/line coverage
inv=json.loads((ROOT/'metadata/active_report_inventory.json').read_text());decl=set(inv['source_reports']);actual=set(p.relative_to(ROOT).as_posix() for p in (ROOT/'reports').iterdir() if p.is_file() and p.name!='active_report_line_audit.csv');ck('active_report_inventory_complete',decl==actual,{'declared':len(decl),'actual':len(actual)})
rows=list(csv.DictReader((ROOT/'reports/active_report_line_audit.csv').open(encoding='utf-8-sig')));exp=[]
for rel in sorted(decl):
 for i,line in enumerate((ROOT/rel).read_text(encoding='utf-8-sig').splitlines(),1):
  if line.strip():exp.append((rel,str(i),line))
got={(r['path'],r['line'],r['line_text']) for r in rows};ck('active_line_exact_coverage',got==set(exp) and all(r['status']=='PASS' and r.get('evidence_type') and r.get('evidence_path') and 'line present' not in r.get('evidence_detail','').lower() for r in rows),{'rows':len(rows),'expected':len(exp)})
# Fresh execution isolated from any pre-generated working dir.
td=Path(tempfile.mkdtemp(prefix='v101125_prefreeze_'))
def rr(name,cmd,parser,timeout=75):
 try:
  attempts=[]
  for attempt in (1,2):
   p=run(cmd,timeout);attempts.append({'attempt':attempt,'returncode':p.returncode,'timed_out':p.timed_out})
   if p.returncode==0: break
   if not p.timed_out: break
   time.sleep(0.5)
  ok=(p.returncode==0);detail={'returncode':p.returncode,'attempts':attempts}
  if parser and p.returncode==0:
   try:
    parsed_ok,parsed_detail=parser();detail={'returncode':p.returncode,'attempts':attempts,'parsed':parsed_detail};ok=parsed_ok
   except Exception as pe:
    ok=False;detail={'returncode':p.returncode,'attempts':attempts,'parser_error':str(pe)}
  ck(name,ok,detail)
 except Exception as e:ck(name,False,str(e))
rr('full_package_builder_reproduction',['python',str(ROOT/'scripts/build_v101125_full_package_reconciliation.py'),str(BASE),str(td/'reb'),str(ROOT)],lambda:(True,{'status':'executed'}),60)
rr('continuity_candidate',['python',str(ROOT/'scripts/run_v101125_continuity_candidate_audit.py'),str(ROOT/'index.html'),str(td/'cand.json')],lambda:(json.loads((td/'cand.json').read_text())['status']=='PASS',json.loads((td/'cand.json').read_text())['status']))
rr('continuity_215',['python',str(ROOT/'scripts/run_v101125_continuity_matrix.py'),str(ROOT/'index.html'),str(td/'cont.json')],lambda:(json.loads((td/'cont.json').read_text())['pass']==215 and json.loads((td/'cont.json').read_text())['fail']==0,{'pass':json.loads((td/'cont.json').read_text())['pass'],'fail':json.loads((td/'cont.json').read_text())['fail'],'total':215}),60)
rr('ind_continuity_205',['python',str(ROOT/'scripts/run_v101125_independent_continuity_probe.py'),str(ROOT/'index.html'),str(td/'icont.json'),VER],lambda:(json.loads((td/'icont.json').read_text())['summary']=={'pass':205,'fail':0,'total':205},json.loads((td/'icont.json').read_text())['summary']),75)
rr('continuity_mutation_9',['python',str(ROOT/'scripts/run_v101125_continuity_mutation_tests.py'),str(ROOT/'index.html'),str(td/'cmut.json')],lambda:(json.loads((td/'cmut.json').read_text())['summary']=={'pass':9,'fail':0,'total':9},json.loads((td/'cmut.json').read_text())['summary']))
rr('continuity_speaker_header_5',['python',str(ROOT/'scripts/run_v101125_continuity_speaker_header_audit.py'),str(ROOT/'index.html'),str(td/'speaker.json')],lambda:(json.loads((td/'speaker.json').read_text())['summary']=={'pass':5,'fail':0,'total':5},json.loads((td/'speaker.json').read_text())['summary']))
rr('hour24_state_16',['python',str(ROOT/'scripts/run_v101125_hour24_state_matrix.py'),str(ROOT/'index.html'),str(td/'state.json'),VER],lambda:(json.loads((td/'state.json').read_text())['summary']=={'pass':16,'fail':0,'total':16},json.loads((td/'state.json').read_text())['summary']))
rr('hour24_ux_70',['python',str(ROOT/'scripts/run_v101125_five_profile_ux_matrix.py'),str(ROOT/'index.html'),str(td/'ux.json'),VER],lambda:(json.loads((td/'ux.json').read_text())['summary']['pass']==70 and json.loads((td/'ux.json').read_text())['summary']['fail']==0,json.loads((td/'ux.json').read_text())['summary']),60)
rr('help_70',['python',str(ROOT/'scripts/run_v101125_help_browser_matrix.py'),str(ROOT/'index.html'),str(td/'help.json'),VER],lambda:(json.loads((td/'help.json').read_text())['summary']['pass']==70 and json.loads((td/'help.json').read_text())['summary']['fail']==0,json.loads((td/'help.json').read_text())['summary']),60)
rr('broad_52',['python',str(ROOT/'scripts/run_broad_runtime_matrix.py'),str(ROOT/'index.html'),VER,str(td/'broad.json')],lambda:(json.loads((td/'broad.json').read_text())['summary']=={'pass':52,'fail':0,'total':52},json.loads((td/'broad.json').read_text())['summary']),60)
rr('fixed_point',['python',str(ROOT/'scripts/run_v101119_quoted_span_fixed_point.py'),str(ROOT/'index.html'),str(td/'fixed')],lambda:(lambda d:(d['scanner_a_valid_defects']==0 and d['scanner_b_valid_defects']==0 and d['presentation_relevant_spans']==398,{'A':d['scanner_a_valid_defects'],'B':d['scanner_b_valid_defects'],'spans':d['presentation_relevant_spans']}))(json.loads((td/'fixed/M1_FIXED_POINT_SUMMARY.json').read_text())),75)
ledger=td/'fixed/M1_QUOTED_SPAN_PRESENTATION_LEDGER.csv'
rr('presentation_1990',['python',str(ROOT/'scripts/run_v101119_exhaustive_presentation_matrix.py'),str(ROOT/'index.html'),str(ledger),str(td/'pres.json'),VER],lambda:(json.loads((td/'pres.json').read_text())['summary']['pass']==1990 and json.loads((td/'pres.json').read_text())['summary']['fail']==0,json.loads((td/'pres.json').read_text())['summary']),90)
rr('sw_15',['node',str(ROOT/'scripts/run_sw_logic_matrix.js'),str(ROOT/'sw.js'),CACHE,str(td/'sw.json')],lambda:(json.loads((td/'sw.json').read_text())['summary']=={'pass':15,'fail':0,'total':15},json.loads((td/'sw.json').read_text())['summary']))
rr('hour24_mutation_12',['python',str(ROOT/'scripts/run_v101125_mutation_tests.py'),str(ROOT/'index.html'),str(td/'hmut.json')],lambda:(json.loads((td/'hmut.json').read_text())['summary']=={'pass':12,'fail':0,'total':12},json.loads((td/'hmut.json').read_text())['summary']))
rr('ind_hour24_55',['python',str(ROOT/'scripts/run_v101125_independent_hour24_probe.py'),str(ROOT/'index.html'),str(td/'ih.json'),VER],lambda:(json.loads((td/'ih.json').read_text())['summary']['pass']==55 and json.loads((td/'ih.json').read_text())['summary']['fail']==0,json.loads((td/'ih.json').read_text())['summary']))
rr('ind_runtime_50',['python',str(ROOT/'scripts/run_v101125_independent_runtime_smoke.py'),str(ROOT/'index.html'),str(td/'ir.json'),VER],lambda:(json.loads((td/'ir.json').read_text())['summary']['pass']==50 and json.loads((td/'ir.json').read_text())['summary']['fail']==0,json.loads((td/'ir.json').read_text())['summary']))
rr('ind_presentation_1990',['python',str(ROOT/'scripts/run_v101125_independent_presentation_matrix.py'),str(ROOT/'index.html'),str(ledger),str(td/'ip.json'),VER],lambda:(json.loads((td/'ip.json').read_text())['summary']['pass']==1990 and json.loads((td/'ip.json').read_text())['summary']['fail']==0,json.loads((td/'ip.json').read_text())['summary']),90)
rr('current_evidence_schema',['python',str(ROOT/'scripts/run_v101125_current_evidence_schema_audit.py'),str(ROOT),str(td/'schema.json')],lambda:(json.loads((td/'schema.json').read_text())['status']=='PASS',json.loads((td/'schema.json').read_text())['summary']))
rr('report_claim_assertions',['python',str(ROOT/'scripts/run_v101125_report_claim_audit.py'),str(ROOT),str(td/'line.csv'),str(td/'assert.json'),str(td/'report_summary.json')],lambda:(json.loads((td/'report_summary.json').read_text())['status']=='PASS' and json.loads((td/'report_summary.json').read_text())['exact_coverage'] is True,{'summary':json.loads((td/'report_summary.json').read_text()),'assertions':json.loads((td/'assert.json').read_text()).get('assertions_total')}))
rr('stale_scans',['python',str(ROOT/'scripts/run_v101125_stale_scans.py'),str(ROOT),str(td/'vscan.json'),str(td/'sscan.json')],lambda:(json.loads((td/'vscan.json').read_text())['status']=='PASS' and json.loads((td/'sscan.json').read_text())['status']=='PASS',{'version':json.loads((td/'vscan.json').read_text())['status'],'semantic':json.loads((td/'sscan.json').read_text())['status']}))
status='PASS_PREFREEZE_INDEPENDENT_FOUR_PASS' if all(x['status']=='PASS' for x in C) else 'FAIL';obj={'schema':'L24H_V101125_INDEPENDENT_PREFREEZE_V1','version':VER,'stage':STAGE,'status':status,'checks_pass':sum(x['status']=='PASS' for x in C),'checks_total':len(C),'checks_fail':sum(x['status']=='FAIL' for x in C),'checks':C}
OJ.parent.mkdir(parents=True,exist_ok=True);OJ.write_text(json.dumps(obj,indent=2)+'\n');OM.write_text('# Independent prefreeze audit — v101.125\n\n**'+status+'**\n\n'+'\n'.join(f'- `{x["check"]}` — **{x["status"]}** — `{str(x["detail"])[:800]}`' for x in C)+'\n');shutil.rmtree(td,ignore_errors=True);print(json.dumps({'status':status,'pass':obj['checks_pass'],'fail':obj['checks_fail'],'total':obj['checks_total']}));raise SystemExit(0 if status.startswith('PASS') else 2)
