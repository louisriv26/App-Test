#!/usr/bin/env python3
from pathlib import Path
import sys,re,json
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');OUT=Path(sys.argv[2])

def fun(txt,name):
 m=re.search(r'function\s+'+re.escape(name)+r'\s*\(',txt)
 if not m: return ''
 i=txt.find('(',m.start()); pd=0;q=None;esc=False
 while i<len(txt):
  c=txt[i]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:q=None
  else:
   if c in "'\"`":q=c
   elif c=='(':pd+=1
   elif c==')':
    pd-=1
    if pd==0: i+=1;break
  i+=1
 b=txt.find('{',i);dep=1;q=None;esc=False;line=False;blk=False;j=b+1
 while dep and j<len(txt):
  c=txt[j];n=txt[j+1] if j+1<len(txt) else ''
  if line:
   if c=='\n':line=False
   j+=1;continue
  if blk:
   if c=='*' and n=='/':blk=False;j+=2;continue
   j+=1;continue
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:q=None
   j+=1;continue
  if c=='/' and n=='/':line=True;j+=2;continue
  if c=='/' and n=='*':blk=True;j+=2;continue
  if c in "'\"`":q=c;j+=1;continue
  if c=='{':dep+=1
  elif c=='}':dep-=1
  j+=1
 return txt[m.start():j]

def validate(txt):
 errs=[]
 a=fun(txt,'buildHourEndActions'); p=fun(txt,'buildHour24CyclePanel'); r=fun(txt,'refreshHourEndCycleUI'); m=fun(txt,'markMeditee'); rs=fun(txt,'restartTwentyFourHours'); rr=fun(txt,'renderReader')
 for x in ['Réflexion et pratique','Approfondir','Revenir au début']:
  if x not in a: errs.append('hour_action_missing:'+x)
 if 'showProgressView()' in a or 'showCompletedHoursView()' in a or 'restartTwentyFourHours' in a: errs.append('cycle_action_leaked_to_hour_actions')
 if "const nextHour = isTerminal ? null : next" not in a: errs.append('hours_1_23_next_contract_missing')
 if "if (Number(hour && hour.hour_number) !== 24) return '';" not in p: errs.append('hour24_scope_missing')
 if 'getProgressSnapshot()' not in p or 'if (!p.complete)' not in p: errs.append('canonical_complete_gate_missing')
 ix=p.find('if (!p.complete)'); ret=p.find('return `',ix); end=p.find('`;',ret)
 inc=p[ret:end] if ret>=0 and end>=0 else ''
 if 'restartTwentyFourHours' in inc or 'Recommencer' in inc: errs.append('restart_visible_in_incomplete_branch')
 if 'restartTwentyFourHours({requireComplete:true' not in p: errs.append('completed_restart_action_missing')
 if "state.view !== 'reader'" not in r or 'state.currentHour' not in r or '!== 24' not in r: errs.append('refresh_not_hour24_scoped')
 if 'refreshHourEndCycleUI();' not in m: errs.append('meditee_does_not_refresh')
 if 'requireComplete' not in rs or 'requireComplete && !p.complete' not in rs: errs.append('restart_complete_guard_missing')
 if "destination === 'hour1'" not in rs or 'openHour(1, false)' not in rs: errs.append('restart_hour1_destination_missing')
 if re.search(r'state\.(notes|textHighlights|libraryMarks|themePreference)\s*=',rs): errs.append('restart_clears_protected_personal_data')
 if '${next ? `<button class="nav-btn"' not in rr or "${!next?'disabled':''}" in rr: errs.append('hour24_next_control_not_removed')
 if 'Revenir à l’Accueil' in txt: errs.append('redundant_home_restored')
 return errs

base=validate(HTML)
if base: raise SystemExit('Baseline validator failed: '+repr(base))
mutations=[]
def add(mid,desc,mutator,expect):
 t=mutator(HTML); errors=validate(t); ok=expect in errors
 mutations.append({'mutation':mid,'description':desc,'status':'PASS' if ok else 'FAIL','expected_detection':expect,'detected_errors':errors})

add('MUT-01','Treat Hour 24 as complete regardless of progress',lambda s:s.replace('if (!p.complete) {','if (false) {',1),'canonical_complete_gate_missing')
add('MUT-02','Show restart in incomplete state',lambda s:s.replace('Show `VOTRE PARCOURS`' if False else '<div class="hour-end-buttons"><button type="button" class="hour-end-btn primary" onclick="showProgressView()">Voir ma progression</button>', '<div class="hour-end-buttons"><button type="button" class="hour-end-btn" onclick="restartTwentyFourHours({requireComplete:true,destination:\'hour1\'})">Recommencer</button><button type="button" class="hour-end-btn primary" onclick="showProgressView()">Voir ma progression</button>',1),'restart_visible_in_incomplete_branch')
add('MUT-03','Omit Hour-24 Réflexion et pratique',lambda s:s.replace('Réflexion et pratique</button>','Réflexion supprimée</button>',1),'hour_action_missing:Réflexion et pratique')
add('MUT-04','Omit Hour-24 Approfondir',lambda s:s.replace('>Approfondir</button>','>Approfondissement supprimé</button>',1),'hour_action_missing:Approfondir')
add('MUT-05','Omit Hour-24 Revenir au début',lambda s:s.replace('↟ Revenir au début</button>','↟ Retour supprimé</button>',1),'hour_action_missing:Revenir au début')
add('MUT-06','Leave Suivante rendered on Hour 24',lambda s:s.replace('${next ? `<button class="nav-btn"','${true ? `<button class="nav-btn"',1),'hour24_next_control_not_removed')
add('MUT-07','Fail to refresh after Méditée toggle',lambda s:s.replace('  refreshHourEndCycleUI();\n  if (committed.ok)','  if (committed.ok)',1),'meditee_does_not_refresh')
add('MUT-08','Allow incomplete completed-cycle reset',lambda s:s.replace('if (requireComplete && !p.complete) {','if (false) {',1),'restart_complete_guard_missing')
add('MUT-09','Route completed restart to Home',lambda s:s.replace('openHour(1, false);','showHome();',1),'restart_hour1_destination_missing')
add('MUT-10','Clear notes/highlights during restart',lambda s:s.replace('state.meditationLog = [];','state.meditationLog = [];\n  state.notes = {};\n  state.textHighlights = {};',1),'restart_clears_protected_personal_data')
add('MUT-11','Add progress action to Hours 1–23',lambda s:s.replace('${nextBtn}</div></div>`;','${nextBtn}<button type="button" onclick="showProgressView()">Voir ma progression</button></div></div>`;',1),'cycle_action_leaked_to_hour_actions')
add('MUT-12','Restore redundant Hour-24 Accueil action',lambda s:s.replace('Voir ma progression</button>','Voir ma progression</button><button type="button">Revenir à l’Accueil</button>',1),'redundant_home_restored')
summary={'pass':sum(x['status']=='PASS' for x in mutations),'fail':sum(x['status']=='FAIL' for x in mutations),'total':len(mutations)}
OUT.write_text(json.dumps({'schema':'L24H_V101125_MUTATION_TEST_MATRIX_V1','baseline_validator_errors':base,'summary':summary,'mutations':mutations},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary));raise SystemExit(0 if summary['fail']==0 and summary['total']==12 else 2)
