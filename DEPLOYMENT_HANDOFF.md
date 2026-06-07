# Deployment handoff — prototype-77

Package: `luisa_24_heures_app_v77_stage5i_mobile_visual_polish_locked.zip`

Stage: Stage 5I — iPhone bottom-nav responsive repair + Help modal containment

Deploy the contents of this folder or the nested `luisa_24h_github_deploy.zip` to GitHub Pages.

Primary change:

- Android/Samsung-only main-content scroll repair. Aide already had independent modal scrolling; this patch gives the main app pages an explicit Android content scroll root.

Real-device validation remains required for:

- Samsung/Android Chrome or Samsung Internet: Accueil, Heure complète, Textes, Mon Espace, and Aide must all scroll correctly;
- iPhone Safari and installed iPhone PWA regression;
- iPad Safari portrait and landscape regression;
- highlighting/text selection;
- update banner;
- offline/PWA behaviour.
