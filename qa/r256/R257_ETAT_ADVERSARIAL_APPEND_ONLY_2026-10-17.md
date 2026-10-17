# Livre du Ciel — R257 — Addendum de qualification adversariale R256 (append-only)

**Date :** 17 octobre 2026  
**État documentaire préalable :** R255, état maître cumulatif et addendum R256 (préservés; non remplacés).  
**Environnement autorisé :** branche GitHub QA uniquement; pas de mutation du corpus ni des données utilisateur.

## 1. Décision de version et de déploiement

- APP TEST, branche `main` : commit `f025be8b8c8ff34f2ae439afb20de3bf293395c9`, v142.45 — **inchangé**.
- MAIN (application publique) : v142.34 — **inchangée**.
- Candidat correctif : `v2.19.142.46-R1B-UNIFIED` — **LOCAL HOLD**.
- Branche de construction : `qa/ldc-r256-sw-lifecycle-20261017`, commit `189451831feb0c5a67842b67e014e14c1c8a3469`.
- Branche indépendante de qualification : `qa/ldc-r256-isolated-webkit-activation-20261017`, commit `1ca2075f57d08d001dff10fad34ced453637fefb`.

**GO APP TEST : non autorisé dans cet addendum. GO MAIN : interdit.**

## 2. Régression R255 démontrée

Le remplacement de l’actif sémantique `pls_v16/patch_r198.json` par `pls_v16/patch_r255.json` a remplacé une entrée au sein des 205 actifs du manifeste hors ligne, sans recalcul de l’empreinte canonique correspondante.

Dans le Service Worker v142.45, la comparaison entre `sha256(JSON.stringify(bindingCanonicalString))` et `OFFLINE_CONTENT_BINDING` échoue :

`offline manifest content binding invalide`

La promesse `event.waitUntil(installCurrentRevisionAtomically())` est rejetée et le nouveau Service Worker devient `redundant`. Cette défaillance a été reproduite dans un vrai navigateur sur profil neuf et en migration v142.43 → v142.45. Elle explique la boucle SW_SYNC et l’indisponibilité du parcours « Reprendre » pour les fichiers hors ligne.

## 3. Correctif de construction R256

L’empreinte canonique réparée est :

`c6d295844181613e12fb121a9d803e5b8d801e63a084ebd790439b914cde14fd`

Vérifiée par deux calculs indépendants, l’un en Python lors du packaging, l’autre en JavaScript/Node suivant l’ordre exact des clés utilisé par le Service Worker.

Les 205 entrées du manifeste et leurs attributs d’intégrité sont préservés. Les modifications du candidat sont exclusivement :

1. `offline_manifest.json`
2. `sw.js`
3. `index.html`
4. `version.json`
5. `PACKAGE_MANIFEST_SHA256.json` (manifeste de paquet, non compté parmi les 278 fichiers)

Les 274 autres fichiers applicatifs sont déclarés et vérifiés strictement identiques au candidat précédent. Le ZIP contient 279 entrées. Le correctif ne modifie aucun texte canonique, complément éditorial, index sémantique R255, donnée utilisateur, schéma de migration, logique de sélection ou surlignage.

Le candidat généré par la qualification `39006866182` a pour SHA-256 du ZIP `2237b33a15e547b52a33f3d757b6ecab9e319e9b8ff9bc2b6b91cbefbad539df`. L’archive de CI publiée par GitHub Actions l’encapsule dans un second ZIP d’artifact; son empreinte est distincte.

## 4. Qualifications positives

### Installation neuve et ancien client, Chromium

- Installation neuve du Service Worker v142.46 : PASS.
- Ouverture et rechargement : PASS.
- Migration contrôlée v142.43 → v142.46 avec `Actualiser` : PASS sur un passage validé, mais **non reproductible à 100 %**.
- Absence d’erreurs JS dans ces passages réussis : PASS limité au périmètre testé.

### Reproduction de la panne réelle puis récupération

Exécution `39005952937`, corroborée par des exécutions ultérieures :

1. v142.43 installée et application fonctionnelle;
2. sauvegarde d’un marqueur synthétique dans IndexedDB;
3. introduction de v142.45 erronée;
4. reproduction `SW_SYNC · nouveau Service Worker devenu redondant`;
5. mise en ligne simulée de v142.46 local et activation de `Réparer et recharger`;
6. application ouverte correctement en v142.46, Service Worker actif;
7. marqueur IndexedDB toujours présent;
8. préparation hors ligne : **205/205 READY**, zéro échec;
9. redémarrage entièrement hors ligne : application fonctionnelle et **205/205 READY**, marqueur persistant.

