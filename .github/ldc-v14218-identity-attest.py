#!/usr/bin/env python3
"""Fail-closed exact-source asset and identity attestation for isolated LDC 142.18 WIP."""
from __future__ import annotations
import hashlib,json,pathlib,re,subprocess,sys

EXPECTED_MAIN="572d9df7927765b575a76eaee98fd3cc9d455e74"
READER="56a306997a37ab975a573774a97fa976a40ffe40"
SEMANTIC="39b9ec90ab3b2199b1738e96b353cc6b27d9cac0"
EXPECTED_PACK="37dc813c06c4358eb66c0e0c5d6f4fa4c7b8f7e2d775b66c957df68c5f171ef0"
EXPECTED_BINDING="1fb8d6d8a532806ad6a25b32250091deed174ddb54130f1b05d3da2233a05384"
VERSION="v2.19.142.18-R1B-READER-SEMANTIC-INTEGRATION-WIP"
SW="ldc-v2.19.142.18-R1B-reader-semantic-integration-wip"
def command(*args): return subprocess.check_output(args,text=True).strip()
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
 return h.hexdigest()
def main():
 status=dict(schema="ldc-v14218-exact-current-source-asset-attestation-v1",status="INCOMPLETE",
   head=command("git","rev-parse","HEAD"),branch=command("git","branch","--show-current"),
   authoritative_reader=READER,authoritative_semantic=SEMANTIC,
   deployment_authorized=False,physical_iphone_ipad="OPEN",hosted_origin_e16_e19="OPEN",
   curated_release_zip="NOT_CREATED",checks={},sha256={},git_blob={},bytes={},assets=[])
 def yes(key,condition):
  status["checks"][key]=bool(condition)
  if not condition:raise RuntimeError("ATTESTATION_FAIL:"+key)
 try:
  yes("proper_branch",status["branch"]=="ldc-v142-18-reader-semantic-integration-wip-20261008")
  yes("main_immutable",command("git","rev-parse","origin/main")==EXPECTED_MAIN)
  yes("reader_immutable",command("git","rev-parse","origin/ldc-v142.17-reader-transaction-repair-candidate")==READER)
  yes("semantic_immutable",command("git","rev-parse","origin/ldc-v142-16-search-integrity-wip-20261007")==SEMANTIC)
  protected=["corpus","pls_v15","search_engine_v2.js","search_exact_v21.js",
   "search_foundation_v21b.js","search_near_v22.js","search_worker_v2.js","interim_user_state_migration.js"]
  yes("protected_byte_delta_empty",not command("git","diff","--name-only",READER,"--",*protected))
  paths=["index.html","sw.js","version.json","offline_manifest.json",
   "pls_v16/semantic_pack_manifest.json","pls_v16/runtime_v1.mjs",
   "search_semantic_pack_guard_r4.js","search_semantic_hybrid_r6.js","search_semantic_pack_registry_r6.js"]
  for path in paths:
   fp=pathlib.Path(path)
   yes("path_exists_"+path,fp.is_file())
   status["sha256"][path]=sha(fp)
   status["git_blob"][path]=command("git","hash-object",path)
   status["bytes"][path]=fp.stat().st_size
  yes("pack_manifest_frozen",status["sha256"]["pls_v16/semantic_pack_manifest.json"]==EXPECTED_PACK)
  m=json.loads(pathlib.Path("pls_v16/semantic_pack_manifest.json").read_bytes())
  yes("pack_verified_v16_status",m["status"]=="QUALIFIED__ACTIVATION_ELIGIBLE_AFTER_GUARD_VERIFICATION")
  yes("frozen_pack_flag_immutable",m["app_runtime_wired"] is False and m["deployment_authorized"] is False)
  yes("pack_bind_matches_current_corpus",m["bindings"]["offline_content_binding_sha256"]==EXPECTED_BINDING)
  yes("qualified_file_count_20",len(m["files"])==20)
  size=0
  for d in m["files"]:
   path=d["path"];f=pathlib.Path(path)
   yes("exists_"+path,f.is_file())
   yes("bytes_"+path,f.stat().st_size==d["bytes"])
   yes("sha256_"+path,sha(f)==d["sha256"])
   status["assets"].append(dict(path=path,bytes=d["bytes"],sha256=d["sha256"]))
   size+=d["bytes"]
  yes("frozen_assets_total_213290251",size==213290251)
  v=json.loads(pathlib.Path("version.json").read_bytes())
  off=json.loads(pathlib.Path("offline_manifest.json").read_bytes())
  html=pathlib.Path("index.html").read_text()
  sw=pathlib.Path("sw.js").read_text()
  yes("html_identity",f"const APP_VERSION = '{VERSION}';" in html and f"const SW_CACHE_VERSION = '{SW}';" in html)
  yes("worker_identity",f"const VERSION = '{SW}';" in sw)
  yes("version_manifest_revision_identity",v["app_version"]==VERSION and v["page_worker_revision"]==SW)
  yes("offline_manifest_revision_identity",off["app_version"]==VERSION and off["page_worker_revision"]==SW)
  yes("offline204_count",off["asset_count"]==204 and len(off["assets"])==204)
  yes("offline_corpus_binding",off["content_binding_sha256"]==EXPECTED_BINDING)
  canonical=dict(assets=[dict(bytes=int(a["bytes"]),path=a["path"],sha256=a["sha256"]) for a in off["assets"]],
   corpus_generation=off["corpus_generation"],corpus_manifest_sha256=off["corpus_manifest_sha256"],schema="ldc-offline-content-binding-v2")
  actual=hashlib.sha256(json.dumps(canonical,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
  status["recomputed_offline_binding_sha256"]=actual
  yes("binding_recomputed_exactly",actual==EXPECTED_BINDING)
  m0=re.search(r"const SHELL\s*=\s*\[(.*?)\];",sw,re.S)
  yes("worker_has_shell_list",bool(m0))
  shell=m0.group(1)
  for req in ["search_semantic_pack_guard_r4.js","search_semantic_v3_core_r4.js",
              "search_semantic_hybrid_r6.js","search_semantic_pack_registry_r6.js",
              "pls_v16/runtime_v1.mjs"]:
   yes("shell_"+req,req in shell)
  yes("heavy_213mb_not_mandatory_shell",not any(x in shell for x in ["model_int8.onnx","metadata.jsonl","vectors.i8","jesus_mask.bits"]))
  yes("bounded_50_mb_runtime_corpus_cache", "RUNTIME_MAX_BYTES = 50331648" in sw)
  yes("cache_corpus_unchanged",off["content_binding_sha256"]==EXPECTED_BINDING)
  status["status"]="PASS_SOURCE_ONLY"
 except Exception as e:
  status["error"]=str(e);status["status"]="FAIL_SOURCE";raise
 finally:
  pathlib.Path("LDC_v142.18_SOURCE_IDENTITY_ATTESTATION.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n")
  print(json.dumps({k:v for k,v in status.items() if k!="assets"},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
