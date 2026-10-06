#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import hashlib,json
root=Path('24h-v120-b7-adversarial')
out=Path('24H_v120_B7_BLIND_ADVERSARIAL_PREPHYSICAL.zip')
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted((x for x in root.rglob('*') if x.is_file()),key=lambda x:str(x.relative_to(root))):
    rel=str(p.relative_to(root)).replace('\\','/')
    zi=ZipInfo(rel,date_time=(1980,1,1,0,0,0));zi.compress_type=ZIP_DEFLATED;zi.external_attr=(0o100644<<16);zi.create_system=3
    z.writestr(zi,p.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
manifest={
 'app':'24H','version':'v120','build_revision':'B7',
 'tree_sha':'bca352b0b86e829c52bbc762273e77581d86a544',
 'release_id':'24h-v120-b7-20261003-blind-accessibility-closure',
 'release_sequence':120000007,
 'package':out.name,'sha256':sha,'bytes':out.stat().st_size,
 'physical_pass_inferred':False,'production_deployment_authority':'NONE'
}
Path('24H_v120_B7_FREEZE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('B7_FREEZE_PASS',sha,out.stat().st_size)
