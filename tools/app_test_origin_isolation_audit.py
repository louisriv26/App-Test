#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
from urllib.parse import urlparse

APPS = ("ldc","24h","marie","lettres","hub")

def origin(url):
    p=urlparse(url)
    scheme=(p.scheme or "").lower()
    host=(p.hostname or "").lower()
    if not scheme or not host:
        raise ValueError("absolute http(s) URL required")
    port=p.port
    default=(scheme=="https" and port in (None,443)) or (scheme=="http" and port in (None,80))
    return f"{scheme}://{host}" if default else f"{scheme}://{host}:{port}"

def text(path):
    try: return path.read_text(encoding="utf-8")
    except Exception: return ""

def db_name(html):
    m=re.search(r"\bconst\s+DB_NAME\s*=\s*['\"]([^'\"]+)['\"]",html)
    return m.group(1) if m else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--production-origin", default="https://louisriv26.github.io/")
    ap.add_argument("--test-origin", required=True)
    ap.add_argument("--production-db-name", default="ldc_user_v1")
    ap.add_argument("--json-out", default="")
    a=ap.parse_args()
    root=Path(a.root)
    prod=origin(a.production_origin); test=origin(a.test_origin)
    checks=[]

    def add(name, passed, detail):
        checks.append({"check":name,"status":"PASS" if passed else "FAIL","detail":detail})

    add("DISTINCT_BROWSER_ORIGIN", test != prod, {"production":prod,"test":test})

    root_index=text(root/"index.html")
    add("ROOT_INDEX_PRESENT", bool(root_index), str(root/"index.html"))
    add("ROOT_NO_SERVICE_WORKER_REGISTRATION",
        "serviceWorker.register" not in root_index,
        "root index must be a neutral launcher")
    add("ROOT_NO_INDEXEDDB_OPEN",
        "indexedDB.open" not in root_index and "DB_NAME" not in root_index,
        "root must not own application storage")

    for app in APPS:
        d=root/app
        html=text(d/"index.html")
        sw=(d/"sw.js")
        add(f"{app.upper()}_FOLDER_PRESENT", d.is_dir(), str(d))
        add(f"{app.upper()}_INDEX_PRESENT", bool(html), str(d/"index.html"))
        add(f"{app.upper()}_SW_PRESENT", sw.is_file(), str(sw))
        if html:
            regs=re.findall(r"serviceWorker\.register\(([^\n;]+)",html)
            add(f"{app.upper()}_LOCAL_SW_REGISTRATION",
                any("./sw.js" in x or "'sw.js'" in x or '"sw.js"' in x for x in regs),
                regs[:5])
            add(f"{app.upper()}_NO_PARENT_SW_SCOPE",
                not any("../" in x for x in regs),
                regs[:5])

    ldc_html=text(root/"ldc"/"index.html")
    candidate_db=db_name(ldc_html) if ldc_html else None
    add("LDC_DB_IDENTITY_PRESERVED",
        candidate_db in (None,a.production_db_name),
        {"production_db_name":a.production_db_name,"test_ldc_db_name":candidate_db,
         "note":"same DB name is acceptable only because DISTINCT_BROWSER_ORIGIN must pass"})

    passed=all(x["status"]=="PASS" for x in checks)
    result={
        "schema":"app-test-origin-isolation-static-audit-v1",
        "status":"PASS" if passed else "FAIL",
        "production_origin":prod,
        "test_origin":test,
        "e16_static_gate":"PASS" if passed else "OPEN",
        "e19_origin_gate":"PASS" if test!=prod else "OPEN",
        "checks":checks,
        "limits":[
            "Static audit cannot prove browser storage isolation.",
            "E-19 requires live cross-origin IndexedDB/localStorage/CacheStorage verification.",
            "E-16 requires live Service Worker registration/scope verification.",
            "No deployment authority is granted by this report."
        ]
    }
    out=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    if a.json_out: Path(a.json_out).write_text(out,encoding="utf-8")
    print(out,end="")
    raise SystemExit(0 if passed else 2)

if __name__=="__main__":
    main()
