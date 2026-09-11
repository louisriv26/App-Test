#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,zipfile,shutil,sys
BASE=Path(sys.argv[1]); SRC=Path(sys.argv[2]); OUT=Path(sys.argv[3])
EXPECTED='d2614307d3335d4e76a3b9559cb4d8267549b9a5a4adf4ec616344f2b98664d6'
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
if sha(BASE)!=EXPECTED: raise SystemExit('baseline SHA mismatch')
manifest=json.loads((SRC/'metadata/full_build_overlay_manifest.json').read_text(encoding='utf-8'))
if manifest['version']!='v101.128' or manifest['baseline_zip_sha256']!=EXPECTED: raise SystemExit('overlay authority mismatch')
shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z:
 if z.testzip() is not None: raise SystemExit('baseline corrupt')
 z.extractall(OUT)
for rel in manifest['removed']:
 p=OUT/rel
 if p.exists(): p.unlink()
for row in manifest['changed_or_added']:
 rel=row['path'] if isinstance(row,dict) else row
 if rel in ('metadata/hash_manifest.json','metadata/package_manifest.json'): continue
 s=SRC/rel
 if not s.is_file(): raise SystemExit('overlay source missing '+rel)
 d=OUT/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,d)
# regenerate self-excluding manifests
exclude={'metadata/hash_manifest.json','metadata/package_manifest.json'}
files=[]
for p in sorted(x for x in OUT.rglob('*') if x.is_file()):
 rel=p.relative_to(OUT).as_posix()
 if rel in exclude: continue
 files.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
pkg={'schema':'L24H_PACKAGE_MANIFEST_V1','version':'v101.128','stage':'MEDITEE_RECOVERY_ACCESS_AND_SINGLE_STATE_SYNC_R1','self_exclusion':sorted(exclude),'file_count':len(files),'files':[{'path':x['path'],'size':x['size']} for x in files]}
hm={'schema':'L24H_HASH_MANIFEST_V1','version':'v101.128','stage':'MEDITEE_RECOVERY_ACCESS_AND_SINGLE_STATE_SYNC_R1','self_exclusion':sorted(exclude),'file_count':len(files),'files':files}
(OUT/'metadata/package_manifest.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'metadata/hash_manifest.json').write_text(json.dumps(hm,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','files_total':sum(1 for p in OUT.rglob('*') if p.is_file()),'manifest_files':len(files),'html_sha256':sha(OUT/'index.html')},indent=2))
