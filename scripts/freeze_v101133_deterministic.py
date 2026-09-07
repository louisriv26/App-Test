#!/usr/bin/env python3
from pathlib import Path
import zipfile,hashlib,json,sys
FIXED_DT=(2026,9,4,0,0,0)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def freeze(root,out):
 root=Path(root);out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.unlink()
 paths=sorted(p for p in root.rglob('*') if p.is_file())
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9,strict_timestamps=True) as z:
  for p in paths:
   rel=p.relative_to(root).as_posix(); data=p.read_bytes();zi=zipfile.ZipInfo(rel,date_time=FIXED_DT)
   zi.compress_type=zipfile.ZIP_DEFLATED;zi.create_system=3;zi.external_attr=(0o100644<<16);zi.flag_bits|=0x800
   z.writestr(zi,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 with zipfile.ZipFile(out) as z:
  bad=z.testzip();members=len(z.infolist())
  if bad is not None:raise RuntimeError(bad)
 return {'zip':str(out),'sha256':sha(out),'members':members,'bytes':out.stat().st_size}
if __name__=='__main__': print(json.dumps(freeze(sys.argv[1],sys.argv[2]),indent=2))
