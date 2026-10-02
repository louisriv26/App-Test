
from pathlib import Path
import json,re,hashlib,base64
root=Path('24h-v120-b6-blind-closure')
live=Path('24h-v119-b1-governed-r4')
findings=[]
def add(sev,code,msg,**kw): findings.append(dict(severity=sev,code=code,message=msg,**kw))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
# Protected parity and shell identity
allowed={'index.html','luisa_24_heures.html','manifest.json','sw.js','version.json'}
a={str(p.relative_to(live)):sha(p) for p in live.rglob('*') if p.is_file()}
b={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}
changed={k for k in set(a)|set(b) if a.get(k)!=b.get(k)}
if changed!=allowed: add('error','MUTATION-BOUNDARY','Changed-file set differs from bounded shell/metadata surface',changed=sorted(changed))
if (root/'index.html').read_bytes()!=(root/'luisa_24_heures.html').read_bytes(): add('error','SHELL-DIVERGENCE','index.html and canonical shell differ')
shell_sha=sha(root/'luisa_24_heures.html')
manifest=json.load(open(root/'manifest.json',encoding='utf-8'))
version=json.load(open(root/'version.json',encoding='utf-8'))
sw=(root/'sw.js').read_text(encoding='utf-8')
page=(root/'index.html').read_text(encoding='utf-8')
def one(text,pat,label):
 m=re.search(pat,text)
 if not m: add('error','IDENTITY-MISSING',f'Missing {label}'); return None
 return m.group(1)
page_id={
 'app_version':one(page,r"const APP_VERSION = '([^']+)'",'page APP_VERSION'),
 'build_revision':one(page,r"const BUILD_REVISION = '([^']+)'",'page BUILD_REVISION'),
 'release_sequence':int(one(page,r"const APP_RELEASE_SEQUENCE = (\d+)",'page release sequence') or 0),
 'release_id':one(page,r"const APP_RELEASE_ID = '([^']+)'",'page release id')
}
sw_id={
 'app_version':one(sw,r"const APP_VERSION = '([^']+)'",'SW APP_VERSION'),
 'build_revision':one(sw,r"const BUILD_REVISION = '([^']+)'",'SW BUILD_REVISION'),
 'release_sequence':int(one(sw,r"const RELEASE_SEQUENCE = (\d+)",'SW release sequence') or 0),
 'release_id':one(sw,r"const RELEASE_ID = '([^']+)'",'SW release id'),
 'shell_sha':one(sw,r"const CANONICAL_SHELL_SHA256 = '([0-9a-f]{64})'",'SW shell hash')
}
active={
 'page':page_id,'sw':sw_id,
 'manifest':{k:manifest.get(k) for k in ['version','build_revision','release_sequence','release_id','start_url']},
 'version':{k:version.get(k) for k in ['app_version','build_revision','release_sequence','release_id','canonical_shell_sha256','real_device_status','overall_release_status']}
}
expected={'app_version':manifest.get('version'),'build_revision':manifest.get('build_revision'),'release_sequence':manifest.get('release_sequence'),'release_id':manifest.get('release_id')}
for src,d in [('page',page_id),('sw',sw_id)]:
 for k in ['app_version','build_revision','release_sequence','release_id']:
  if d.get(k)!=expected.get(k): add('error','RELEASE-IDENTITY-MISMATCH',f'{src}.{k} differs from manifest',source=src,key=k,value=d.get(k),manifest=expected.get(k))
for k in ['app_version','build_revision','release_sequence','release_id']:
 if version.get(k)!=expected.get(k): add('error','VERSION-METADATA-MISMATCH',f'version.json {k} differs from manifest',key=k,value=version.get(k),manifest=expected.get(k))
if version.get('canonical_shell_sha256')!=shell_sha:add('error','VERSION-SHELL-HASH','version.json canonical shell SHA does not match bytes',actual=shell_sha,declared=version.get('canonical_shell_sha256'))
if sw_id.get('shell_sha')!=shell_sha:add('error','SW-SHELL-HASH','SW canonical shell SHA does not match bytes',actual=shell_sha,declared=sw_id.get('shell_sha'))
# CSP exact inline blocks
cspm=re.search(r'Content-Security-Policy" content="([^"]+)"',page)
if not cspm: add('error','CSP-MISSING','No CSP meta policy')
else:
 csp=cspm.group(1)
 def tokens(dir):
  m=re.search(r'(?:^|;\s*)'+re.escape(dir)+r'\s+([^;]+)',csp)
  return set(re.findall(r"'sha256-([^']+)'",m.group(1))) if m else set()
 for tag,dir in [('script','script-src-elem'),('style','style-src-elem')]:
  blocks=re.findall(fr'<{tag}(?![^>]*\bsrc=)[^>]*>(.*?)</{tag}>',page,re.S|re.I)
  actual={base64.b64encode(hashlib.sha256(x.encode()).digest()).decode() for x in blocks}
  declared=tokens(dir)
  miss=sorted(actual-declared)
  if miss:add('error','CSP-HASH-MISSING',f'{dir} does not authorize all inline {tag} blocks',missing=miss)
# Exact scope-derived cache expression must not be escaped/literal.
if r'\\${CACHE_PREFIX}' in sw:
    add('error','SW-CACHE-LITERAL','SW CACHE_NAME contains escaped CACHE_PREFIX interpolation')
if 'const CACHE_NAME = `${CACHE_PREFIX}v120-b6`;' not in sw:
    add('error','SW-CACHE-SCOPE','SW CACHE_NAME is not the exact scope-derived B6 expression')
# SW precache paths all exist
m=re.search(r"const ASSETS = \[(.*?)\];",sw,re.S)
if m:
 assets=re.findall(r"'([^']+)'",m.group(1))
 for x in assets:
  p=root/x.removeprefix('./')
  if not p.exists():add('error','PRECACHE-MISSING','SW precache asset missing',asset=x)
else:add('error','PRECACHE-LIST-MISSING','SW ASSETS list not found')
# Active staleness/contradictions
for key in ['real_device_status','overall_release_status']:
 val=str(version.get(key,''))
 if 'B1' in val and expected['build_revision']!='B1':add('error','ACTIVE-METADATA-STALE',f'{key} still refers to B1',key=key,value=val)
# Current external gates should name current candidate or predecessor->current rather than obsolete v119/B1 as target.
for key in ['known_blockers','external_open_gates']:
 vals=version.get(key) or []
 stale=[v for v in vals if 'v119/B1' in str(v) and 'v120' not in str(v)]
 if stale:add('warning','OPEN-GATE-STALE',f'{key} contains prior-candidate wording',key=key,items=stale)
out={'candidate_tree':'977b1d9c9475988d03aa6debb78cd9370e6e1192','shell_sha256':shell_sha,'active_identity':active,'changed_files':sorted(changed),'findings':findings}
Path('24h-blind-adversarial-b6-static.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('STATIC_FINDINGS',len(findings))
for f in findings: print(json.dumps(f,ensure_ascii=False))
