#!/usr/bin/env python3
"""Package current frozen LDC 142.18 engineering WIP: inspect, curate, rehash, never deploy."""
from __future__ import annotations
import hashlib, json, pathlib, re, shutil, subprocess, tempfile, zipfile, os

VERSION="142.19"
PARENT="7c292d6221bb350fac3aeaa83750b8784706d45c"
PACK_HASH="37dc813c06c4358eb66c0e0c5d6f4fa4c7b8f7e2d775b66c957df68c5f171ef0"
OFFLINE_BINDING="1fb8d6d8a532806ad6a25b32250091deed174ddb54130f1b05d3da2233a05384"
EXPECTED_APP={
 "index.html":"88e5c30d20175956dbf8c0d50d3acaa9b0c5ba5fe38e03132fe6278ae01d24a2",
 "sw.js":"e1325ff22ecbcb91b3da0806917f0744a02d803b1fe414e05eb8d796b33fab3e",
 "version.json":"87f0ecd8c9bd0dd644cc8faf3bb10c28c43fbc03725678d6ab357c52b3e03e07",
 "offline_manifest.json":"cf65b9bd1891ac9f97254e59ec3173a3418e62fc65f3932d32c2b62a5a7eeebb",
 "pls_v16/runtime_v1.mjs":"e5e50095ddf357d91c66f1cef041454d137b025fcc048626568578f17a714831"
}
CHANGED={"index.html","sw.js","version.json","offline_manifest.json"}
ROOT_FILES=(
 "index.html","sw.js","version.json","offline_manifest.json","manifest.json",
 "speech_model.js","display_map.js","interaction_anchor.js","search_normalizer.js",
 "search_engine_v2.js","search_exact_v21.js","search_foundation_v21b.js",
 "search_near_v22.js","search_worker_v2.js","interim_user_state_migration.js",
 "search_semantic_pack_guard_r4.js","search_semantic_v3_core_r4.js",
 "search_semantic_hybrid_r6.js","search_semantic_pack_registry_r6.js"
)
V16_EXTRA=(
 "pls_v16/semantic_pack_manifest.json",
 "pls_v16/runtime_v1.mjs",
 "pls_v16/BINDING_CONTRACT.json",
 "pls_v16/QUALIFIED_PACK_IDENTITY.json",
 "pls_v16/QUALIFIED_SHA256SUMS.txt"
)
OUTPUT="LDC_v142.19_GEOMETRY_CANDIDATE_DO_NOT_DEPLOY.zip"
REPORT="LDC_v142.19_GEOMETRY_CANDIDATE_PACKAGE_AUDIT.json"
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()
def assert_ok(x,msg):
 if not x:raise RuntimeError(msg)
