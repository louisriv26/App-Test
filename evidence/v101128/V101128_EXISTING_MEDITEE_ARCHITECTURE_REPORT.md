# Existing Méditée architecture — v101.127 baseline

PASS. `buildMarkBar(hourNum)` exists and was dormant; `renderReader()` already invokes it below the reader header; the bottom `markReadBtn` invokes `markMeditee(hourNum)`; `markMeditee` mutates only `state.readHours`/`meditationLog`, uses `commitDurableChange`, and refreshes Hour-24 cycle UI; resume uses `restoreSavedParaForHour`. No second progression authority is present.