**PASS dans le navigateur automatisé isolé.** Aucun test de vraies notes, favoris ou surlignages historiques ne découle du seul marqueur synthétique.

## 5. Qualification adversariale de l’activation : NON ACQUISE

Une série indépendante, exécutée sur une branche isolée, a comparé une application minimale et l’application complète sur Chromium/WebKit.

Observations du run `39007364167` :

| Moteur | Scénario | Activations observées |
|---|---|---:|
| Chromium | Mini SW, commande directe | 1/2 |
| Chromium | Application v142.43 → v142.46, commande directe | 1/6 |
| Chromium | Mini SW, fermeture et réouverture | 2/2 |
| Chromium | Application, fermeture et réouverture | 2/2 |
| WebKit | Mini SW, commande directe | 2/2 |
| WebKit | Application, commande directe | 6/6 |
| WebKit | Mini SW, fermeture et réouverture | 2/2 |
| WebKit | Application, fermeture et réouverture | 2/2 |

Ces fréquences sont des observations sur profils de test, **pas des probabilités prévisionnelles d’échec pour les utilisateurs**. Elles contredisent l’affirmation selon laquelle le problème serait exclusivement WebKit.

Un test supplémentaire, `39007668563`, a comparé **48 opérations** sur des SW minimaux et quatre modalités de `skipWaiting` : les 48 activations ont réussi, dans Chromium et WebKit. Cela suggère un effet de timing, de protocole ou d’interaction de l’application complète, mais ne fournit pas une cause unique établie.

**Conclusion adversariale :** un contrôle statique conforme et un test fonctionnel réussi ne suffisent pas à annoncer un parcours de mise à jour « Actualiser » totalement qualifié. Les essais concurrents, la fermeture de toutes les pages, l’état du contrôleur et les transitions de cache restent des portes à valider.

## 6. Changements expérimentaux rejetés

Un essai de `e.waitUntil(self.skipWaiting())`, un essai de temporisation bornée et un appel direct supplémentaire ont été explorés. Ils ne produisent pas un PASS reproductible sur toutes les exécutions.

Le candidat minimal retient le gestionnaire historique `SKIP_WAITING` sans le changement expérimental `waitUntil`; seules les identités de version et de liaison hors ligne sont corrigées. Les essais non qualifiés ne sont pas promus. L’absence de bénéfice robuste ne justifie pas d’ajouter une complexité au Service Worker.

## 7. Portes restantes

- Activation déterministe du nouveau contrôleur depuis le bouton `Actualiser`, avec test multi-onglets et garde de saisie non enregistrée.
- Vérification de toutes les versions historiques ciblées, caches préexistants et migrations de stockage.
- Test iPhone/iPad réels, Safari/Chrome, y compris arrêt et relance de la PWA.
- Sauvegarde/restauration des notes, surlignages, favoris, sélections, positions et collections.
- Qualité indépendante du moteur Par le sens; les contrôles éditoriaux/canoniques restent séparés.
- Parité stricte entre archive de déploiement, manifestes GitHub, GitHub Pages et runtime.
- Accord explicite de promotion MAIN distinct de toute qualification APP TEST.

## 8. Autorités et preuves

- Défaillance publiée v142.45 : https://github.com/louisriv26/App-Test/actions/runs/38999238627
- Simulation complète de panne-réparation, hors ligne et données : https://github.com/louisriv26/App-Test/actions/runs/39005952937
- Comparaison Chromium/WebKit : https://github.com/louisriv26/App-Test/actions/runs/39007364167
- 48 essais SW minimaux : https://github.com/louisriv26/App-Test/actions/runs/39007668563
- Construction exacte du candidat v142.46 : https://github.com/louisriv26/App-Test/actions/runs/39006866182

**Décision R257 :** cause de panne v142.45 prouvée et réparation R256 confirmée sur les tests de récupération et hors ligne. Synchronisation instantanée du processus `Actualiser` **non qualifiée à ce stade**. Préserver APP TEST/MAIN et toutes les données, maintenir LOCAL HOLD jusqu’à décision contraire fondée sur des preuves.
