#!/usr/bin/env python3
from pathlib import Path
import sys,zipfile,hashlib,shutil,json
BASE=Path(sys.argv[1]); OUT=Path(sys.argv[2]); SRC=Path(sys.argv[3]) if len(sys.argv)>3 else Path(__file__).resolve().parents[1]; ZIP_OUT=Path(sys.argv[4]) if len(sys.argv)>4 and sys.argv[4] else None
EXPECTED_BASE='2959dfb832521af6f810d5f6b30ee187448aa799900993fd54ceae2b7c252b0d'; FIXED=(2026,8,29,0,0,0)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(BASE)!=EXPECTED_BASE: raise SystemExit(f'FAIL_BASELINE_IDENTITY {sha(BASE)}')
ov=json.loads((SRC/'metadata/full_build_overlay_manifest.json').read_text(encoding='utf-8'))
shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z:z.extractall(OUT)
for rel in ov.get('removed',[]):
 p=OUT/rel
 if p.is_dir():shutil.rmtree(p)
 elif p.exists():p.unlink()
for rel in ov.get('changed_or_added',[]):
 src=SRC/rel;dst=OUT/rel
 if not src.is_file():raise SystemExit(f'FAIL_OVERLAY_SOURCE_MISSING {rel}')
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
def fmap(r):return {p.relative_to(r).as_posix():sha(p) for p in r.rglob('*') if p.is_file()}
a=fmap(SRC);b=fmap(OUT)
if a!=b:
 raise SystemExit('FAIL_FULL_TREE_REPRODUCTION '+json.dumps({'only_source':sorted(set(a)-set(b))[:30],'only_output':sorted(set(b)-set(a))[:30],'changed':sorted(k for k in set(a)&set(b) if a[k]!=b[k])[:30]},ensure_ascii=False))
hm=json.loads((OUT/'metadata/hash_manifest.json').read_text());listed={x['path']:(x['size'],x['sha256']) for x in hm['files']};ex=set(hm.get('self_exclusion',[]));actual={}
for p in OUT.rglob('*'):
 if p.is_file():
  rel=p.relative_to(OUT).as_posix()
  if rel not in ex:actual[rel]=(p.stat().st_size,sha(p))
if listed!=actual:raise SystemExit('FAIL_HASH_MANIFEST_RECONCILIATION')
if ZIP_OUT:
 ZIP_OUT.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(ZIP_OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted((x for x in OUT.rglob('*') if x.is_file()),key=lambda x:x.relative_to(OUT).as_posix()):
   rel=p.relative_to(OUT).as_posix();zi=zipfile.ZipInfo(rel,FIXED);zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=(0o100644&0xffff)<<16;z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'status':'PASS_FULL_PACKAGE_REPRODUCTION','baseline_sha256':EXPECTED_BASE,'file_count':len(a),'zip_sha256':sha(ZIP_OUT) if ZIP_OUT else None}))
