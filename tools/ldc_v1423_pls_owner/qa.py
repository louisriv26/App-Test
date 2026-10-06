#!/usr/bin/env python3
from pathlib import Path
import json,re,math,subprocess,sys,base64,os
ROOT=Path(os.environ.get('GITHUB_WORKSPACE',Path(__file__).resolve().parents[2])).resolve()
T=ROOT/'ldc-v142-3-pls-owner-prototype'
# static checks
subprocess.run(['node','--check',str(T/'pls_sparse_owner_v1423.js')],check=True)
subprocess.run(['node','--check',str(T/'sw.js')],check=True)
v=json.loads((T/'version.json').read_text()); o=json.loads((T/'offline_manifest.json').read_text()); idx=(T/'index.html').read_text(); sw=(T/'sw.js').read_text()
assert v['public_version']=='142.3'; assert v['app_version']==o['app_version']; assert v['page_worker_revision']==o['page_worker_revision']; assert v['page_worker_revision'] in idx and v['page_worker_revision'] in sw
assert 'PROTOTYPE PERSONNEL · 96/72' in idx and 'semantic_dense_claim' not in idx
# Run actual JS module with the three genuine queries against staged corpus.
js=ROOT/'tools/ldc_v1423_pls_owner/qa_runtime.js'
subprocess.run(['node',str(js),str(T)],check=True)
print(json.dumps({'status':'PASS','checks':['version_worker_coherence','node_syntax','actual_js_three_query_smoke_9_7_1','corpus_baseline_protected_by_builder']},indent=2))
