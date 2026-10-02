#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import hashlib,json
apps=[
 ('24H_v120_B4','24h-v120-b4-darkmode','fa26ec9bf92f9d5ff8551113ad43d26fda45168e'),
 ('LDC_v136','ldc-v136-r9-darkmode','c8a300b6167f015c4895572c900d989ff63bd386'),
 ('LETTRES_v2.12','lettres-v2.12-b1-darkmode','03617ce508bb9cce7e114c1cec4aa40c3a0b6dc9'),
 ('MJV_v47','marie-v47-b1-darkmode','81acbb9f409c7c0e1695b0ab35f33dfdc4978631')]
out=Path('final-dark-mode-freeze');out.mkdir(exist_ok=True)
rows=[]
for label,src,tree in apps:
 root=Path(src); target=out/(label+'.zip')
 with ZipFile(target,'w',ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted((x for x in root.rglob('*') if x.is_file()),key=lambda x:str(x.relative_to(root))):
   rel=str(p.relative_to(root)).replace('\\','/')
   zi=ZipInfo(rel,date_time=(1980,1,1,0,0,0));zi.compress_type=ZIP_DEFLATED;zi.external_attr=(0o100644<<16);zi.create_system=3
   z.writestr(zi,p.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
 sha=hashlib.sha256(target.read_bytes()).hexdigest()
 rows.append({'label':label,'source_route':src,'tree_sha':tree,'package':target.name,'sha256':sha,'bytes':target.stat().st_size})
manifest={'freeze_date':'2026-10-02','production_deployment_authority':'NONE','physical_pass_inferred':False,'packages':rows}
(out/'FREEZE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(out/'SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['package']+'\n' for r in rows),encoding='utf-8')
for r in rows: print('FREEZE',r['label'],r['tree_sha'],r['sha256'],r['bytes'])
