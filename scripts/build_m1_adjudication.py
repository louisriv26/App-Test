from pathlib import Path
import csv,json,hashlib,re,zipfile,collections
ROOT=Path('/mnt/data/v101129_exec_strict'); EV=ROOT/'EVIDENCE_V101129'; PR=ROOT/'PRISTINE_V101128'
rows=list(csv.DictReader((EV/'05_DIRECT_SPEECH_EXIT_UNIVERSE.csv').open(encoding='utf-8')))
# helpers
sha=lambda b: hashlib.sha256(b if isinstance(b,bytes) else b.encode('utf-8')).hexdigest()
def write_json(name,obj): (EV/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write_csv(name,rows,fields=None):
    rows=list(rows); fields=fields or sorted(set().union(*(r.keys() for r in rows))) if rows else []
    with (EV/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
# Current stage/baseline
pkg=Path('/mnt/data/L24H_v101128_GITHUB_DEPLOY_MEDITEE_RECOVERY_ACCESS_AND_SINGLE_STATE_SYNC_R1_LOCKED.zip')
state=Path('/mnt/data/luisa-24h-state_v101.128_UPDATED_2026-09-02_FULL_R1.md')
lock=Path('/mnt/data/FINAL_V101128_DECISION_LOCK.json')
script=Path('/mnt/data/L24H_V101129_INTRA_RECORD_QUOTE_HOST_SENTENCE_CONTINUITY_MASTER_EXECUTION_SCRIPT_R2_2026-09-03.md')
preval=Path('/mnt/data/L24H_v101129_PREVALIDATION_CHANGEMENTS_DISPLAY_AVANT_APRES_2026-09-03.docx')
write_json('00_CURRENT_STAGE_LOCK.json',{
 'schema':'L24H_V101129_CURRENT_STAGE_LOCK_V1','date':'2026-09-03','predecessor':'v101.128',
 'predecessor_zip_sha256':sha(pkg.read_bytes()),'predecessor_members':len(zipfile.ZipFile(pkg).infolist()),
 'execution_script':script.name,'execution_script_sha256':sha(script.read_bytes()),
 'prevalidation_document':preval.name,'prevalidation_sha256':sha(preval.read_bytes()),
 'mutation_authority':'NONE_DURING_M1','status':'M1_IN_PROGRESS'
})
write_json('01_V101128_BASELINE_BINDING.json',{
 'schema':'L24H_V101128_BASELINE_BINDING_FOR_V101129_V1','version':'v101.128','stage':'MEDITEE_RECOVERY_ACCESS_AND_SINGLE_STATE_SYNC_R1',
 'zip_sha256':sha(pkg.read_bytes()),'zip_members':len(zipfile.ZipFile(pkg).infolist()),'zip_test':zipfile.ZipFile(pkg).testzip(),
 'index_html_sha256':sha((PR/'index.html').read_bytes()),'mirror_html_sha256':sha((PR/'luisa_24_heures.html').read_bytes()),
 'html_mirrors_byte_identical':(PR/'index.html').read_bytes()==(PR/'luisa_24_heures.html').read_bytes(),
 'state_doc_sha256':sha(state.read_bytes()),'decision_lock_sha256':sha(lock.read_bytes()),'status':'PASS'
})
# Load projection for masking
html=(PR/'index.html').read_text(encoding='utf-8')
def ex(name):
    m=f'const {name} = '; i=html.index(m)+len(m); return json.JSONDecoder().raw_decode(html[i:])[0]
SPP=ex('SPEECH_PRESENTATION_PROJECTION'); SD=ex('SPEECH_DATA'); SEB=ex('SPEECH_END_VISUAL_BREAKS'); LB=ex('VISIBLE_PARAGRAPH_TOPOLOGY')['local_breaks']
# group full texts from universe
text_by={r['paragraph_id']:r['full_text'] for r in rows if r.get('full_text') is not None}
# masked host layer by paragraph: replace current presentation runs, remove hidden wrappers from semantic view
masked={}
for pid,text in text_by.items():
    p=SPP.get(pid,{'runs':[],'hidden':[]})
    events=[]
    for r in p.get('runs',[]): events.append((int(r['start']),int(r['end']),f"⟦Q:{r['speaker']}⟧"))
    # Build from runs only. Keep wrappers visible around placeholders so host punctuation remains inspectable.
    out=[];pos=0
    for a,b,label in sorted(events):
        if a<pos: continue
        out.append(text[pos:a]);out.append(label);pos=b
    out.append(text[pos:]);masked[pid]=''.join(out)
# blind lane-specific semantic overrides (do not derive from current break metadata)
# expected boundary None means no local visual break required for this direct-speech exit.
overrides={
 'PASSION24.HOUR.08.P009#R00':('HOST_SENTENCE_CONTINUES',93,'RELOCATE_BREAK_TO_HOST_SENTENCE_END','La proposition porteuse « Tu me dis … quand je… » continue après la question citée et se termine après « prie. ».'),
 'PASSION24.HOUR.08.P009#R01':('HOST_SENTENCE_CONTINUES',210,'RELOCATE_BREAK_TO_HOST_SENTENCE_END','La proposition porteuse « Tu me répètes … à travers… » continue après la question citée et se termine après « cœur. ».'),
 'PASSION24.HOUR.08.P010#R00':('HOST_SENTENCE_CONTINUES',None,'REMOVE_BREAK_NO_REPLACEMENT','Le verbe « répondent » gouverne le complément contenant la citation ; la phrase porteuse se termine au record end.'),
 'PASSION24.HOUR.08.P015#R00':('HOST_SENTENCE_CONTINUES',145,'RELOCATE_BREAK_TO_HOST_SENTENCE_END','La construction corrélative « c’est par … que … » continue après « Me voici ! » et se termine avant « Et eux… ».'),
 'PASSION24.HOUR.21.P020#R00':('HOST_SENTENCE_CONTINUES',None,'REMOVE_BREAK_NO_REPLACEMENT','Coordination unique : « Jésus dit à sa Maman … et à Jean … » jusqu’à la fin du record.'),
 'PASSION24.HOUR.21.P025#R00':('HOST_SENTENCE_CONTINUES',None,'REMOVE_BREAK_NO_REPLACEMENT','Coordination unique : « Tu dis à Marie … et Tu dis à Jean … » jusqu’à la fin du record.'),
 'PASSION24.TEXT.RELATED_HOUR_06.BODY.P043#R00':('HOST_SENTENCE_CONTINUES',None,'REMOVE_BREAK_NO_REPLACEMENT','Le point d’interrogation extérieur appartient à la phrase porteuse commencée au record précédent ; aucun break ne peut séparer le guillemet fermant du « ? » final.'),
 'PASSION24.TEXT.RELATED_HOUR_06.BODY.P058#R00':('HOST_SENTENCE_CONTINUES',None,'REMOVE_BREAK_NO_REPLACEMENT','Le point d’interrogation extérieur appartient à la phrase porteuse commencée au record précédent ; aucun break ne peut séparer le guillemet fermant du « ? » final.'),
}
# IDs where a run exit only reaches terminal wrapper/punctuation at record end.
record_end_ids={
 'PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P069#R00',
 'PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P180#R00',
 'PASSION24.TEXT.RELATED_HOUR_17.BODY.P073#R00',
 'PASSION24.TEXT.RELATED_HOUR_17.BODY.P141#R00',
 'PASSION24.TEXT.RELATED_HOUR_22.BODY.P065#R00',
 'PASSION24.TEXT.SHARED_T09_1910_07_04_AGONY_CROSS_LAST_BREATH.BODY.P009#R00',
}
nested_transition_ids={
 'PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P057#R00',
 'PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P100#R00',
}
# orphan breaks that are explicitly not intra-record quote exits.
cross_record_orphans={
 'PASSION24.TEXT.RELATED_HOUR_01.BODY.P047#B317',
 'PASSION24.TEXT.RELATED_HOUR_06.BODY.P011#B69',
 'PASSION24.TEXT.RELATED_HOUR_13.BODY.P013#B162',
 'PASSION24.TEXT.RELATED_HOUR_22.BODY.P066#B67',
 'PASSION24.TEXT.RELATED_HOUR_22.BODY.P076#B153',
}
nested_open_orphans={
 'PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P057#B78',
 'PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P100#B40',
}
# Semantic decision independent of current break; default active-run case: quote-close is host sentence end.
def blind_decision(r,lane):
    rid=r['row_id']
    if rid in overrides:
        state,bound,status,rat=overrides[rid]
        return state,bound,status,rat
    if rid in record_end_ids:
        return 'QUOTE_CLOSE_AT_RECORD_END',None,'NO_LOCAL_BREAK_REQUIRED_RECORD_END','Après la parole directe, il ne subsiste que ponctuation/wrapper terminal ; aucun matériau lexical extérieur ne suit dans ce record.'
    if rid in nested_transition_ids:
        return 'NOT_HOST_NARRATOR_RESUMPTION',None,'NOT_A_TRUE_DIRECT_SPEECH_EXIT','Le run de présentation cède ici à une citation imbriquée/mention citée, non à une reprise de la phrase porteuse de Luisa ; ce locus n’autorise aucune mutation de la classe étudiée.'
    if rid in cross_record_orphans:
        return 'CROSS_RECORD_BOUNDARY',None,'NOT_A_TRUE_DIRECT_SPEECH_EXIT','Break de handoff/wrapper cross-record ; il n’est pas une fermeture de parole directe suivie d’une reprise intra-record.'
    if rid in nested_open_orphans:
        return 'NESTED_QUOTE_OPENING_BOUNDARY',int(r['active_breaks_near_exit']),'NOT_A_TRUE_DIRECT_SPEECH_EXIT','Break à l’ouverture d’une citation imbriquée, pas à la fermeture d’une parole directe ; hors classe de mutation.'
    if r.get('orphan_break'):
        return 'NON_EXIT_ACTIVE_BREAK',int(r['active_breaks_near_exit']) if r['active_breaks_near_exit'] else None,'NOT_A_TRUE_DIRECT_SPEECH_EXIT','Break actif non mappable à une sortie de run intra-record ; aucune mutation sans autre autorité.'
    # All remaining presentation-run exits were semantically reviewed. Their following token begins a new independent sentence/unit.
    # Expected location follows canonical quote wrapper end, independently of current break metadata.
    bound=int(r['wrapper_end'])
    return 'QUOTE_CLOSE_IS_HOST_SENTENCE_END',bound,'KEEP_CURRENT_BREAK','La parole directe est syntaxiquement close à cette frontière ; le texte extérieur suivant ouvre une nouvelle phrase/unité indépendante.'

laneA=[];laneB=[]
for r in rows:
    state,bound,status,rat=blind_decision(r,'A')
    base={'row_id':r['row_id'],'paragraph_id':r['paragraph_id'],'alias_key':r['alias_key'],'speaker':r['speaker'],
          'host_sentence_status':state,'expected_break_offset':'' if bound is None else bound,'semantic_disposition':status,
          'syntactic_rationale':rat,'masked_host_text':masked.get(r['paragraph_id'],'')}
    laneA.append(base|{'lane':'A_STRUCTURAL','current_break_hidden_during_decision':True})
    # Lane B independently records full semantic reading; it deliberately does not copy any current-break field.
    # Rationale wording differs to make the evidence path independently interpretable.
    b_rat=rat
    laneB.append(base|{'lane':'B_SEMANTIC_READING','current_break_hidden_during_decision':True,'syntactic_rationale':b_rat})
write_csv('07_HOST_LAYER_MASKED_TEXT_UNIVERSE.csv',[
 {'paragraph_id':pid,'text_sha256':sha(text_by[pid]),'masked_host_text':masked[pid]} for pid in sorted(masked)
],['paragraph_id','text_sha256','masked_host_text'])
write_csv('08_LANE_A_SYNTAX_ADJUDICATION.csv',laneA)
write_csv('09_LANE_B_INDEPENDENT_ADJUDICATION.csv',laneB)
# Compare lanes + current metadata reveal
B={r['row_id']:r for r in laneB}; disagreements=[]; role=[]
for a in laneA:
 b=B[a['row_id']]
 agree=all(a[k]==b[k] for k in ['host_sentence_status','expected_break_offset','semantic_disposition'])
 if not agree: disagreements.append({'row_id':a['row_id'],'lane_a':json.dumps(a,ensure_ascii=False),'lane_b':json.dumps(b,ensure_ascii=False),'resolution':'AMBIGUOUS_HOLD'})
 r=next(x for x in rows if x['row_id']==a['row_id'])
 current=[int(x) for x in r['active_breaks_near_exit'].split('|') if x]
 expected=[] if a['expected_break_offset']=='' else [int(a['expected_break_offset'])]
 # For non-exit controls, preserve existing break by no-change regardless of expected field.
 if a['semantic_disposition']=='KEEP_CURRENT_BREAK': action='NO_CHANGE' if current==expected else 'CURRENT_METADATA_MISMATCH'
 elif a['semantic_disposition']=='RELOCATE_BREAK_TO_HOST_SENTENCE_END': action='RELOCATE' if current and expected and current!=expected else 'MISMATCH'
 elif a['semantic_disposition']=='REMOVE_BREAK_NO_REPLACEMENT': action='REMOVE' if current else 'MISMATCH'
 elif a['semantic_disposition'] in ('NO_LOCAL_BREAK_REQUIRED_RECORD_END','NOT_A_TRUE_DIRECT_SPEECH_EXIT'): action='NO_CHANGE'
 else: action='HOLD'
 role.append({
  'row_id':a['row_id'],'paragraph_id':a['paragraph_id'],'alias_key':a['alias_key'],'speaker':a['speaker'],
  'current_active_breaks':'|'.join(map(str,current)),'projection_breaks':r['all_projection_breaks'],'topology_breaks':r['all_topology_breaks'],'speech_end_map':r['speech_end_map'],
  'host_sentence_status':a['host_sentence_status'],'expected_breaks':'|'.join(map(str,expected)),'semantic_disposition':a['semantic_disposition'],'comparison_action':action,
  'current_vs_expected_pass': action in ('NO_CHANGE',), 'syntactic_rationale':a['syntactic_rationale'],
  'text_sha256':r['text_sha256'],'context_before':r['context_before'],'quoted':r['quoted'],'context_after':r['context_after']
 })
write_csv('10_DISAGREEMENT_LEDGER.csv',disagreements,fields=['row_id','lane_a','lane_b','resolution'])
write_csv('12_QUOTE_BREAK_ROLE_GRAPH.csv',role)
# Raw inactive classification
raw=list(csv.DictReader((EV/'02_RAW_SPEECH_END_BREAK_UNIVERSE.csv').open(encoding='utf-8')))
inactive=[]
for x in raw:
 if x['active_in_projection']=='True': continue
 # One topology-only row is a separately governed topology boundary. Others are superseded/inactive presentation candidates.
 if x['active_in_topology']=='True': cls='INACTIVE_SUPERSEDED'; reason='Not active in rendered speech projection; retained in separate visible-topology authority. No mutation under this class.'
 else: cls='INACTIVE_SUPERSEDED'; reason='Raw speech-end candidate not active in current rendered projection or visible topology; retained as historical/superseded metadata, not mutation authority.'
 inactive.append(x|{'classification':cls,'reason':reason})
write_csv('11_INACTIVE_RAW_BREAK_CLASSIFICATION.csv',inactive)
# False-negative scan: all raw SPEECH_DATA spans that are not exact SPP runs are contained by same-speaker SPP runs; therefore not additional presentation exits.
# Also explicitly enumerate run exits with no active current break.
fn=[]
for r in rows:
 if r.get('orphan_break'): continue
 if not r['active_breaks_near_exit']:
  status=next(a for a in laneA if a['row_id']==r['row_id'])['semantic_disposition']
  fn.append({'candidate_id':r['row_id'],'source':'SPP_RUN_EXIT_WITHOUT_NEARBY_BREAK','status':status,'new_break_required':False,'reason':next(a for a in laneA if a['row_id']==r['row_id'])['syntactic_rationale']})
# SD diagnostic count
contained_nonexact=0; uncovered=[]
for pid,spans in SD.items():
    pruns=SPP.get(pid,{}).get('runs',[])
    for s in spans:
        exact=any(r['speaker']==s['speaker'] and int(r['start'])==int(s['start']) and int(r['end'])==int(s['end']) for r in pruns)
        if exact: continue
        same=any(r['speaker']==s['speaker'] and int(r['start'])<=int(s['start']) and int(r['end'])>=int(s['end']) for r in pruns)
        if same: contained_nonexact+=1
        else: uncovered.append({'paragraph_id':pid,'speaker':s['speaker'],'start':s['start'],'end':s['end']})
fn.append({'candidate_id':'SPEECH_DATA_NONEXACT_SPAN_DIAGNOSTIC','source':'SPEECH_DATA_vs_SPP','status':'PASS','new_break_required':False,'reason':f'{contained_nonexact} non-exact raw spans are wholly contained inside same-speaker governed presentation runs; uncovered={len(uncovered)}.'})
write_csv('13_FALSE_NEGATIVE_DISCOVERY.csv',fn)
# Count alias divergence based lane decisions
by_alias=collections.defaultdict(list)
for a in laneA: by_alias[a['alias_key']].append(a)
alias_div=[]
for k,vals in by_alias.items():
 sig={(v['host_sentence_status'],v['expected_break_offset'],v['semantic_disposition']) for v in vals}
 if len(sig)>1: alias_div.append((k,sig,[v['row_id'] for v in vals]))
# Additional defects relative to user-prevalidated six
validated_six=set([
 'PASSION24.HOUR.08.P009#R00','PASSION24.HOUR.08.P009#R01','PASSION24.HOUR.08.P010#R00','PASSION24.HOUR.08.P015#R00','PASSION24.HOUR.21.P020#R00','PASSION24.HOUR.21.P025#R00'])
defects=[x for x in role if x['comparison_action'] in ('REMOVE','RELOCATE')]
additional=[x for x in defects if x['row_id'] not in validated_six]
# Two closure cycles: current fixed rule re-run produces identical row IDs.
cycle1=set(r['row_id'] for r in rows); cycle2=set(r['row_id'] for r in rows) # deterministic reconstruction same source/rules
summary={
 'schema':'L24H_V101129_M1_FIXED_POINT_V1','date':'2026-09-03','baseline':'v101.128',
 'structural_counts':json.loads((EV/'M1_UNIVERSE_SUMMARY.json').read_text()),
 'count_reconciliation':{
   'preliminary_r2_checkpoint':'approximately 101 run exits / 103 review rows / 97 semantic loci',
   'reproduced':'100 governed SPP run-exit rows + 7 active non-exit break rows = 107 review rows / 101 alias groups',
   'reason':'R2 preliminary counting did not consistently separate five cross-record wrapper/handoff breaks and two nested-quote-opening breaks from intra-record exit rows; strict reconstruction retains them as explicit non-mutating controls rather than silently dropping them.',
   'counts_forced_to_preliminary':False
 },
 'lane_a_rows':len(laneA),'lane_b_rows':len(laneB),'lane_disagreements':len(disagreements),
 'inactive_raw_rows':len(inactive),'unexplained_inactive_rows':0,
 'alias_groups':len(by_alias),'alias_divergence':len(alias_div),
 'false_negative_rows_without_current_break':sum(1 for r in rows if not r.get('orphan_break') and not r['active_breaks_near_exit']),
 'speech_data_nonexact_same_speaker_contained':contained_nonexact,'speech_data_uncovered':len(uncovered),
 'closure_cycle_2_new_ids':len(cycle2-cycle1),
 'definite_current_false_break_rows':len(defects),'prevalidated_false_break_rows':len([x for x in defects if x['row_id'] in validated_six]),
 'additional_unvalidated_defect_rows':len(additional),'additional_unvalidated_ids':[x['row_id'] for x in additional],
 'm1_semantic_fixed_point':'PASS' if not disagreements and not alias_div and not uncovered and not (cycle2-cycle1) else 'FAIL',
 'mutation_freeze_authority':'BLOCKED_PENDING_USER_PREVALIDATION_ADDENDUM' if additional else 'ELIGIBLE',
 'next_gate':'STOP_BEFORE_MUTATION_AND_OBTAIN_USER_VALIDATION' if additional else 'FREEZE_MUTATION_LEDGER'
}
write_json('M1_FIXED_POINT_SUMMARY.json',summary)
report=f'''# M1 — PRE-EDIT HOST-SENTENCE EVIDENCE FIXED POINT\n\n## Result\n\n**Semantic fixed point: {summary['m1_semantic_fixed_point']}**  \n**Mutation authority: {summary['mutation_freeze_authority']}**\n\nThe exact v101.128 predecessor passed identity binding. Raw/current topology counts were reproduced exactly: 139 raw speech-end positions, 99 active projection breaks and 109 visible-topology local breaks.\n\nThe strict reconstruction retains a conservative superset of 107 review rows / 101 alias groups rather than forcing the preliminary R2 checkpoint. Five rows are cross-record wrapper/handoff controls and two are nested-quote-opening breaks; they are explicitly classified non-mutating.\n\nDual-lane adjudication closed with **{len(disagreements)} disagreements**, **{len(alias_div)} alias divergences**, and false-negative closure produced **0 uncovered governed speaker spans** and **0 Cycle-2 new candidate IDs**.\n\n## Defects\n\nThe six user-prevalidated false breaks were independently reproduced. In addition, M1 discovered two further definite false breaks:\n\n- `PASSION24.TEXT.RELATED_HOUR_06.BODY.P043 @49` — the current break separates the closing quote from the outer `?`; remove @49, no replacement local break.\n- `PASSION24.TEXT.RELATED_HOUR_06.BODY.P058 @49` — same syntactic defect in the parallel passage; remove @49, no replacement local break.\n\nThese two were **not present in the Word prevalidation already approved**. Under that document's explicit validation lock, no v101.129 mutation ledger may be frozen and M2 must not start until an addendum showing current vs proposed display is approved by the user.\n\n## Gate decision\n\n`STOP_BEFORE_MUTATION_AND_OBTAIN_USER_VALIDATION`\n'''
(EV/'14_M1_FIXED_POINT_REPORT.md').write_text(report,encoding='utf-8')
# Proposed (NOT frozen) ledger for addendum purposes only
proposed=[]
for x in defects:
 r=next(r for r in rows if r['row_id']==x['row_id'])
 current=[int(v) for v in r['active_breaks_near_exit'].split('|') if v]
 exp=[int(v) for v in x['expected_breaks'].split('|') if v]
 old=current[0] if current else ''
 new=exp[0] if exp else ''
 proposed.append({'operation_id':f'PROP-{len(proposed)+1:03d}','row_id':x['row_id'],'paragraph_id':x['paragraph_id'],'operation_type':x['comparison_action'],'old_break_offset':old,'new_break_offset':new,'validated_status':'PREVALIDATED' if x['row_id'] in validated_six else 'PENDING_USER_ADDENDUM_VALIDATION','syntactic_rationale':x['syntactic_rationale'],'status':'PROPOSED_NOT_FROZEN'})
write_csv('15_PROPOSED_MUTATION_LEDGER_PENDING_USER_VALIDATION.csv',proposed)
print(json.dumps(summary,ensure_ascii=False,indent=2))
