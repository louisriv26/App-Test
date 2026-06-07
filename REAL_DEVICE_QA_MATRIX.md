# Real-device QA matrix — Luisa 24 Heures

Package: prototype-70 / Stage 5C-R4 minute recheck package

Purpose: execute these tests on real devices before public or closed-beta sharing. Record results in REAL_DEVICE_QA_RESULTS_TEMPLATE.csv.

## Required environments

| Device / mode | Minimum required result |
|---|---|
| iPhone Safari portrait | PASS or logged issue |
| iPhone installed PWA portrait | PASS or logged issue |
| iPad Safari portrait | PASS or logged issue |
| iPad Safari landscape | PASS or logged issue |
| iPad installed PWA | PASS or logged issue |
| Desktop browser | PASS or logged issue |

## Core launch and deployment

| ID | Test | Expected result |
|---|---|---|
| RDQ-001 | Open deployment URL fresh | App loads without visible error. |
| RDQ-002 | Confirm version from app/about/deploy metadata | prototype-70 / Stage 5C-R4 package context is clear. |
| RDQ-003 | Add to Home Screen on iPhone | App icon appears; launch opens the app. |
| RDQ-004 | Add to Home Screen on iPad | App icon appears; launch opens the app. |
| RDQ-005 | Refresh while online | No blank screen; same content remains usable. |
| RDQ-006 | Enable airplane mode after first load; reopen | Offline app shell opens or graceful offline fallback appears. |

## Reader navigation

| ID | Test | Expected result |
|---|---|---|
| RDQ-010 | Open Hours 1, 5, 13, 21, 24 | Each opens at the beginning unless explicit resume is selected. |
| RDQ-011 | Scroll within an Hour, leave, return via normal Hour selection | Opens at top, not arbitrary old position. |
| RDQ-012 | Use explicit resume/Mon Espace resume | Returns to saved location. |
| RDQ-013 | Open prayer before the Hour and Psalm 129, then Retour | Returns to previous prayer/hour context. |
| RDQ-014 | Hour 24 desolation subsections | All subsections open/read normally. |

## Highlighting and text selection

| ID | Test | Expected result |
|---|---|---|
| RDQ-020 | Select text in Hour on iPhone | Highlight controls do not cover essential color controls; highlight can be applied. |
| RDQ-021 | Select text in Hour on iPad | Controls appear without blocking the selected text or color choices. |
| RDQ-022 | Change highlight color | Color is applied and visible. |
| RDQ-023 | Delete highlight from Mon Espace | Highlight is removed and not recreated on reload. |
| RDQ-024 | Highlight prayer paragraph | Highlight works where enabled. |
| RDQ-025 | Highlight Library/Textes paragraph | Highlight works where enabled; placeholder text is not highlightable if intentionally disabled. |

## Library/Textes and large text performance

| ID | Test | Expected result |
|---|---|---|
| RDQ-030 | Open Library/Textes landing | Section navigation is clear and responsive. |
| RDQ-031 | Open Part III hour-linked texts | Text opens, no blank screen, no major delay. |
| RDQ-032 | Open Marie dans le Royaume de la Divine Volonté | Large text opens and scrolls without major jank. |
| RDQ-033 | Use Textes liés from Hours 21, 22, 23, 24 | Linked cards open the correct texts. |
| RDQ-034 | Use Mon Espace side panel on iPad/desktop | Panel opens/closes and reading width changes correctly. |

## Search

| ID | Test | Expected result |
|---|---|---|
| RDQ-040 | Search 'Passion' | Results appear with cap messaging if many results. |
| RDQ-041 | Search 'Marie' | Results include relevant Mary items. |
| RDQ-042 | Search 'Psaume 129' | Psalm result opens correctly. |
| RDQ-043 | Search rare terms from Part III | Result opens the correct Library/Textes or Hour-linked text. |

## Personal data import/export

| ID | Test | Expected result |
|---|---|---|
| RDQ-050 | Export personal data after adding favorite/highlight | File downloads or share/save works; no crash. |
| RDQ-051 | Import previously exported safe data | Favorites/highlights/logs restore. |
| RDQ-052 | Import malformed file | App rejects gracefully without corrupting data. |
| RDQ-053 | Clear/reset browser storage then reload | App loads cleanly with no blank screen. |

## Accessibility and keyboard

| ID | Test | Expected result |
|---|---|---|
| RDQ-060 | Tab through top controls on desktop | Visible focus and logical order. |
| RDQ-061 | Use skip link | Focus moves to main text region. |
| RDQ-062 | Search results announced/updated | No disruptive focus trap. |
| RDQ-063 | Bottom navigation active state | Screen reader/DOM exposes active tab where applicable. |

## Result rules

- PASS: works on the real device.
- FAIL: broken or incorrect; attach screenshot/video if possible.
- LIMITED_PASS: usable but with caveat.
- NOT_TESTED: not tested on that device/mode.
