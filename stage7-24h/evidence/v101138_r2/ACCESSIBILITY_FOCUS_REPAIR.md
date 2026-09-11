# v101.138 R2 Help quick-navigation focus repair

R1 scrolled correctly to `#help-support` but `helpJumpTo()` searched only `.help-section-hd`. Assistance uses `.help-feature-title`, so focus stayed on the source quick-navigation button.

R2 changes only the target selector to `.help-section-hd, .help-feature-title`. Existing Help headings remain eligible, and the Assistance heading becomes focusable temporarily (`tabindex=-1`) through the existing focus-transfer logic.
