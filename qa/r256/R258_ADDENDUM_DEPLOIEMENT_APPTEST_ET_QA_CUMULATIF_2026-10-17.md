# LIVRE DU CIEL — R258 — ADDENDUM CUMULATIF APRÈS DÉPLOIEMENT APP TEST

**Date : 17 octobre 2026**  
**Héritage documentaire :** R255 (état maître complet), R256 (diagnostic et correctif), R257 (qualification adversariale), sans suppression, réécriture ni transformation rétroactive des constats historiques.  
**Cette pièce est un addendum cumulatif, pas une reproduction intégrale du fichier R255 de 32 714 lignes.**

## 1. Décision et périmètre d'autorité

L'utilisateur a expressément autorisé le déploiement sur APP TEST **en ne remplaçant que les fichiers modifiés**, puis des tests en ligne sur le site déployé. Aucun déploiement sur MAIN production n'a été demandé ni autorisé.

- APP TEST `louisriv26/App-Test`, branche `main` : **v142.46 déployée**.
- Commit déployé : `290290984c4097b43d83ed521d2ca490de6ad714`.
- Parent exact : `f025be8b8c8ff34f2ae439afb20de3bf293395c9` (v142.45).
- Un seul commit et exactement **cinq chemins modifiés** :
  1. `PACKAGE_MANIFEST_SHA256.json`
  2. `index.html`
  3. `offline_manifest.json`
  4. `sw.js`
  5. `version.json`
- Aucun des **274 autres fichiers du candidat** n'a été modifié ; Reader, corpus, index de recherche, surlignage, persistences et autres scripts applicatifs préservés octet pour octet.
- Déploiement GitHub Pages : run `39009256278`, **SUCCESS**.
- MAIN production `louisriv26/Le-livre-du-Ciel---Github` : non modifié.

## 2. Identité reproductible

Package local R257 minimal `v2.19.142.46-R1B-UNIFIED` :
- SHA-256 ZIP interne : `715999543b73c9b9a8068cbb0fc945ccbe57f0a5af5b2d2d99f222f2271bd750`.
- Taille ZIP : 126 519 653 octets (le package complet dépasse 100 Mio, **mais seuls les cinq fichiers changés ont été transférés sur GitHub**).
- 279 entrées ZIP : 278 fichiers applicatifs et 1 manifeste.
- SHA-256 de la liaison canonique hors ligne : `c6d295844181613e12fb121a9d803e5b8d801e63a084ebd790439b914cde14fd`.
- 205 entrées d'actifs hors ligne conservées.
- Construction déterministe confirmée par plusieurs exécutions indépendantes.

## 3. Intégrité de la publication réelle

**Test en ligne sur l'origine GitHub Pages** (et non seulement sur les sources GitHub) :

- `278/278` fichiers du manifeste récupérés par HTTP et recalculés SHA-256 : **PASS**, zéro divergence.
- Volume vérifié : **336 699 188 octets** d'actifs servis.
- Les quatre fichiers `index.html`, `offline_manifest.json`, `sw.js` et `version.json` ont leurs empreintes attendues : **4/4 PASS** dans un contrôle distinct.
- Vérification du nouveau Service Worker activé en Chromium et WebKit : **PASS**.
- Préparation complète hors ligne par l'interface logicielle sur le site réel : **205/205 READY** dans les deux moteurs.
- Rechargement connecté et persistance d'une donnée IndexedDB **synthétique**, dans les deux moteurs : PASS.
- GitHub Pages v142.46 effectivement servi : PASS.

## 4. Tests fonctionnels en ligne (six configurations de viewport)

Moteurs : Chromium et WebKit automatisés, pour chacun desktop `1280×800`, portrait mobile simulé `390×844`, et paysage simulé `844×390`. Il ne s'agit **pas** de tests iPhone/iPad physiques.

