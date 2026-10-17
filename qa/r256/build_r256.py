#!/usr/bin/env python3
"""R256: exact minimal repair for R255 offline manifest/content binding mismatch.
Only creates a QA candidate in a temporary checkout. Does NOT deploy to APP TEST / MAIN.
"""
import hashlib, json, os, pathlib, sys, zipfile, shutil
P=pathlib.Path(__file__).resolve().parents[2]
OLD_APP="v2.19.142.45-R1B-UNIFIED"
NEW_APP="v2.19.142.46-R1B-UNIFIED"
OLD_SW="ldc-v2.19.142.45-r1b-unified"
NEW_SW="ldc-v2.19.142.46-r1b-unified"
OLD_BIND="38833ef76d248a6b55c1a09d460939781c30e081a2d7bbd27ed47aa7d9ed12ee"
sha=lambda x:hashlib.sha256(x).hexdigest()
def read(p):return (P/p).read_text(encoding="utf-8")
def write(p,s):(P/p).write_text(s,encoding="utf-8")
def obj(p):return json.loads(read(p))
def dump(p,o):write(p,json.dumps(o,ensure_ascii=False,indent=2)+"\n")
def change_exact(p,old,new,count=1):
    s=read(p);n=s.count(old)
    assert n==count,(p,"expected",count,"found",n,old[:70])
    write(p,s.replace(old,new))
m=obj("offline_manifest.json")
assert m["app_version"]==OLD_APP
assert m["page_worker_revision"]==OLD_SW
assert m["content_binding_sha256"]==OLD_BIND
assert m["asset_count"]==205 and len(m["assets"])==205
assert sum(a["path"]=="pls_v16/patch_r255.json" for a in m["assets"])==1
assert all(a["path"]!="pls_v16/patch_r198.json" for a in m["assets"])
canonical=json.dumps({
 "assets":[{"bytes":int(a["bytes"]),"path":str(a["path"]),"sha256":str(a["sha256"])} for a in m["assets"]],
 "corpus_generation":m["corpus_generation"],
 "corpus_manifest_sha256":m["corpus_manifest_sha256"],
 "schema":m["content_binding_schema"]
},separators=(",",":"),ensure_ascii=False)
newbind=hashlib.sha256(canonical.encode("utf-8")).hexdigest()
assert newbind!=OLD_BIND
assert m["content_binding_schema"]=="ldc-offline-content-binding-v2"
assert newbind==sha(canonical.encode("utf-8"))
m["content_binding_sha256"]=newbind;m["app_version"]=NEW_APP;m["page_worker_revision"]=NEW_SW
m["r256_sw_binding_repair"]={
 "scope":"APP_TEST_ONLY_QA_CANDIDATE_LOCAL_HOLD",
 "root_cause":"R255 replaced offline manifest asset patch_r198 by patch_r255 without recalculating content_binding_sha256",
 "calculation":"SHA256(JSON.stringify({assets:[{bytes,path,sha256},...],corpus_generation,corpus_manifest_sha256,schema}))",
 "historical_manifest_digest":OLD_BIND,
 "new_manifest_digest":newbind,
 "offline_assets_preserved":205,
 "user_data_mutations":0,
 "status":"STATIC_CONTRACT_REPAIRED_BROWSER_QA_PENDING"}
