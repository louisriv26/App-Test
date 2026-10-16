#!/usr/bin/env python3
"""R238 application ZIP builder. Read-only source tree; refuses missing, unlisted or altered files.
THIS DOES NOT GRANT DEPLOYMENT AUTHORITY OR SUBSTITUTE FOR REAL APPLICATION QA.
Usage: python 05_SAFE_STANDALONE_PACKAGE_BUILDER_R238.py /path/to/EXACT_APP_ROOT /path/to/output.zip
"""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZIP_DEFLATED
import sys, json, os

def main(root, output):
    root = Path(root).resolve()
    output = Path(output).resolve()
    manifest_path = root / "PACKAGE_MANIFEST_SHA256.json"
    if not manifest_path.is_file():
        raise RuntimeError("Package manifest missing")
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    records = manifest["files"]
    paths = [r["path"] for r in records]
    if not records or len(paths) != len(set(paths)) or paths != sorted(paths):
        raise RuntimeError("Package inventory not strictly ordered and unique")
    if len(records) != manifest["packaged_file_count_excluding_manifest"]:
        raise RuntimeError("Package count mismatch")
    if "PACKAGE_MANIFEST_SHA256.json" in paths:
        raise RuntimeError("Manifest must not self-reference its SHA")
    verified = []
    for rec in records:
        rel = Path(rec["path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise RuntimeError(f"Unsafe manifest path: {rel}")
        source = (root / rel).resolve()
        if not source.is_relative_to(root) or not source.is_file() or source.is_symlink():
            raise RuntimeError(f"Missing or unsafe file: {rel}")
        data = source.read_bytes()
        if len(data) != rec["bytes"] or sha256(data).hexdigest() != rec["sha256"]:
            raise RuntimeError(f"Invalid SHA-256/length for {rel}")
        verified.append((str(rel).replace(os.sep, "/"), data))
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.is_relative_to(root):
        raise RuntimeError("Output ZIP must be OUTSIDE source tree")
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in verified:
            z.writestr(name, data)
        z.writestr("PACKAGE_MANIFEST_SHA256.json", manifest_bytes)
    with ZipFile(output, "r") as z:
        names = z.namelist()
        if names != paths + ["PACKAGE_MANIFEST_SHA256.json"]:
            raise RuntimeError("Reopen ZIP entry/order mismatch")
        for rec in records:
            b = z.read(rec["path"])
            if len(b) != rec["bytes"] or sha256(b).hexdigest() != rec["sha256"]:
                raise RuntimeError(f"Reopen ZIP failed: {rec['path']}")
        if z.read("PACKAGE_MANIFEST_SHA256.json") != manifest_bytes:
            raise RuntimeError("Reopen package manifest failed")
    print(json.dumps({"zip": str(output), "entries": len(records) + 1,
                      "sha256": sha256(output.read_bytes()).hexdigest(),
                      "status": "BUILT_AND_REOPENED_NOT_RELEASE_QUALIFIED"}, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
