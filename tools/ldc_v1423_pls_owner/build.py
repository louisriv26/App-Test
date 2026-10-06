#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,shutil,sys,re,os

ROOT=Path(os.environ.get('GITHUB_WORKSPACE',Path(__file__).resolve().parents[2])).resolve()
SRC=ROOT/'ldc-v142-r15-search-submit-explicit-commit'
DST=ROOT/'ldc-v142-3-pls-owner-prototype'
HERE=Path(__file__).resolve().parent
OLD_APP='v2.19.142-R1B-UX-ACCESS-R15'
NEW_APP='v2.19.142.3-R1B-PLS-SPARSE-OWNER-PROTOTYPE'
OLD_SW='ldc-v2.19.142-R1B-ux-access-r15'
NEW_SW='ldc-v2.19.142.3-R1B-pls-sparse-owner-prototype'
EXPECTED={
 'index.html':'48a8f34a14f92ce20efefbcbb8f08a6203f50ad17acd27d870b8789a9d6f8d8c',
 'sw.js':'89115980fb60874231955eefa33a47e3019eec3a4f4c78799e6f55df7d4d38be',
 'version.json':'b31a207f2e2af49e6e2ba862cf5f7b1d7dae444cf57a8c3fcaed4f4df9481b68',
 'offline_manifest.json':'6b4bb5cf45eff6602b889532b16a999fce97edbe3099357c8407337e36f5cfdd',
 'corpus/manifest.json':'92426c8aaac6fc7c6b8a02b0a7e00cd5870e80b805b411ae64c55e59bec1ad8b',
 'corpus/search_v2_documents.json':'65cfeb954ce9ecaa02c761024f2802436c9fcd07982e20438486d1a793fc195a',
 'corpus/search_v2_entries.json':'ae74aceaa596c72afa5727f1dceb39b4e349ceffbb07e926a6aab30c70a5c54c',
 'corpus/search_v2_jesus_filter.json':'67bd9e80c8ed1702c95072adff9859e7a25a521df14fd1be6efb496aa0ddf31d',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def must_replace(text,old,new,n=1):
    c=text.count(old)
    if c!=n: raise SystemExit(f'PATCH_COUNT {old[:80]!r}: expected {n}, got {c}')
    return text.replace(old,new,n)

if not SRC.exists(): raise SystemExit(f'MISSING_SOURCE {SRC}')
for rel,h in EXPECTED.items():
    p=SRC/rel
    if not p.is_file() or sha(p)!=h: raise SystemExit(f'BASELINE_HASH_FAIL {rel} {sha(p) if p.exists() else "MISSING"}')
if DST.exists(): shutil.rmtree(DST)
shutil.copytree(SRC,DST)
shutil.copy2(HERE/'pls_sparse_owner_v1423.js',DST/'pls_sparse_owner_v1423.js')

# index.html bounded integration
p=DST/'index.html'; s=p.read_text(encoding='utf-8')
s=must_replace(s,"const APP_VERSION = 'v2.19.142-R1B-UX-ACCESS-R15'; // v142 explicit Search submission successor of frozen v141; adaptive single-scroll reveal preserved; corpus/Search payloads and algorithms preserved; Semantic V3 remains fail-closed",
               "const APP_VERSION = 'v2.19.142.3-R1B-PLS-SPARSE-OWNER-PROTOTYPE'; // owner-only App-Test successor of frozen production v142; current-v142 96/72 matched-window retrieval prototype; production v142 unchanged")
s=must_replace(s,"const PUBLIC_VERSION = (APP_VERSION.match(/v2\\.19\\.(\\d+)/)||[])[1] || '142'; // single authoritative public identity derived from APP_VERSION",
               "const PUBLIC_VERSION = (APP_VERSION.match(/v2\\.19\\.(\\d+(?:\\.\\d+)?)/)||[])[1] || '142.3'; // prototype subversion identity derived from APP_VERSION")
s=must_replace(s,"const APP_BUILD = '2026-10-05';","const APP_BUILD = '2026-10-06';")
s=must_replace(s,"const SW_CACHE_VERSION = 'ldc-v2.19.142-R1B-ux-access-r15';",f"const SW_CACHE_VERSION = '{NEW_SW}';")
s=must_replace(s,'<script src="search_semantic_v3_core_r4.js"></script>', '<script src="search_semantic_v3_core_r4.js"></script>\n<script src="pls_sparse_owner_v1423.js"></script>')
s=must_replace(s,"try{const v=localStorage.getItem(SEARCH_INTENT_MODE_KEY);if(v==='words')searchIntentMode='words'; else if(v==='meaning')localStorage.setItem(SEARCH_INTENT_MODE_KEY,'words');}catch(_){ }",
               "try{const v=localStorage.getItem(SEARCH_INTENT_MODE_KEY);if(v==='words'||v==='meaning')searchIntentMode=v;}catch(_){ }")
s=must_replace(s,"if(persist){try{localStorage.setItem(SEARCH_INTENT_MODE_KEY,mode==='meaning'?'words':mode);}catch(_){ }}",
               "if(persist){try{localStorage.setItem(SEARCH_INTENT_MODE_KEY,mode);}catch(_){ }}")
status_anchor="""async function semanticPackV3Status(){\n  // LAB R3 is deliberately fail-closed. A future bound runtime can provide a status hook,\n  // but only a QUALIFIED status may ever make semantic execution available.\n  try{"""
status_repl="""async function semanticPackV3Status(){\n  // Owner/App-Test prototype: expose only the explicitly marked current-v142 retrieval runtime.\n  // The production semantic-pack registry remains fail-closed and unchanged.\n  try{\n    if(window.LDCPLSSparseOwnerV1423&&typeof window.LDCPLSSparseOwnerV1423.status==='function'){\n      const ps=window.LDCPLSSparseOwnerV1423.status();\n      if(ps&&ps.available===true)return {...ps,available:true,calibration_status:'OWNER_PROTOTYPE_ONLY'};\n    }"""
s=must_replace(s,status_anchor,status_repl)
old_meta="const meta=document.getElementById('search-meta');meta.style.display='block';meta.innerHTML=`Recherche par le sens · ${escapeHtml(searchSourceModeLabel(payload.source_mode||supplementMode))} <span class=\"search-mode-badge\">SEARCH-V3 · pack qualifié</span>`;"
new_meta="const meta=document.getElementById('search-meta');meta.style.display='block';const ownerProto=!!payload.prototype_owner_v1423;meta.innerHTML=`Recherche par le sens · ${escapeHtml(searchSourceModeLabel(payload.source_mode||supplementMode))} <span class=\"search-mode-badge\">${ownerProto?'PROTOTYPE PERSONNEL · 96/72':'SEARCH-V3 · pack qualifié'}</span>`;"
s=must_replace(s,old_meta,new_meta)
old_run="""  const status=await semanticPackV3Status();if(!status.available){renderSemanticPackUnavailable(raw,structural,status);return;}\n  if(!window.LDCSemanticPackRegistryV5||typeof window.LDCSemanticPackRegistryV5.search!=='function')throw new Error('SEARCH_V3_SEMANTIC_REGISTRY_NOT_BOUND');\n  const sem=await window.LDCSemanticPackRegistryV5.search(structural.residual||raw,{sourceMode:supplementMode,volMin:structural.volume||searchVolFilter||0,volMax:structural.volume||searchVolFilterMax||0,dateIso:structural.date||null,year:structural.date?0:(structural.year||0),stableRef:structural.ref||null,jesus:!!searchSpeakerFilter,maxResults:20});\n  if(!isSearchActive(searchRunSeq))return;\n  renderSemanticResultsV4(sem,raw,structural);"""
new_run="""  const status=await semanticPackV3Status();if(!status.available){renderSemanticPackUnavailable(raw,structural,status);return;}\n  if(window.LDCPLSSparseOwnerV1423&&typeof window.LDCPLSSparseOwnerV1423.search==='function'){\n    const sem=await window.LDCPLSSparseOwnerV1423.search(structural.residual||raw,{volMin:structural.volume||searchVolFilter||0,volMax:structural.volume||searchVolFilterMax||0,dateIso:structural.date||null,year:structural.date?0:(structural.year||0),stableRef:structural.ref||null,jesus:!!searchSpeakerFilter});\n    if(!isSearchActive(searchRunSeq))return;renderSemanticResultsV4(sem,raw,structural);return;\n  }\n  if(!window.LDCSemanticPackRegistryV5||typeof window.LDCSemanticPackRegistryV5.search!=='function')throw new Error('SEARCH_V3_SEMANTIC_REGISTRY_NOT_BOUND');\n  const sem=await window.LDCSemanticPackRegistryV5.search(structural.residual||raw,{sourceMode:supplementMode,volMin:structural.volume||searchVolFilter||0,volMax:structural.volume||searchVolFilterMax||0,dateIso:structural.date||null,year:structural.date?0:(structural.year||0),stableRef:structural.ref||null,jesus:!!searchSpeakerFilter,maxResults:20});\n  if(!isSearchActive(searchRunSeq))return;\n  renderSemanticResultsV4(sem,raw,structural);"""
s=must_replace(s,old_run,new_run)
old_row="function renderSearchSourceModeRow(){\n  const row=document.getElementById('search-source-mode-row');if(!row)return;row.innerHTML='';row.classList.add('search-foundation-row');"
new_row="function renderSearchSourceModeRow(){\n  const row=document.getElementById('search-source-mode-row');if(!row)return;row.innerHTML='';row.classList.add('search-foundation-row');\n  if(searchIntentMode==='meaning'&&window.LDCPLSSparseOwnerV1423){row.style.display='none';return;}row.style.display='flex';"
s=must_replace(s,old_row,new_row)
s=must_replace(s,"Par le sens fail-closed tant que pack/modèle non qualifiés","Par le sens : prototype personnel v142.3 actif sur App-Test · moteur de production toujours non autorisé")
p.write_text(s,encoding='utf-8')

# service worker identity + shell module
p=DST/'sw.js'; s=p.read_text(encoding='utf-8')
s=s.replace(OLD_SW,NEW_SW)
s=s.replace(OLD_APP,NEW_APP)
needle="'./search_semantic_v3_core_r4.js', './search_semantic_pack_registry_r5.js'"
if s.count(needle)!=1: raise SystemExit('SW_SHELL_ANCHOR_FAIL')
s=s.replace(needle,"'./search_semantic_v3_core_r4.js', './pls_sparse_owner_v1423.js', './search_semantic_pack_registry_r5.js'",1)
p.write_text(s,encoding='utf-8')

# version metadata
p=DST/'version.json'; v=json.loads(p.read_text(encoding='utf-8'))
v['app_version']=NEW_APP; v['public_version']='142.3'; v['page_worker_revision']=NEW_SW
v['public_release']='NOT_AUTHORIZED'; v['public_deployment_authorized']=False
v['pls_owner_prototype_v142_3']={
 'status':'APP_TEST_OWNER_PROTOTYPE_ONLY','base_public_version':'142','production_unchanged':True,
 'retrieval':'CURRENT_V142_96_72_MATCHED_WINDOW_BM25','semantic_dense_claim':False,
 'real_query_smoke_target_entry_ranks':[9,7,1],'date':'2026-10-06'
}
p.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=False)+'\n',encoding='utf-8')

