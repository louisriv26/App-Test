#!/usr/bin/env python3
"""Reproducible v142.18 two-parent splice. No deployment, no model mutation."""
import bisect
import collections
import hashlib
import json
import pathlib
import subprocess

BASE = "572d9df7927765b575a76eaee98fd3cc9d455e74"
READER = "56a306997a37ab975a573774a97fa976a40ffe40"
SEMANTIC = "39b9ec90ab3b2199b1738e96b353cc6b27d9cac0"
OUT = pathlib.Path("LDC_v142.18_INITIAL_SPLICE_EVIDENCE.json")
FROZEN_MANIFEST = "37dc813c06c4358eb66c0e0c5d6f4fa4c7b8f7e2d775b66c957df68c5f171ef0"
PROTECTED_BINDING = "1fb8d6d8a532806ad6a25b32250091deed174ddb54130f1b05d3da2233a05384"
SCRIPTS = [
    "search_semantic_pack_guard_r4.js",
    "search_semantic_hybrid_r6.js",
    "search_semantic_pack_registry_r6.js",
    "pls_v16/runtime_v1.mjs",
]
V16_FILES = [
    "pls_v16/semantic_pack_manifest.json",
    "pls_v16/BINDING_CONTRACT.json",
    "pls_v16/QUALIFIED_PACK_IDENTITY.json",
    "pls_v16/QUALIFIED_SHA256SUMS.txt",
    "pls_v16/pack/metadata.jsonl",
    "pls_v16/pack/vectors.i8",
    "pls_v16/pack/inverse_norms.f32le",
    "pls_v16/pack/jesus_mask.bits",
    "pls_v16/evidence/coverage.json",
    "pls_v16/evidence/token_coverage.json",
    "pls_v16/evidence/calibration_evidence_v2.json",
    "pls_v16/CALIBRATION_PROTOCOL_V2.json",  # CI-only test fixture
]
FILES = SCRIPTS + V16_FILES
def run(*args):
    return subprocess.check_output(args)
def source(ref, path):
    return run("git","show", f"{ref}:{path}")
def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):
            h.update(b)
    return h.hexdigest()
def unique_anchors(a,b):
    ac=collections.Counter(a);bc=collections.Counter(b)
    bm={line:j for j,line in enumerate(b) if bc[line]==1}
    pairs=[(i,bm[line]) for i,line in enumerate(a) if ac[line]==1 and line in bm]
    tails=[]; pred=[-1]*len(pairs); indexes=[]
    for idx,(_,y) in enumerate(pairs):
        pos=bisect.bisect_left(tails,y)
        if pos>0: pred[idx]=indexes[pos-1]
        if pos==len(tails):
            tails.append(y);indexes.append(idx)
        else:
            tails[pos]=y;indexes[pos]=idx
    lis=[]
    if indexes:
        k=indexes[-1]
        while k!=-1:
            lis.append(pairs[k]);k=pred[k]
    return [(-1,-1)]+lis[::-1]+[(len(a),len(b))]
def diffs(a,b):
    anch=unique_anchors(a,b)
    result=[]
    for (x,y),(u,v) in zip(anch,anch[1:]):
        aa=a[x+1:u]; bb=b[y+1:v]
        if aa!=bb:result.append((x,u,aa,bb))
    return result
