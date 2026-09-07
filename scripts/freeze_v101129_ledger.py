#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json
ROOT=Path('/mnt/data/v101129_exec_strict'); EV=ROOT/'EVIDENCE_V101129'
ADD=Path('/mnt/data/L24H_v101129_PREVALIDATION_ADDENDUM_M1_2_NOUVEAUX_CAS_2026-09-03_FINAL.docx')
PRE=Path('/mnt/data/L24H_v101129_PREVALIDATION_CHANGEMENTS_DISPLAY_AVANT_APRES_2026-09-03.docx')
sha=lambda b: hashlib.sha256(b if isinstance(b,bytes) else b.encode('utf-8')).hexdigest()
rows={r['row_id']:r for r in csv.DictReader((EV/'05_DIRECT_SPEECH_EXIT_UNIVERSE.csv').open(encoding='utf-8'))}
ops=[
 ('V101129-QH-001','PASSION24.HOUR.08.P009#R00','RELOCATE_BREAK','42','93','0','93'),
 ('V101129-QH-002','PASSION24.HOUR.08.P009#R01','RELOCATE_BREAK','140','210','94','210'),
 ('V101129-QH-003','PASSION24.HOUR.08.P010#R00','REMOVE_BREAK','49','','0','92'),
 ('V101129-QH-004','PASSION24.HOUR.08.P015#R00','RELOCATE_BREAK','50','145','0','145'),
 ('V101129-QH-005','PASSION24.HOUR.21.P020#R00','REMOVE_BREAK','69','','0','101'),
 ('V101129-QH-006','PASSION24.HOUR.21.P025#R00','REMOVE_BREAK','118','','0','157'),
 ('V101129-QH-007','PASSION24.TEXT.RELATED_HOUR_06.BODY.P043#R00','REMOVE_BREAK','49','','CROSS_RECORD','RECORD_END'),
 ('V101129-QH-008','PASSION24.TEXT.RELATED_HOUR_06.BODY.P058#R00','REMOVE_BREAK','49','','CROSS_RECORD','RECORD_END'),
]
fields=['operation_id','semantic_locus_id','paragraph_id','alias_group','operation_type','old_break_offset','new_break_offset','canonical_text_sha256','speaker','quote_run_start','quote_run_end','host_sentence_start','host_sentence_end','exact_before','exact_after','evidence_ids','projection_action','topology_action','speech_end_map_action','speaker_data_action','user_state_impact','status']
out=[]
for opid,rid,typ,old,new,hs,he in ops:
 r=rows[rid]; text=r['full_text']; oldi=int(old); newi=int(new) if new else None
 before=text[max(0,oldi-40):oldi]
 after=text[oldi:min(len(text),oldi+60)]
 if newi is not None:
  after += ' || NEW_BOUNDARY ' + text[max(0,newi-30):min(len(text),newi+45)]
 out.append({
   'operation_id':opid,'semantic_locus_id':rid,'paragraph_id':r['paragraph_id'],'alias_group':r['alias_group'],
   'operation_type':typ,'old_break_offset':old,'new_break_offset':new,'canonical_text_sha256':r['text_sha256'],
   'speaker':r['speaker'],'quote_run_start':r['run_start'],'quote_run_end':r['run_end'],'host_sentence_start':hs,'host_sentence_end':he,
   'exact_before':before,'exact_after':after,
   'evidence_ids':'08_LANE_A_SYNTAX_ADJUDICATION.csv|09_LANE_B_INDEPENDENT_ADJUDICATION.csv|12_QUOTE_BREAK_ROLE_GRAPH.csv|USER_PREVALIDATION_WORD'+('|USER_ADDENDUM_APPROVAL' if opid.endswith(('007','008')) else ''),
   'projection_action':f'REMOVE {old}'+(f'; ADD {new}' if new else ''),
   'topology_action':f'REMOVE {old}'+(f'; ADD {new}' if new else ''),
   'speech_end_map_action':f'REMOVE {old}; DO NOT ADD HOST_SENTENCE_BREAK',
   'speaker_data_action':'NONE','user_state_impact':'NONE_CHARACTER_OFFSETS_UNCHANGED','status':'FROZEN_AUTHORISED_USER_VALIDATED'
 })
p=EV/'15_V101129_QUOTE_HOST_TOPOLOGY_MUTATION_LEDGER_FROZEN.csv'
with p.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
h=sha(p.read_bytes());(EV/'16_MUTATION_LEDGER_SHA256.txt').write_text(f'{h}  {p.name}\n',encoding='utf-8')
stage=json.loads((EV/'00_CURRENT_STAGE_LOCK.json').read_text(encoding='utf-8'))
stage.update({'mutation_authority':'FROZEN_8_USER_VALIDATED_TOPOLOGY_OPERATIONS','m1_status':'PASS','ledger':p.name,'ledger_sha256':h,'additional_addendum':ADD.name,'additional_addendum_sha256':sha(ADD.read_bytes()),'user_approval':'APPROVED_BOTH_ADDITIONAL_CASES_2026-09-03','status':'M2_AUTHORISED'})
(EV/'00_CURRENT_STAGE_LOCK.json').write_text(json.dumps(stage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary=json.loads((EV/'M1_FIXED_POINT_SUMMARY.json').read_text(encoding='utf-8'))
summary.update({'additional_unvalidated_defect_rows':0,'additional_unvalidated_ids':[],'user_validated_defect_rows':8,'mutation_freeze_authority':'AUTHORISED_8_OPERATIONS','next_gate':'M2'})
(EV/'M1_FIXED_POINT_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'ledger_rows':len(out),'ledger_sha256':h,'stage':'M2_AUTHORISED'},indent=2))