dump("offline_manifest.json",m)
change_exact("sw.js",f"const VERSION = '{OLD_SW}';",f"const VERSION = '{NEW_SW}';")
change_exact("sw.js",f"const APP_VERSION = '{OLD_APP}';",f"const APP_VERSION = '{NEW_APP}';")
change_exact("sw.js",f"const OFFLINE_CONTENT_BINDING = '{OLD_BIND}';",f"const OFFLINE_CONTENT_BINDING = '{newbind}';")
# R256 adversarial browser QA: make message-event lifetime extend through skipWaiting promise.
change_exact("sw.js", "if(e.data&&e.data.type==='SKIP_WAITING'){self.skipWaiting();return;}", "if(e.data&&e.data.type==='SKIP_WAITING'){const activation=self.skipWaiting();e.waitUntil(Promise.race([activation,new Promise(resolve=>setTimeout(resolve,1800))]));return;}")
change_exact("index.html",f"const APP_VERSION = '{OLD_APP}';",f"const APP_VERSION = '{NEW_APP}';")
change_exact("index.html",f"const SW_CACHE_VERSION = '{OLD_SW}';",f"const SW_CACHE_VERSION = '{NEW_SW}';")
change_exact("index.html",f"const OFFLINE_CONTENT_BINDING = '{OLD_BIND}';",f"const OFFLINE_CONTENT_BINDING = '{newbind}';")
change_exact("index.html","const APP_BUILD = '2026-10-16';","const APP_BUILD = '2026-10-17';")
v=obj("version.json")
assert v["app_version"]==OLD_APP and v["page_worker_revision"]==OLD_SW
assert v["offline_content_binding_sha256"]==OLD_BIND
v["app_version"]=NEW_APP
v["page_worker_revision"]=NEW_SW
v["offline_content_binding_sha256"]=newbind
v["public_version"]="142.46"
v["build_date"]="2026-10-17"
v["r256_local_qa_candidate"]={
 "status":"LOCAL_HOLD_DO_NOT_DEPLOY",
 "introduced_on":"2026-10-17",
 "parent_version":OLD_APP,
 "root_cause":"R255 offline_manifest canonical SHA mismatch prevented service worker installation",
 "asset_integrity":"205 records unchanged; only binding digest recalculated",
 "user_storage_schema":"UNCHANGED",
 "application_runtime":"Reader, corpus, semantic indices and selection byte-identical apart from published version metadata",
 "physical_ios":"NOT_RUN",
 "main_deployment":"FORBIDDEN"}
dump("version.json",v)
pkg=obj("PACKAGE_MANIFEST_SHA256.json")
assert len(pkg["files"])==278
expected=set(x["path"] for x in pkg["files"])
assert all((P/p).is_file() for p in expected)
changed=[]
for record in pkg["files"]:
    p=record["path"];raw=(P/p).read_bytes()
    updated={"bytes":len(raw),"sha256":sha(raw)}
    if any(record[k]!=updated[k] for k in updated):changed.append(p)
    record.update(updated)
assert set(changed)=={"index.html","sw.js","offline_manifest.json","version.json"},changed
pkg["public_version"]="142.46"
pkg["r256_sw_binding_repair"]={
 "scope":"LOCAL_HOLD_QA_ONLY",
 "proven":["SW install at v142.45 fails: offline manifest content binding invalide", "no changes to 205 offline asset entries or any corpus file"],
 "actual_binding_sha256":newbind,
 "new_version":NEW_APP,
 "changed_paths":changed,
 "no_deployment_authority":True}
dump("PACKAGE_MANIFEST_SHA256.json",pkg)
finalm=obj("offline_manifest.json")
assert sha(json.dumps({
 "assets":[{"bytes":int(a["bytes"]),"path":str(a["path"]),"sha256":str(a["sha256"])} for a in finalm["assets"]],
 "corpus_generation":finalm["corpus_generation"],
 "corpus_manifest_sha256":finalm["corpus_manifest_sha256"],
 "schema":finalm["content_binding_schema"]
},separators=(",",":"),ensure_ascii=False).encode())==newbind
for record in pkg["files"]:
    d=(P/record["path"]).read_bytes()
    assert len(d)==record["bytes"] and sha(d)==record["sha256"],record["path"]
out="/tmp/LDC_R256_v14246_SW_OFFLINE_BINDING_QA_LOCAL_HOLD.zip"
with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for path in ["PACKAGE_MANIFEST_SHA256.json"]+sorted(expected):
    z.write(P/path,path)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None and len(z.namelist())==279
report={
 "candidate":NEW_APP,"status":"LOCAL_HOLD","sha256":sha(pathlib.Path(out).read_bytes()),
 "size":os.path.getsize(out),"zip_files":279,"offline_assets":len(m["assets"]),
 "offline_binding_new":newbind,"offline_binding_old":OLD_BIND,
 "changed_paths":sorted(changed)+["PACKAGE_MANIFEST_SHA256.json"],
 "other_274_files":"BYTE_IDENTICAL_TO_R255",
 "no_external_writes":True
}
pathlib.Path("r256-candidate-build.json").write_text(json.dumps(report,indent=2)+"\n")
print("R256_BUILD_RESULT "+json.dumps(report,ensure_ascii=False),flush=True)
