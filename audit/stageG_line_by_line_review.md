# 24H-G line-by-line change review

Status: PASS.

Reviewed exact diff against immutable v101.60. Changes are limited to:
1. Stage-G accessibility CSS: frequent controls receive minimum 44px hit areas; no corpus/render text selectors changed.
2. Reduced-motion override strengthened to near-zero animation/transition and automatic scroll behavior.
3. APP_VERSION / evidence-stage / build comment updated to v101.61.
4. Help focus return now captures the actual invoking control instead of hard-wiring the desktop Help button.
5. `hasUnsavedNoteDraft()` and the pre-navigation guard were added at the very start of `refreshAppForUpdate()`. The guard returns before service-worker update, session update marker, or location replacement.
6. Update banner receives `role=status`, `aria-live=polite`, and `aria-atomic=true`.
7. sw.js behavior unchanged except cache identity v101.61; manifest/version/README/QA identities updated.

Protected declarations were exact-hash compared and are byte-identical. HTML remains CRLF with zero bare LF.