def run(*args):return subprocess.check_output(args,text=True).strip()
def main():
 report={"schema":"ldc-v14219-reader-geometry-candidate-package-v1","status":"BUILDING",
   "tested_git_commit":run("git","rev-parse","HEAD"),
   "base_reader":PARENT,"deployment_authorized":False,"release_status":"UNRELEASED_ENGINEERING_WIP_ONLY",
   "app_test_deployment_authority":"NONE","production_deployment_authority":"NONE",
   "hosted_e16_e19":"OPEN","physical_iphone_ipad":"OPEN","entries":[],"checks":{}}
 def gate(name,v):
  report["checks"][name]=bool(v)
  assert_ok(v,"PACKAGING_CHECK_FAILED:"+name)
 try:
  gate("branch_isolated",run("git","branch","--show-current")=="ldc-v142-19-reader-root-height-fix-wip-20261008")
  gate("protected_corpus_plsv15_searchv2_intact",
   not run("git","diff","--name-only",PARENT,"--","corpus","pls_v15",
    "search_engine_v2.js","search_exact_v21.js","search_foundation_v21b.js",
    "search_near_v22.js","search_worker_v2.js","interim_user_state_migration.js"))
  for file,digest in EXPECTED_APP.items():gate("bounded_modified_or_unchanged_source_sha256:"+file,sha(file)!=digest if file in CHANGED else sha(file)==digest)
  # Verify source-to-successor bounded mutation and complete current page/worker/cache revision contract.
  changed_files=set(run("git","diff","--name-only",PARENT,"--","index.html","sw.js","version.json","offline_manifest.json","manifest.json","speech_model.js","display_map.js","interaction_anchor.js","search_normalizer.js","search_engine_v2.js","search_exact_v21.js","search_foundation_v21b.js","search_near_v22.js","search_worker_v2.js","interim_user_state_migration.js","search_semantic_pack_guard_r4.js","search_semantic_v3_core_r4.js","search_semantic_hybrid_r6.js","search_semantic_pack_registry_r6.js","pls_v16","assets","icons","corpus","pls_v15").splitlines())
  gate("exact_four_bound_runtime_file_mutations",changed_files==CHANGED)
  page=pathlib.Path("index.html").read_text()
  worker=pathlib.Path("sw.js").read_text()
  version_meta=json.loads(pathlib.Path("version.json").read_text())
  offline_meta=json.loads(pathlib.Path("offline_manifest.json").read_text())
  app_id="v2.19.142.19-R1B-READER-GEOMETRY-CANDIDATE"
  worker_id="ldc-v2.19.142.19-R1B-reader-geometry-candidate"
  gate("one_css_root_declaration_removed",("html{overflow-x:hidden;max-width:100vw;}" in page and "html{overflow-x:hidden;max-width:100vw;height:-webkit-fill-available;}" not in page))
  gate("body_flex_contract_unmodified", "body{overflow:hidden;overflow-x:hidden;max-width:100vw;min-height:100vh;min-height:100dvh;min-height:-webkit-fill-available;display:flex;flex-direction:column;padding-bottom:var(--nav-safe-h);}" in page)
  gate("app_html_worker_manifest_version_consistency",version_meta["app_version"]==app_id and version_meta["public_version"]=="142.19" and offline_meta["app_version"]==app_id and "const APP_VERSION = '"+app_id+"';" in page and "m.app_version!=='"+app_id+"'" in worker)
  gate("page_worker_revision_consistency",version_meta["page_worker_revision"]==worker_id and offline_meta["page_worker_revision"]==worker_id and "const SW_CACHE_VERSION = '"+worker_id+"';" in page and "const VERSION = '"+worker_id+"';" in worker)
  gate("worker_two_new_versioned_cache_names",("shell-v2.19.142.19-R1B-reader-geometry-candidate" in worker and "runtime-v2.19.142.19-R1B-reader-geometry-candidate" in worker))
  gate("user_data_schema_unchanged",version_meta["user_data_schema_version"]==json.loads(run("git","show",PARENT+":version.json"))["user_data_schema_version"] and version_meta["user_data_db_internal_version"]==json.loads(run("git","show",PARENT+":version.json"))["user_data_db_internal_version"])
  m=json.loads(pathlib.Path("pls_v16/semantic_pack_manifest.json").read_text())
  offline=json.loads(pathlib.Path("offline_manifest.json").read_text())
  gate("semantic_pack_manifest_immutable",sha("pls_v16/semantic_pack_manifest.json")==PACK_HASH)
  gate("semantic_pack_never_self_authorizes_release",m["app_runtime_wired"] is False and m["deployment_authorized"] is False)
  gate("offline_binding_204",offline["asset_count"]==204 and len(offline["assets"])==204 and offline["content_binding_sha256"]==OFFLINE_BINDING)
  gate("sw_page_worker_revision",offline["page_worker_revision"]==json.loads(pathlib.Path("version.json").read_text())["page_worker_revision"])
  # Packaging is independent from historical reports: verify completed tests on actual source.
  passed={}
  for fn in ["LDC_v142.18_ADVERSARIAL_DOM_QA.json","LDC_v142.18_EXPANDED_ACTUAL_DOM_QA.json",
             "LDC_v142.18_WEBKIT_ACTUAL_APP_QA.json","LDC_v142.18_FAILURE_RETRY_DOM_EVIDENCE.json",
             "LDC_v142.18_SW_ACTUAL_BROWSER_QA.json","LDC_v142.18_SESSION_HIGHLIGHT_DOM_QA.json",
             "LDC_v142.18_COLD_WARM_RETURN_RESOURCES_QA.json","LDC_v142.18_204_ASSET_OFFLINE_DOM_QA.json"]:
   d=json.loads(pathlib.Path(fn).read_text())
   passed[fn]=d["status"]=="PASS" and all(d["checks"].values())
   gate("current_actual_browser_report:"+fn,passed[fn])
  all_tracked=run("git","ls-files","-z").split("\0")
  runtime=set(ROOT_FILES)|set(V16_EXTRA)
  runtime.update(p for p in all_tracked if p.startswith(("assets/","icons/","corpus/")))
  runtime.update(d["path"] for d in m["files"])
  gate("model_asset_count_20",len(m["files"])==20)
  gate("model_total_bytes_213290251",sum(d["bytes"] for d in m["files"])==213290251)
  for d in m["files"]:
   p=d["path"];gate("qualified_asset_exact_sha256:"+p,sha(p)==d["sha256"])
  for d in offline["assets"]:
   p=d["path"];gate("offline_asset_exact_sha256:"+p,sha(p)==d["sha256"])
  script=pathlib.Path("sw.js").read_text()
  shell=re.search(r"const SHELL\s*=\s*\[(.*?)\];",script,re.S)
  gate("worker_shell_parses",bool(shell))
  for rel in re.findall(r"'(\./[^']*)'",shell.group(1)):
   p=rel[2:] if rel!="./" else "index.html"
   gate("worker_shell_resolves:"+p,p in runtime)
  excludes=[p for p in runtime if p.startswith((".github/","tools/")) or p.startswith("LDC_") or p.endswith(".zip")]
  gate("only_explicit_runtime_allowlist",not excludes)
  for p in runtime:gate("all_curated_paths_exist:"+p,pathlib.Path(p).is_file())
  gate("legacy_v15_unneeded_prototype_not_shipped","pls_v15/owner_runtime_v1_5.mjs" not in runtime)
  gate("current_qualified_runtime_included","pls_v16/runtime_v1.mjs" in runtime)
  # All packaged bytes are independently reproduced from source before writing manifest.
  with tempfile.TemporaryDirectory(prefix="ldc-v14219-package-") as tmp:
   stage=pathlib.Path(tmp)/"site";stage.mkdir()
   for p in sorted(runtime):
    f=stage/p;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,f)
    report["entries"].append({"path":p,"bytes":f.stat().st_size,"sha256":sha(f)})
   manifest={"schema":"ldc-curated-wip-package-manifest-v1",
     "app":"Livre du Ciel","source_commit":report["tested_git_commit"],"public_version":"142.19",
     "usage":"UNRELEASED ENGINEERING WIP—DO NOT DEPLOY WITHOUT SEPARATE WRITTEN AUTHORITY",
     "app_test_authority":"NONE","production_authority":"NONE",
     "semantic_manifest_sha256":PACK_HASH,"offline_corpus_binding_sha256":OFFLINE_BINDING,
     "offline_corpus_assets":204,"qualified_model_files":20,
     "packaged_file_count_excluding_manifest":len(report["entries"]),
     "files":report["entries"]}
   mf=stage/"PACKAGE_MANIFEST_SHA256.json"
   mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
   timestamp=(2026,10,8,0,0,0)
   output=pathlib.Path(OUTPUT)
   with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as zip:
    for p in sorted(runtime|{"PACKAGE_MANIFEST_SHA256.json"}):
     info=zipfile.ZipInfo(p,timestamp);info.compress_type=zipfile.ZIP_DEFLATED
     info.external_attr=0o100644<<16
     zip.writestr(info,(stage/p).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
   with tempfile.TemporaryDirectory(prefix="ldc-v14219-extract-") as d:
    with zipfile.ZipFile(output,"r") as zip:
     bad=zip.testzip();gate("zip_internal_crc",bad is None)
     actual=zip.namelist()
     gate("zip_members_exact",len(actual)==len(runtime)+1 and set(actual)==runtime|{"PACKAGE_MANIFEST_SHA256.json"})
     gate("no_member_path_traversal",all(not p.startswith("/") and ".." not in pathlib.PurePosixPath(p).parts for p in actual))
     zip.extractall(d)
    parsed=json.loads((pathlib.Path(d)/"PACKAGE_MANIFEST_SHA256.json").read_text())
    gate("manifest_count_exact",parsed["packaged_file_count_excluding_manifest"]==len(runtime))
    for v in parsed["files"]:
     p=pathlib.Path(d)/v["path"]
     if not(p.is_file() and p.stat().st_size==v["bytes"] and sha(p)==v["sha256"]):
      raise RuntimeError("EXTRACTED_PACKAGE_DIGEST_MISMATCH:"+v["path"])
    gate("every_extracted_member_rehashed",len(parsed["files"])==len(runtime))
   report["zip_sha256"]=sha(output)
   report["zip_size_bytes"]=output.stat().st_size
   report["package_manifest_sha256"]=sha(mf)
   report["file_count_excluding_manifest"]=len(runtime)
   report["status"]="PASS_PACKAGE_INTEGRITY_ONLY_NOT_RELEASE_AUTHORITY"
 finally:
  pathlib.Path(REPORT).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
  print(json.dumps({k:v for k,v in report.items() if k not in ("entries","checks")},indent=2,ensure_ascii=False))
if __name__=="__main__":main()
