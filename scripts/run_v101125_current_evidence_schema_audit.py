#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(sys.argv[1]); OUT=Path(sys.argv[2]); VER='v101.125'
EV=ROOT/'evidence/v101125'
allowed={
 'evidence/v101125/fixed/M1_FIXED_POINT_SUMMARY.json':'L24H_V101119_QUOTED_SPAN_FIXED_POINT_R1',
 'evidence/v101125/EXHAUSTIVE_PRESENTATION_RUNTIME_MATRIX.json':'L24H_V101119_EXHAUSTIVE_PRESENTATION_MATRIX_V1',
}
rows=[]
for p in sorted(EV.rglob('*.json')):
 rel=p.relative_to(ROOT).as_posix()
 try:d=json.loads(p.read_text(encoding='utf-8'))
 except Exception as e:
  rows.append({'path':rel,'status':'FAIL','issue':'invalid_json','detail':str(e)});continue
 schema=d.get('schema'); evver=d.get('version'); issues=[]
 if evver is not None and evver!=VER:issues.append('version_field='+str(evver))
 if isinstance(schema,str):
  m=re.search(r'V101(\d{3})',schema)
  if m and m.group(1)!='125' and allowed.get(rel)!=schema:issues.append('schema='+schema)
 rows.append({'path':rel,'status':'PASS' if not issues else 'FAIL','schema':schema,'version':evver,'issues':issues,'lineage_allowance':allowed.get(rel)})
summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
obj={'schema':'L24H_V101125_CURRENT_EVIDENCE_SCHEMA_AUDIT_V1','version':VER,'status':'PASS' if summary['fail']==0 else 'FAIL','summary':summary,'allowed_reused_lineage':allowed,'rows':rows};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':obj['status'],**summary}));raise SystemExit(0 if obj['status']=='PASS' else 2)
