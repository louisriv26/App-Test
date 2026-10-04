#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, json, re, shutil

SRC = Path('marie-v47-b1-darkmode')
DST = Path('marie-v48-b2-csp-only-closure')
PREDECESSOR_TREE = '81acbb9f409c7c0e1695b0ab35f33dfdc4978631'
PREDECESSOR_PACKAGE_SHA256 = '29ddfeb04db96dbb7a1e0aebf65954a0f8176b1d6745eac4fef03ccf586f5476'

if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)

def b64sha(text):
    return base64.b64encode(hashlib.sha256(text.encode('utf-8')).digest()).decode('ascii')

def fsha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

idx = DST / 'index.html'
s = idx.read_text(encoding='utf-8')
assert s.count("const APP_VERSION = '47';") == 1
s = s.replace("const APP_VERSION = '47';", "const APP_VERSION = '48';", 1)

# Repair only the release-integrity defect: bind CSP to the exact final inline bytes.
styles = re.findall(r'<style[^>]*>([\s\S]*?)</style>', s, re.I)
scripts = [m.group(1) for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>', s, re.I)]
assert len(styles) == 1
assert len(scripts) == 3
style_tokens = " ".join("'sha256-" + b64sha(x) + "'" for x in styles)
script_tokens = " ".join("'sha256-" + b64sha(x) + "'" for x in scripts)
m = re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]+)(")', s, re.I)
assert m
csp = m.group(2)
csp, n1 = re.subn(r'script-src\s+[^;]*;', 'script-src ' + script_tokens + ';', csp, count=1)
csp, n2 = re.subn(r'style-src\s+[^;]*;', 'style-src ' + style_tokens + ';', csp, count=1)
assert n1 == 1 and n2 == 1
s = s[:m.start(2)] + csp + s[m.end(2):]
idx.write_text(s, encoding='utf-8', newline='\n')

sw = DST / 'sw.js'
w = sw.read_text(encoding='utf-8')
assert w.count("const VERSION = '47';") == 1
w = w.replace("const VERSION = '47';", "const VERSION = '48';", 1)
sw.write_text(w, encoding='utf-8', newline='\n')

# Exact mutation boundary: only index identity/CSP and SW cache identity.
fa = {str(p.relative_to(SRC)): fsha(p) for p in SRC.rglob('*') if p.is_file()}
fb = {str(p.relative_to(DST)): fsha(p) for p in DST.rglob('*') if p.is_file()}
changed = sorted(k for k in set(fa) | set(fb) if fa.get(k) != fb.get(k))
assert changed == ['index.html', 'sw.js'], changed

# Explicitly prove that the rejected B1 placeholder mutation is not present.
final_html = idx.read_text(encoding='utf-8')
assert '.search-input::placeholder { color: var(--muted); }' in final_html
assert '.search-input::placeholder, .note-textarea::placeholder' not in final_html

evidence = {
    'candidate': 'MJV v48/B2',
    'public_version': '48',
    'predecessor': 'MJV v47/B1',
    'predecessor_tree': PREDECESSOR_TREE,
    'predecessor_package_sha256': PREDECESSOR_PACKAGE_SHA256,
    'date': '2026-10-04',
    'root_cause': 'The v47 staging path changed the inline stylesheet and the main inline application script but omitted the Marie CSP hash-rebinding step. The browser therefore rejected the changed style block and changed main script.',
    'correction': [
        'advance runtime/service-worker public version 47 to 48 so the repaired successor has new cache/release identity',
        'recompute script-src hashes for all exact final inline scripts',
        'recompute style-src hash for the exact final inline stylesheet'
    ],
    'rejected_prior_successor': 'MJV v48/B1 mixed this blocker repair with an unproven placeholder CSS mutation and is not governing.',
    'changed_files': changed,
    'index_sha256': fsha(idx),
    'sw_sha256': fsha(sw),
    'script_sha256_base64': [b64sha(x) for x in scripts],
    'style_sha256_base64': [b64sha(x) for x in styles],
    'protected_surfaces': [
        'corpus and corpus migration bytes',
        'manifest and icons/fonts',
        'search, reader, navigation and help semantics',
        'personal-state schema and transaction semantics',
        'backup/export/restore semantics',
        'v47 dark-mode backup-primary hover/focus repair'
    ],
    'corpus_mutation': False,
    'personal_state_schema_mutation': False,
    'production_deployment_authority': 'NONE',
    'physical_gate': 'OPEN'
}
Path('MJV_v48_B2_BUILD_EVIDENCE.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(evidence, ensure_ascii=False, indent=2))