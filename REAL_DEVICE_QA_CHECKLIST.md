> HISTORICAL_CARRIED_FORWARD_RECORD_NOT_CURRENT_GATE: This file is retained for provenance only. It is not a current Stage 6O.1 package gate result. Old package names, old PASS/FAIL rows, and old error counts inside this file are superseded by metadata/final_decision_lock.json, audit/final_reopen_audit.md, and audit/independent_four_pass_audit.md for the current package.

# Stage 6L-B Real-device validation checklist — prototype-97

Package: `luisa_24_heures_app_v97_stage6lb_real_device_validation_pack_locked.zip`  
Source package: `luisa_24_heures_app_v97_stage6la_minute_rechecked_locked.zip`  
Stage: Stage 6L-B — real-device validation execution pack and static package audit

This checklist is for physical-device and live-deployment validation. Static/package gates already passed; these items remain NOT_TESTED until completed by testers on real devices.

## Global precheck on every device
- [ ] Open the deployed app from the exact Stage 6L-B package or nested GitHub deploy ZIP.
- [ ] Confirm Aide / À propos or visible version area shows `prototype-97`.
- [ ] Record device model, OS version, browser, install mode, network state, and orientation.
- [ ] Take screenshot of initial screen and each failure.

## Samsung / Android paragraph highlighting
- [ ] Open one Hour with normal meditation paragraphs.
- [ ] Confirm Paragraphe mode is available on Samsung/Android.
- [ ] Tap Paragraphe.
- [ ] Confirm the hint explains whole-paragraph highlighting and does not ask for word selection.
- [ ] Tap one paragraph.
- [ ] Confirm the paragraph is visibly targeted before choosing a colour.
- [ ] Choose a colour.
- [ ] Confirm the whole paragraph is highlighted.
- [ ] Reload the app and confirm highlight persists.
- [ ] Open Mon Espace and confirm the highlight appears.
- [ ] Confirm no Google/Samsung Translate/Search/Copy overlay interrupts the flow.

## iPhone exact selected-text highlighting
- [ ] Open one Hour in Safari.
- [ ] Select a short exact phrase within one paragraph.
- [ ] Tap Surligner.
- [ ] Choose a colour.
- [ ] Confirm only the selected phrase is highlighted, not the whole paragraph.
- [ ] Reload and confirm persistence.
- [ ] Confirm highlight appears in Mon Espace and jumps back correctly.

## iPad exact highlighting + orientation/scroll
- [ ] Repeat iPhone exact selection test in portrait.
- [ ] Rotate to landscape.
- [ ] Confirm scroll position does not jump unexpectedly.
- [ ] Confirm text remains readable and the body is not compressed into a narrow strip.
- [ ] Confirm colour picker and prayer modal are not clipped.
- [ ] Rotate back to portrait and confirm layout recovers.

## Hour 19 speech display
- [ ] Open the 19e Heure.
- [ ] Confirm “Mon amour, chère Croix...” is styled as Jesus speech.
- [ ] Confirm “Est-il possible, mon Fils...” is styled as Father/Père speech.
- [ ] Confirm “Ah ! Fils...” is styled as Father/Père speech.
- [ ] Confirm narration beginning “Mais Toi, ô mon Jésus...” after the Father quote remains normal narration.

## Installed PWA / offline / update
- [ ] Install/add to home screen where supported.
- [ ] Open online and confirm `prototype-97`.
- [ ] Add a favourite or highlight.
- [ ] Close the app completely.
- [ ] Enable airplane mode.
- [ ] Reopen installed app.
- [ ] Confirm all 24 Hours are readable.
- [ ] Confirm prayers and Textes are readable.
- [ ] Confirm Mon Espace data persists.
- [ ] Confirm no blank screen appears.
- [ ] Reconnect to network.
- [ ] Confirm Actualiser/update does not loop and version remains clear.

## Decision
Use PASS only for a row that was physically tested and passed. Use NOT_TESTED if no real device was used. Use FAIL with screenshots and reproduction steps for any defect.
