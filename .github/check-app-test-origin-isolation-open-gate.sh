#!/usr/bin/env bash
set -euo pipefail
out=app-test-origin-isolation-current-baseline.json
set +e
python3 tools/app_test_origin_isolation_audit.py \
  --root . \
  --production-origin 'https://louisriv26.github.io/Le-livre-du-Ciel---Github/' \
  --test-origin 'https://louisriv26.github.io/App-Test/' \
  --json-out "$out"
rc=$?
set -e
test "$rc" -eq 2
python3 - "$out" <<'PY'
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
assert j['status']=='FAIL'
m={x['check']:x for x in j['checks']}
assert m['DISTINCT_BROWSER_ORIGIN']['status']=='FAIL'
assert m['ROOT_NO_SERVICE_WORKER_REGISTRATION']['status']=='FAIL'
assert m['ROOT_NO_INDEXEDDB_OPEN']['status']=='FAIL'
assert j['e19_origin_gate']=='OPEN'
print(json.dumps({
  'schema':'app-test-origin-isolation-open-gate-baseline-v1',
  'status':'PASS',
  'meaning':'audit correctly rejects current same-origin/root-worker architecture',
  'detected':{
    'same_origin':True,
    'root_service_worker':True,
    'root_application_indexeddb':True
  },
  'e16':'OPEN',
  'e19':'OPEN'
},indent=2))
PY
