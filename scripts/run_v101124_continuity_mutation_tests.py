#!/usr/bin/env python3
from pathlib import Path
import json,re,sys,tempfile
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2])
EXPECTED=["['PASSION24.HOUR.03.P012','PASSION24.HOUR.03.P013']","['PASSION24.HOUR.13.P011','PASSION24.HOUR.13.P013']","['PASSION24.HOUR.15.P014','PASSION24.HOUR.15.P015']","['PASSION24.HOUR.19.P183','PASSION24.HOUR.19.P184']","['PASSION24.HOUR.19.P185','PASSION24.HOUR.19.P186']"]
def fragment_block(s):
 a=s.index('function buildContinuityFragment(')
 b=s.index('function buildContinuityFlowSurface(',a)
 return s[a:b]
def replace_in_fragment(s, old, new):
 a=s.index('function buildContinuityFragment(')
 b=s.index('function buildContinuityFlowSurface(',a)
 block=s[a:b]
 if old not in block: return s
 return s[:a]+block.replace(old,new,1)+s[b:]
def validate(s):
 frag=fragment_block(s)
 checks={
 'all_five_groups': all(x in s for x in EXPECTED),
 'inline_fragment_css': '.continuity-flow-surface .continuity-flow-fragment { display:inline!important;' in s,
 'inline_text_css': '.continuity-flow-surface .continuity-flow-fragment .para-text { display:inline!important;' in s,
 'space_joiner': '<span class="continuity-flow-joiner" aria-hidden="true"> </span>' in s,
 'fragment_stable_id': ' id="${p.id}"' in frag,
 'fragment_data_para_id': 'data-para-id="${p.id}"' in frag,
 'note_float': '.continuity-flow-surface .continuity-flow-fragment .para-note-dot { float:right;' in s,
 'group_renderer_used': '? buildMeditationParagraphHtml(displayParagraphs, hour.hour_number)' in s,
 'adjacency_fail_closed': "if (next && next.id===followerId)" in s,
 }
 return checks,all(checks.values())
base_checks,base_ok=validate(HTML)
mutations=[
 ('remove_hour15_group',lambda s:s.replace("                           ['PASSION24.HOUR.15.P014','PASSION24.HOUR.15.P015'],\n",'')),
 ('fragments_block',lambda s:s.replace('.continuity-flow-surface .continuity-flow-fragment { display:inline!important;','.continuity-flow-surface .continuity-flow-fragment { display:block!important;')),
 ('text_block',lambda s:s.replace('.continuity-flow-surface .continuity-flow-fragment .para-text { display:inline!important;','.continuity-flow-surface .continuity-flow-fragment .para-text { display:block!important;')),
 ('remove_join_space',lambda s:s.replace('<span class="continuity-flow-joiner" aria-hidden="true"> </span>','<span class="continuity-flow-joiner" aria-hidden="true"></span>')),
 ('remove_stable_id',lambda s:replace_in_fragment(s,' id="${p.id}"\n    ontouchstart','\n    ontouchstart')),
 ('remove_data_para_id',lambda s:replace_in_fragment(s,' data-para-id="${p.id}"','')),
 ('notes_back_in_flow',lambda s:s.replace('.continuity-flow-surface .continuity-flow-fragment .para-note-dot { float:right;','.continuity-flow-surface .continuity-flow-fragment .para-note-dot { float:none;')),
 ('bypass_group_renderer',lambda s:s.replace('? buildMeditationParagraphHtml(displayParagraphs, hour.hour_number)',"? displayParagraphs.map((p, i) => buildParaBlock(p, hour.hour_number, getDashListRhythmClass(displayParagraphs, i))).join('')")),
 ('remove_adjacency_guard',lambda s:s.replace('if (next && next.id===followerId) {','if (next) {')),
]
rows=[]
for name,fn in mutations:
 m=fn(HTML); checks,ok=validate(m); detected=not ok; rows.append({'mutation':name,'status':'PASS' if detected else 'FAIL','detected':detected,'failed_checks':[k for k,v in checks.items() if not v]})
out={'schema':'L24H_V101124_CONTINUITY_MUTATION_TESTS_V1','version':'v101.124','baseline_validator_status':'PASS' if base_ok else 'FAIL','baseline_checks':base_checks,'summary':{'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)},'rows':rows}
OUT.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out['summary']));raise SystemExit(0 if base_ok and all(r['status']=='PASS' for r in rows) else 2)
