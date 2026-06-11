# Stage 6O live-device / PWA validation guide

Package: `luisa_24_heures_app_v98_stage6o_live_device_pwa_validation_pack_locked.zip`
App version: `prototype-98`
Status before live evidence: `LIMITED_PASS_STATIC`
Real-device status: `NOT_TESTED`
Generated UTC: `2026-06-11T16:44:00Z`

## Purpose

Use this deploy folder, or the nested `luisa_24h_github_deploy.zip`, for live GitHub Pages and physical-device validation. This is not a public-release PASS.

## Required evidence before any live PASS claim

For each device/test, record: tester, date/time, exact URL, browser, OS/device model, install state, network state, action, expected result, observed result, screenshot/video evidence, and PASS/FAIL/NOT_TESTED.

## Mandatory live scenarios

1. Install/open PWA from GitHub Pages.
2. Open after first load with network disabled.
3. Run Actualiser while online and confirm version/update behaviour.
4. Rotate iPhone/iPad portrait to landscape and back inside a long Hour.
5. Open Accueil, reader, Réglages, Approfondir/Textes liés, Comment pratiquer/Aide.
6. Smoke-test Samsung paragraph highlighting only as deferred preserve-check, not as a public-release blocker.
7. Smoke-test iPhone/iPad exact text highlighting only as preserve-check.

## Stop conditions

Stop and report if blank screen, broken offline open, lost local data, broken scroll/orientation, hidden/blocked controls, stale version confusion, or any regression affecting prayer-first UX.
