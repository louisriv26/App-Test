# Real-device QA checklist — v101.56 / 24H-C

Target HTML SHA-256: `db1ddb644bcdf7e34254c7645b2381ea15c558cdadaf8cd6311ec0c693071b44`

Physical-device validation is release-critical for this stage.

## iPhone / iPad Safari

1. Select an exact phrase inside a meditation paragraph. Confirm one contextual bar appears with **Surligner · Copier · Note · Fermer**.
2. Tap **Surligner**, choose a colour, and confirm only the exact selected range is highlighted. Reload and confirm persistence.
3. Repeat on a Réflexion.
4. Select across two adjacent paragraphs; confirm the shared bar appears and the resulting grouped highlight survives reload without losing either segment.
5. From a selected range, tap **Note**; save two notes on the same paragraph, reload, and confirm both survive.
6. Long-press a paragraph. Confirm the same contextual component appears. Copy and Note must work. Surligner must not silently convert an ordinary Apple paragraph target into whole-paragraph highlighting; exact selection remains the Apple policy.
7. Open an existing highlight and change its colour; stale/recovery behavior must remain intact.
8. Confirm the note textarea does not trigger iOS auto-zoom and the app does not become horizontally pannable.

## Samsung / Android Chrome

1. Tap **Paragraphe**. Confirm native word selection/search/translate does not appear.
2. Tap one paragraph. Confirm it becomes the visual paragraph target and the same contextual bar appears.
3. Tap **Surligner**, choose a colour, and confirm the whole paragraph is highlighted. Reload and confirm persistence and Mon Espace visibility.
4. Repeat **Copier** and **Note** from the same paragraph-target contextual bar.
5. Confirm cancelling the contextual bar or colour picker clears the visual target without leaving a stuck mode.

## Regression

- Repères OFF/ON must not hide contextual actions.
- Existing highlights from v101.55 must render/recover or remain visibly stale; none may silently disappear.
- Search, progression, update flow, theme and 16/19/22/26 px settings remain unchanged.
