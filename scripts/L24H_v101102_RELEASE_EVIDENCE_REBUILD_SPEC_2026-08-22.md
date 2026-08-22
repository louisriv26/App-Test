# v101.102 release-evidence rebuild specification — RE1

## Scope lock

Release engineering only. Do not modify the speech/presentation algorithm, canonical text, `SPEECH_DATA`, visible paragraph topology, app UI, storage, search, highlighting, or service-worker runtime.

## Evidence lifecycle

1. Rebuild all active reports so they contain only evidence already available before package freeze.
2. Do not embed final reopened-ZIP reports or a final decision lock inside the candidate ZIP.
3. Mark final reopened-ZIP, independently reopened-ZIP, and final deterministic-ZIP outcomes as `POST_PACKAGE_EXTERNAL` inside the candidate.
4. Build deterministic A/B ZIPs with fixed timestamps and identical member bytes.
5. Freeze one exact immutable ZIP and compute its SHA-256.
6. Run a primary fresh-extraction audit against that exact SHA.
7. Run a separately implemented independent fresh-extraction audit against that same exact SHA.
8. Only after both complete, write external `FINAL_REOPEN_AUDIT.md`, `INDEPENDENT_REOPEN_AUDIT.md`, `FINAL_DECISION_LOCK.json`, and `EXECUTION_SUMMARY.md`.
9. If either reopen audit fails, final status is FAIL. If both pass but physical-device/live/offline gates remain untested, final status is `LIMITED_PASS_STATIC`.

The immutable ZIP remains untouched after step 5.
