#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys,zipfile
ROOT=Path(sys.argv[1]);BASE=Path(sys.argv[2]);OUT=Path(sys.argv[3]);OUT.parent.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
def add(n,ok,d=None):rows.append({'check':n,'status':'PASS' if ok else 'FAIL','detail':d})
m=json.loads((ROOT/'metadata/builder_input_manifest.json').read_text())
add('baseline_sha_exact',sha(BASE)==m['baseline_zip']['sha256'],sha(BASE))
with zipfile.ZipFile(BASE) as z:add('baseline_members_exact',len(z.infolist())==m['baseline_zip']['members'],len(z.infolist()))
missing=[];bad=[]
for x in m['source_files']:
 p=ROOT/x['path']
 if not p.is_file():missing.append(x['path'])
 elif sha(p)!=x['sha256'] or p.stat().st_size!=x['size']:bad.append({'path':x['path'],'sha':sha(p),'size':p.stat().st_size})
add('all_source_inputs_package_local',not missing,missing)
add('all_source_inputs_sha_bound',not bad,bad[:10])
add('input_manifest_nonempty',len(m.get('source_files',[]))>=20,len(m.get('source_files',[])))
sm={'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'total':len(rows)}
OUT.write_text(json.dumps({'schema':'L24H_V101135_BUILDER_INPUT_MANIFEST_GATE_V1','summary':sm,'rows':rows},indent=2)+'\n');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