Six parcours complets vérifiés :
- Première visite et sortie du parcours d'accueil initial : PASS.
- Navigation `Tomes → Tome 7 → entrée 30 janvier 1906` via bouton visible et cliquable : PASS.
- Affichage réel du Reader : PASS (9 fragments de paragraphe ; texte visible).
- Sélection DOM native simulée d'une plage courte : PASS, aucun déplacement du conteneur de lecture mesuré dans ce scénario précis (`delta=0`).
- Recherche `Par les mots`, expression `constance` : PASS, résultats présents.
- Recherche `Par le sens`, description libre de la constance : appel et affichage exécutés sans erreur fatale, **mais aucun classement sémantique confirmé** lors de ces essais. Des pistes textuelles de substitution ont été présentées. **NE PAS considérer cela comme un PASS de pertinence sémantique.**
- Retour à l'accueil : PASS.
- Contrôle des fragments mal formés `ni e Et si`, `à l’i Il n’y`, `de sorte  de telle sorte` dans les résultats affichés : aucun de ces fragments n'a été observé dans ces requêtes et limites d'affichage. Cela ne qualifie pas les 44 fenêtres sémantiques dans leur ensemble.
- Toutes les six exécutions finales : **scénario technique réussi**.

Important : le premier test QA automatisé avait échoué à cliquer une entrée parce que l'**écran d'accueil initial n'avait pas été terminé** (état `app-state-onboarding` provoquant intentionnellement `visibility:hidden`). Après réalisation du parcours d'accueil, le test a réussi sans modification de l'application. Il s'agissait d'un défaut du protocole QA et non d'une régression Reader.

## 5. Limitations et réserves

- Activation immédiate via le bouton `Actualiser` après migration depuis des états SW anciens : intermittence observée sur un banc d'essai isolé ; la réparation depuis l'état d'échec `SW_SYNC` a été démontrée dans les deux navigateurs mais **la mise à jour sans aucune intervention n'est pas qualifiée universellement**.
- L'application de test a été publiée pour vérifier précisément ces transitions historiques sur les appareils réels. Ne pas prétendre que les anciens onglets des utilisateurs ont déjà été mis à niveau.
- La recherche `Par le sens` peut produire une abstention avec repli lexical. Les tests R258 démontrent le fonctionnement du parcours et la transparence du repli, **pas l'exactitude sémantique ou le bon rang de passage**. Les deux passages Tome 7 du 30 janvier et 11 août 1906 doivent rester des cas de vérification manuelle.
- Le test de sélection programmée court ne remplace pas un geste natif iOS de sélection et de surlignage couvrant plusieurs paragraphes ; pas de garantie globale de stabilité.
- La conservation d'un marqueur synthétique ne constitue pas la vérification de toutes les anciennes notes, annotations, surlignages, collections et sauvegardes.
- WebKit Playwright a rencontré un échec interne lors de relances **entièrement déconnectées** ; le même échec se reproduit sur le témoin v142.43. Ne pas attribuer au correctif une régression sans démonstration causale et conserver ce test physique ouvert.
- Aucun arbitrage éditorial italien, espagnol ou français nouveau ; aucune mutation des sources, canons, paragraphes et règles de locuteur.

## 6. Décision R258

- **APP TEST v142.46 : DÉPLOYÉE, publiée, contrôlée sur deux moteurs et six tailles, intégrité des 278 fichiers vérifiée.**
- **MAIN v142.34 : INCHANGÉE ; NO GO MAIN.**
- Portes utilisateur : (1) sortie de la boucle de mise à jour, préparation 205/205 et reprise ; (2) sélection/surlignage sans saut et persistance ; (3) Par le sens pour les deux passages Tome 7, distinction résultats sémantiques confirmés / pistes lexicales.
- Toute future modification du corpus, des moteurs ou de la donnée utilisateur exige une autorisation séparée.
- Le présent déploiement ne transfère pas automatiquement l'autorité vers MAIN.

## 7. Preuves vérifiables

- Déploiement cinq fichiers + QA hébergée : https://github.com/louisriv26/App-Test/actions/runs/39009199605
- GitHub Pages : https://github.com/louisriv26/App-Test/actions/runs/39009256278
- Inventaire 278/278 + six parcours fonctionnels : https://github.com/louisriv26/App-Test/actions/runs/39010260314
- Ancienne v142.43 → v142.45 erronée → v142.46 corrigée : https://github.com/louisriv26/App-Test/actions/runs/39005952937
- Contrôle A/B WebKit hors ligne v142.43/v142.46 : https://github.com/louisriv26/App-Test/actions/runs/39008420616