def apply():
    assert run("git","rev-parse","HEAD").decode().strip() not in (BASE,READER,SEMANTIC), "must run on isolated successor"
    assert source(READER,"index.html")==pathlib.Path("index.html").read_bytes(), "starting Reader bytes changed"
    base=source(BASE,"index.html").decode("utf8").splitlines(keepends=True)
    reader=source(READER,"index.html").decode("utf8").splitlines(keepends=True)
    sem=source(SEMANTIC,"index.html").decode("utf8").splitlines(keepends=True)
    d=diffs(base,sem)
    assert len(d)==14, f"semantic changed-region count shifted: {len(d)}"
    merged=list(reader); ledger=[]
    for left,right,old,new in d[::-1]:
        before=0 if left<0 else merged.index(base[left])+1
        after=len(merged) if right>=len(base) else merged.index(base[right])
        current=merged[before:after]
        if current!=old:
            raise RuntimeError(f"THREE_WAY_COLLISION base={left+2} old={len(old)} reader={len(current)}")
        merged[before:after]=new
        ledger.append(dict(base_start_line=left+2,base_end_line=right,reader_start_line=before+1,
                           removed_lines=len(old),added_lines=len(new),conflict=False))
    merged_data="".join(merged).encode("utf8")
    assert b"pls_v16/runtime_v1.mjs" in merged_data
    assert b"function beginReaderProgrammaticScroll" in merged_data
    assert b"function invalidateReaderAsyncTransactions" in merged_data
    assert b"function updateReaderLowHeightMode" in merged_data
    assert b"search_semantic_pack_guard_r3.js" not in merged_data
    assert b"LDCPLSOwnerPrototypeV15" not in merged_data
    pathlib.Path("index.html").write_bytes(merged_data)
    # Bring frozen exact Git blobs across without rebuilding/calibrating.
    subprocess.check_call(["git","restore",f"--source={SEMANTIC}","--",*FILES])
    # All 20 runtime model/index assets include inherited v15 plus v16.
    manifest_data=pathlib.Path("pls_v16/semantic_pack_manifest.json").read_bytes()
    assert hashlib.sha256(manifest_data).hexdigest()==FROZEN_MANIFEST
    m=json.loads(manifest_data)
    assert m["bindings"]["offline_content_binding_sha256"]==PROTECTED_BINDING
    assert m["deployment_authorized"] is False and m["app_runtime_wired"] is False
    assert len(m["files"])==20
    for f in m["files"]:
        path=f["path"]
        assert pathlib.Path(path).stat().st_size==f["bytes"],"size mismatch "+path
        assert sha256(path)==f["sha256"],"hash mismatch "+path
        if path.startswith("pls_v15/"):
            assert source(READER,path)==pathlib.Path(path).read_bytes(),"v15 byte change "+path
    for p in SCRIPTS:
        assert pathlib.Path(p).read_bytes()==source(SEMANTIC,p),"runtime source changed: "+p
    assert source(READER,"sw.js")==pathlib.Path("sw.js").read_bytes()
    assert source(READER,"version.json")==pathlib.Path("version.json").read_bytes()
    assert source(READER,"offline_manifest.json")==pathlib.Path("offline_manifest.json").read_bytes()
    assert json.loads(pathlib.Path("offline_manifest.json").read_text())["asset_count"]==204
    for path in ["index.html","sw.js","version.json","offline_manifest.json"]+SCRIPTS:
        if path=="index.html":continue
        if path.endswith(".js") or path.endswith(".mjs"):
            subprocess.check_call(["node","--check",path])
    import re
    html=pathlib.Path("index.html").read_text()
    for i,match in enumerate(re.finditer(r"<script([^>]*)>(.*?)</script>",html,re.I|re.S)):
        if "src=" in match.group(1).lower() or "application/json" in match.group(1).lower():continue
        data=pathlib.Path("/tmp/ldc-v14218-inline-%d.js"%i)
        data.write_text(match.group(2))
        subprocess.check_call(["node","--check",str(data)])
    report=dict(schema="ldc-v14218-initial-functional-splice-v1",starting_head=READER,
        common_ancestor=BASE,semantic_parent=SEMANTIC, hunk_count=len(d),
        hunk_ledger=sorted(ledger,key=lambda e:e["base_start_line"]),
        merged_index_sha256=sha256("index.html"),frozen_manifest_sha256=FROZEN_MANIFEST,
        model_assets_verified=20,model_index_bytes=sum(f["bytes"] for f in m["files"]),
        corpus_assets_protected=204, reader_sw_version_files_preserved_pre_qa=True,
        app_test_deployment_authority="NONE",production_deployment_authority="NONE",
        real_combined_browser_qa="NOT_YET_EXECUTED",physical_safari="OPEN",
        published_version="NONE",status="INITIAL_SPLICE_SOURCE_INTEGRITY_PASS_ONLY")
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="hunk_ledger"},indent=2))
if __name__=="__main__":
    apply()
