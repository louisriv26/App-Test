#!/usr/bin/env python3
"""Provisional 142.18 version/SW atomic binding reconciliation; no publishing."""
import hashlib,json,pathlib,re,subprocess
READER="56a306997a37ab975a573774a97fa976a40ffe40"
SEARCH="39b9ec90ab3b2199b1738e96b353cc6b27d9cac0"
MERGED_REPAIRED_GIT_BLOB="c4447294c30132cc0e07f4a966e4f2e05118e1a3"
OLD="v2.19.142.17-R1B-READER-TRANSACTION-REPAIR"
NEW="v2.19.142.18-R1B-READER-SEMANTIC-INTEGRATION-WIP"
OLD_SW="ldc-v2.19.142.17-R1B-reader-transaction-repair"
NEW_SW="ldc-v2.19.142.18-R1B-reader-semantic-integration-wip"
BINDING="1fb8d6d8a532806ad6a25b32250091deed174ddb54130f1b05d3da2233a05384"
MANIFEST_HASH="37dc813c06c4358eb66c0e0c5d6f4fa4c7b8f7e2d775b66c957df68c5f171ef0"
paths=[pathlib.Path(p) for p in ["index.html","sw.js","version.json","offline_manifest.json"]]
def b3(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hash_blob(p):return subprocess.check_output(["git","hash-object",str(p)],text=True).strip()
def replace_one(s,a,b,label):
    assert s.count(a)==1,(label,a,s.count(a))
    return s.replace(a,b)
def main():
    assert hash_blob(paths[0])==MERGED_REPAIRED_GIT_BLOB,"integrated source mutated after tested QA"
    old_sw=paths[1].read_text()
    old_version=json.loads(paths[2].read_text())
    old_off=json.loads(paths[3].read_text())
    assert old_version["app_version"]==OLD
    assert old_off["app_version"]==OLD
    assert old_off["asset_count"]==204 and old_off["content_binding_sha256"]==BINDING
    before={str(p):b3(p) for p in paths}
    index=paths[0].read_text()
    index=replace_one(index,"const APP_VERSION = '"+OLD+"'; // bounded successor of frozen v142.15 after physical iPhone Reader findings; corpus/search/provenance/user-state schemas preserved",
       "const APP_VERSION = '"+NEW+"'; // WIP candidate, not deployed or authorized; preserves v142.17 Reader ownership and integrates qualified PLS v16", "app html version")
    index=replace_one(index,"|| '142.17'; // single authoritative public identity derived from APP_VERSION",
       "|| '142.18'; // single authoritative public identity derived from APP_VERSION","public version fallback")
    index=replace_one(index,"const SW_CACHE_VERSION = '"+OLD_SW+"';",
       "const SW_CACHE_VERSION = '"+NEW_SW+"';","app cache version")
    assert "search_semantic_pack_guard_r4.js" in index and "pls_v16/runtime_v1.mjs" in index
    sw=old_sw
    sw=replace_one(sw,"const VERSION = '"+OLD_SW+"';","const VERSION = '"+NEW_SW+"';","worker version")
    sw=replace_one(sw,"const SHELL_CACHE = ${SCOPE_CACHE_PREFIX}shell-v2.19.142.17-R1B-reader-transaction-repair","const SHELL_CACHE = ${SCOPE_CACHE_PREFIX}shell-v2.19.142.18-R1B-reader-semantic-integration-wip","shell cache") if False else sw
    sw=replace_one(sw,"const SHELL_CACHE = `${SCOPE_CACHE_PREFIX}shell-v2.19.142.17-R1B-reader-transaction-repair`;","const SHELL_CACHE = `${SCOPE_CACHE_PREFIX}shell-v2.19.142.18-R1B-reader-semantic-integration-wip`;","shell cache")
    sw=replace_one(sw,"const RUNTIME_CACHE = `${SCOPE_CACHE_PREFIX}runtime-v2.19.142.17-R1B-reader-transaction-repair`;","const RUNTIME_CACHE = `${SCOPE_CACHE_PREFIX}runtime-v2.19.142.18-R1B-reader-semantic-integration-wip`;","runtime cache")
    old_scripts="'./search_semantic_pack_guard_r3.js', './search_semantic_v3_core_r4.js', './search_semantic_pack_registry_r5.js', './search_semantic_pack_lifecycle_r5.js', './pls_v15/hybrid_core_v1_5.js', './pls_v15/owner_runtime_v1_5.mjs'"
    new_scripts="'./search_semantic_pack_guard_r4.js', './search_semantic_v3_core_r4.js', './search_semantic_hybrid_r6.js', './search_semantic_pack_registry_r6.js', './pls_v16/runtime_v1.mjs'"
    sw=replace_one(sw,old_scripts,new_scripts,"worker shell scripts")
    sw=replace_one(sw,"m.app_version!=='"+OLD+"'","m.app_version!=='"+NEW+"'","worker offline-manifest compatibility")
    assert old_sw.count(OLD)==1 and sw.count(NEW)==1,"worker version string identity not unique"
    assert sw.count(BINDING)==old_sw.count(BINDING),"corpus binding altered"
    assert "50331648" in sw and "50331648" in old_sw,"runtime corpus cache limit altered"
    old_off["app_version"]=NEW
    old_off["page_worker_revision"]=NEW_SW
    # Preserve the complete 204-asset immutable list and content-binding bytes.
    off=json.dumps(old_off,ensure_ascii=False,indent=2)+"\n"
    check_off=json.loads(off)
    assert check_off["assets"]==json.loads(paths[3].read_text())["assets"]
    assert check_off["content_binding_sha256"]==BINDING
    assert check_off["page_worker_revision"]==NEW_SW
    ver=old_version
    ver["app_version"]=NEW
    ver["page_worker_revision"]=NEW_SW
    ver["public_version"]="142.18"
    ver["baseline_candidate_version"]=OLD
    ver["baseline_candidate_sha256"]=None
    ver["build_date"]="2026-10-08"
    ver["current_release_authority"]="V142_18_ENGINEERING_WIP_ONLY__APP_TEST_DEPLOYMENT_AUTHORITY_NONE__PRODUCTION_DEPLOYMENT_AUTHORITY_NONE"
    ver["current_runtime_browser_validation"]="V142_18_INITIAL_ACTUAL_CHROMIUM_NAVIGATION_PASS__INDEPENDENT_V14218_READER_MODES_POSITIVE_NEGATIVES_19_OF_19_PASS_ON_PRE_METADATA_BYTES__NEW_METADATA_AND_SW_REQUIRE_EXACT_RETEST__HOSTED_WEBKIT_PHYSICAL_OPEN"
    ver["external_validation_status"]="V142_18_HOSTED_APP_TEST_E16_E19_PHYSICAL_IPHONE_IPAD_PWA_VOICEOVER_OPEN__NO_PRODUCTION_AUTHORITY"
    ver["rebuild_status"]="PROVISIONAL_V14218_IDENTITY_RECONCILED_ON_UNDEPLOYED_BRANCH__ORIGINAL_204_CORPUS_BINDING_PRESERVED__POST_RECONCILIATION_QA_OPEN"
    ver["wide_public_release"]="NOT_AUTHORIZED__INTEGRATION_WIP_ONLY__NO_OWNER_DEPLOYMENT_CONSENT"
    ver["wide_public_release_gate"]="NO_GO__POST_METADATA_FULL_APP_QA_AND_HOSTED_ORIGIN_AND_PHYSICAL_QA_OPEN"
    ver["v142_18_controlled_integration"]={
        "status":"WIP_POST_RECONCILIATION_UNRELEASED",
        "reader_parent_commit":READER,
        "qualified_semantic_parent_commit":SEARCH,
        "initial_integrated_repair_git_blob":MERGED_REPAIRED_GIT_BLOB,
        "semantic_manifest_sha256":MANIFEST_HASH,
        "frozen_model_asset_count":20,
        "frozen_asset_total_bytes":213290251,
        "offline_corpus_assets":204,
        "offline_content_binding_sha256":BINDING,
        "positive_and_negative_and_reader_modes_chromium_qa":"19_OF_19_PASS_ON_PRIOR_WIP_INDEX__MUST_RETEST_VERSION_RECONCILIATION",
        "hosted_origin_isolation_e16_e19":"OPEN",
        "web_kit_and_physical_device_gate":"OPEN",
        "curated_release_zip":"NOT_CREATED",
        "app_test_deployment_authority":"NONE",
        "production_deployment_authority":"NONE",
        "immutable_qualified_engineering_manifest_flags_preserved":True,
        "source_and_search_algorithms_ranking_changed":False,
        "corpus_payload_or_user_state_schema_changed":False
    }
    ver_bytes=json.dumps(ver,ensure_ascii=False,indent=2)+"\n"
    assert json.loads(ver_bytes)["page_worker_revision"]==NEW_SW
    assert json.loads(ver_bytes)["user_data_schema_version"]==old_version["user_data_schema_version"]
    assert json.loads(ver_bytes)["user_data_db_internal_version"]==old_version["user_data_db_internal_version"]
    for p,data in zip(paths,[index,sw,ver_bytes,off]):p.write_text(data)
    subprocess.check_call(["node","--check","sw.js"])
    sem=json.loads(pathlib.Path("pls_v16/semantic_pack_manifest.json").read_text())
    assert b3(pathlib.Path("pls_v16/semantic_pack_manifest.json"))==MANIFEST_HASH
    assert sem["app_runtime_wired"] is False and sem["deployment_authorized"] is False
    assert json.loads(paths[3].read_text())["assets"]==old_off["assets"]
    # Manifest content binding is tied to these corpus objects, not cosmetic app metadata.
    report={"schema":"ldc-v14218-provisional-version-reconciliation-v1",
      "status":"SOURCE_CONTRACT_PASS__ACTUAL_BROWSER_RETEST_REQUIRED",
      "original_reader_commit":READER,"semantic_source_commit":SEARCH,
      "old_hashes":before,"new_sha256":{str(p):b3(p) for p in paths},
      "semantic_manifest_sha256":MANIFEST_HASH,
      "corpus_content_binding":BINDING,
      "offline_corpus_assets_unchanged":204,"frozen_model_files_not_mutated":20,
      "new_shell_small_javascript_only":True,"model_213mb_not_added_to_mandatory_shell":True,
      "app_test_deployment_authority":"NONE","production_deployment_authority":"NONE",
      "real_hosted_isolation":"OPEN","physical_iphone_ipad_pwa":"OPEN",
      "curated_release_zip":"NOT_BUILT"}
    pathlib.Path("LDC_v142.18_PROVISIONAL_VERSION_RECONCILIATION.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
