# LDC v142.16 — E-16 / E-19 App-Test origin-isolation architecture

Status: **ENGINEERING PLAN — NOT DEPLOYED — HOSTED ORIGIN GATE OPEN**

## Root cause

The application deliberately uses browser storage that is scoped by **origin**, not by repository path:

- IndexedDB database: `ldc_user_v1`;
- localStorage for onboarding/search preferences;
- Cache Storage for offline/runtime assets;
- Service Worker registrations whose control is scoped by origin + path.

A different GitHub Pages project path on the same `scheme://host:port` does **not** create a new storage origin. Consequently, a production app and an App-Test app served from different paths of the same host can still observe the same IndexedDB/localStorage/Cache Storage namespace. Path-scoped Service Workers and cache-name fingerprints reduce worker/cache collisions, but they do not isolate origin-scoped IndexedDB or localStorage.

Therefore E-16/E-19 cannot be closed by:

1. changing only the pathname;
2. giving App-Test a different IndexedDB name in production code;
3. relying only on the existing scope-fingerprinted Cache Storage names;
4. relying only on Service Worker scope.

## Required architecture

### 1. Separate origin

App-Test must be served from an origin different from production:

`scheme://host:port` must differ in at least one origin component, normally **host**.

Preferred shape:

- production: existing production origin;
- test: dedicated test host/subdomain/origin;
- neutral test landing root;
- LDC under an app-specific path such as `/ldc/`.

The exact host is infrastructure-owned and is **not selected or deployed by this WIP**.

### 2. Neutral test root

The root of the test origin must not register an LDC Service Worker. Each test app registers only inside its own subfolder/scope. This prevents an LDC worker from accidentally becoming the root controller for future test apps.

### 3. Production code remains environment-neutral

Do **not** rename `ldc_user_v1` or other production storage keys merely for App-Test. With genuine origin separation, identical application storage identifiers are desirable: they prove that isolation comes from the web security boundary rather than conditional test code.

### 4. Required hosted proof before closure

On the eventual hosted test origin, run the same browser with production and App-Test and prove:

- `location.origin` differs;
- writing a sentinel to IndexedDB `ldc_user_v1` in App-Test does not appear in production and vice versa;
- identical localStorage keys remain isolated;
- identical Cache Storage names remain isolated;
- Service Worker registrations/controllers are confined to their own origins and intended scopes;
- opening/removing test data leaves production user state unchanged;
- installed-PWA state/update behavior remains independent.

No real production user records should be overwritten for this proof. Use dedicated sentinel keys/records and delete them after the test.

## Machine proof in this branch

The companion WIP QA intentionally uses:

- two local origins (different ports) with **identical** DB/key/cache names to prove origin isolation;
- a same-origin/different-path control to prove that pathname separation is insufficient.

This is a browser-mechanism proof only. It does **not** close the hosted infrastructure gate.

## Gate status

| Gate | Status |
|---|---|
| Root-cause established | PASS |
| No App-Test-specific DB-name mutation | PASS |
| Browser origin-isolation mechanism | PENDING companion CI |
| Same-origin pathname negative control | PENDING companion CI |
| Dedicated hosted App-Test origin exists | OPEN |
| Neutral hosted root verified | OPEN |
| Hosted production-vs-test storage proof | OPEN |
| Deployment authority | NONE |

E-16/E-19 remain **OPEN** until the hosted-origin gates pass.
