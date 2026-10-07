# App-Test Origin & Service-Worker Isolation Contract

**Status:** WIP architecture contract — **E-16 OPEN / E-19 OPEN**  
**Baseline:** LDC v142.15 frozen commit `572d9df7927765b575a76eaee98fd3cc9d455e74`  
**Deployment authority:** NONE

## 1. Verified defects

### E-16 — App-Test root service worker controls sibling test surfaces

The current LDC test shell is at the repository root and registers `./sw.js`. With the GitHub Pages project-site layout, the worker's default scope is the App-Test repository root. That scope contains many unrelated candidate folders (24H, Marie, Lettres and others).

Scope-fingerprinted cache names reduce cache-name collisions but **do not reduce Service Worker control scope**.

### E-19 — App-Test and production do not have storage isolation

The current App-Test LDC and production LDC both run under the browser origin `https://louisriv26.github.io` and both use the IndexedDB name `ldc_user_v1`.

IndexedDB, CacheStorage and localStorage are isolated by **origin (scheme + host + port)**, not by URL path. Therefore a separate repository path is insufficient.

## 2. Non-solutions prohibited

The following do **not** close E-19:

- moving App-Test from one path to another under the same `https://louisriv26.github.io` origin;
- merely changing the IndexedDB name in test code;
- changing the production database name;
- relying on cache-name prefixes alone;
- claiming isolation from repository separation when scheme/host/port are unchanged.

Production user-data schema and database identity are protected surfaces and must not be mutated merely to accommodate testing.

## 3. Required target architecture

A successor App-Test environment must use a **genuinely distinct browser origin** from production, for example a dedicated test hostname.

Within that distinct origin:

- root `/` is a neutral launcher only;
- root must not register a Service Worker;
- root must not open application IndexedDB databases;
- LDC lives under `/ldc/`;
- 24H lives under `/24h/`;
- Marie lives under `/marie/`;
- Lettres lives under `/lettres/`;
- Hub lives under `/hub/`;
- each app registers only its own `./sw.js` from inside its own folder;
- each app worker must remain scoped to its own app folder;
- no app worker may control a sibling app folder.

## 4. Isolation invariant

Let:

- production origin = `scheme://host:port` of the production app;
- test origin = `scheme://host:port` of the App-Test environment.

**Required:** `test_origin != production_origin`.

Only after that invariant holds may the same application database name (for example `ldc_user_v1`) safely exist in both environments without cross-environment IndexedDB collision.

## 5. E-16 acceptance gates

E-16 may close only when all are proven on the actual test origin:

1. root page has no Service Worker registration;
2. no active root-scoped App-Test worker controls app pages;
3. each app's worker script resides inside its app folder;
4. each app registration resolves to a scope contained by that app folder;
5. opening LDC does not create/control a worker for 24H, Marie, Lettres or Hub;
6. opening any sibling app does not replace or control LDC's worker;
7. CacheStorage entries remain app/scope-specific;
8. installed-PWA update and offline behavior still pass per app.

## 6. E-19 acceptance gates

E-19 may close only when all are proven on the actual production and test environments:

1. production and test origins differ by scheme, host or port;
2. a test write to `ldc_user_v1` is invisible from production;
3. a production write is invisible from test;
4. localStorage probes are isolated;
5. CacheStorage probes are isolated;
6. Service Worker registrations are isolated;
7. no production user data is copied into test by migration logic;
8. no production DB-name/schema mutation was introduced for this fix.

## 7. Migration order

1. Provision the distinct test origin.
2. Bind the App-Test Pages/site deployment to that origin.
3. Build the neutral root and per-app folder layout on a successor infrastructure candidate.
4. Move/copy exact app candidates into their respective folders without semantic mutation.
5. Rebind relative paths and per-app Service Worker registration only where mechanically required.
6. Run machine isolation audit.
7. Run browser cross-origin storage/SW challenge.
8. Run physical iPhone/iPad installed-PWA and offline/update qualification.
9. Only then close E-16/E-19.

## 8. Current disposition

This branch is **planning and verification tooling only**. It does not change the frozen v142.15 runtime, does not deploy a new App-Test origin, and does not close E-16 or E-19.