p=DST/'offline_manifest.json'; o=json.loads(p.read_text(encoding='utf-8'))
o['app_version']=NEW_APP; o['page_worker_revision']=NEW_SW
o['pls_owner_prototype_v142_3']={'status':'APP_TEST_OWNER_PROTOTYPE_ONLY','retrieval':'CURRENT_V142_96_72_MATCHED_WINDOW_BM25','production_unchanged':True}
p.write_text(json.dumps(o,ensure_ascii=False,indent=2,sort_keys=False)+'\n',encoding='utf-8')

# QA boundary: corpus must remain byte-identical
for src in (SRC/'corpus').rglob('*'):
    if src.is_file():
        rel=src.relative_to(SRC); dst=DST/rel
        if not dst.is_file() or sha(src)!=sha(dst): raise SystemExit(f'CORPUS_MUTATION {rel}')
# exact changed pre-existing set
src_files={p.relative_to(SRC).as_posix():sha(p) for p in SRC.rglob('*') if p.is_file()}
dst_files={p.relative_to(DST).as_posix():sha(p) for p in DST.rglob('*') if p.is_file()}
removed=sorted(set(src_files)-set(dst_files)); added=sorted(set(dst_files)-set(src_files)); changed=sorted(k for k in src_files.keys()&dst_files.keys() if src_files[k]!=dst_files[k])
if removed: raise SystemExit(f'FILES_REMOVED {removed}')
if added!=['pls_sparse_owner_v1423.js']: raise SystemExit(f'UNEXPECTED_ADDED {added}')
if changed!=['index.html','offline_manifest.json','sw.js','version.json']: raise SystemExit(f'UNEXPECTED_CHANGED {changed}')
# coherence
idx=(DST/'index.html').read_text(encoding='utf-8'); sw=(DST/'sw.js').read_text(encoding='utf-8')
v=json.loads((DST/'version.json').read_text()); o=json.loads((DST/'offline_manifest.json').read_text())
assert NEW_APP in idx and NEW_SW in idx and 'pls_sparse_owner_v1423.js' in idx
assert NEW_APP in sw and NEW_SW in sw and 'pls_sparse_owner_v1423.js' in sw
assert v['app_version']==o['app_version']==NEW_APP
assert v['page_worker_revision']==o['page_worker_revision']==NEW_SW
assert v['public_version']=='142.3'
assert o['content_binding_sha256']=='1fb8d6d8a532806ad6a25b32250091deed174ddb54130f1b05d3da2233a05384'
print(json.dumps({'status':'PASS','target':DST.name,'changed':changed,'added':added,'app_version':NEW_APP,'worker':NEW_SW},indent=2))
