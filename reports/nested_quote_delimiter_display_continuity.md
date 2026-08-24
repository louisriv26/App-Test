# v101.110 — nested quote delimiter display continuity

The v101.109 runtime DOM audit found two residual presentation defects after RA19E semantic reconciliation:

- `PASSION24.TEXT.RELATED_HOUR_21.BODY.P094`: the final meaningful straight closing quote at offset 267 was outside the Jesus display run.
- `PASSION24.TEXT.PROMISES_BENEFITS.BODY.P134`: the meaningful straight closing quote at offset 76 was outside the Jesus display run; a derivative speech-end break remained at offset 77 immediately before the hidden redundant outer `»`.

Repairs:
- P094 Jesus presentation extends `0–267` → `0–268`.
- P134 Jesus presentation extends `0–76` → `0–77`; presentation/local break 77 removed; outer redundant `»` at `77–78` remains hidden.

Canonical text, raw `SPEECH_DATA`, RA19E semantic adjudications and RA19B flow are unchanged.
