# LDC PLS v16 — Calibration V1 adjudication

**Status:** V1 = **FAIL_ENGINEERING_ONLY**  
**Deployment authority:** NONE  
**App runtime wiring:** NONE

## 1. Frozen V1 result

The prospective V1 protocol was frozen at commit `007c44c158071ca3b774710b0c1ee228afb99a86` before v16 retrieval outcomes.

Exact vector authority:

- run: `37672229541`
- source head: `c379199d71d50da343f6be3a7517af1faed1bb8e`
- vectors SHA-256: `e7c252118ad8b867737da54c9dcfba36932f54f67f036d6240380140e8c05708`
- inverse norms SHA-256: `27c6d376f1021f56b7c2e365eedf97603cc519a403bf1bcfc9c94d772fdeea47`
- metadata SHA-256: `25d1032044996d2eed8cab3b2c9d6bfbfab91349f0ac6e49ef168c307654b24f`

Independent byte reproducibility was established by a second monolithic build and a fully merged eight-shard singleton build.

V1 selected, prospectively from the three owner positives and eight development negatives:

- minimum positive top-hybrid dense score: `0.8998987177566466`
- maximum development-negative top-hybrid dense score: `0.869260984351889`
- selected midpoint threshold: `0.8845798510542678`
- required channels: `2`
- close label: disabled

Gate results:

- owner real-query gate: **PASS** — target ranks `9 / 1 / 1`
- eight development negatives: **PASS**
- four blind doctrinal negatives: **FAIL** — one of four was accepted

No V1 threshold, rule, feature or query-specific exception was changed after observing the blind result.

## 2. Blind failure

The failed blind probe was:

> La Divine Volonté rend inutile la confession sacramentelle et remplace tous les sacrements.

Its top hybrid result was `LDC.T18.E0010`, 5 November 1925, titled:

**« Les gémissements du Saint-Esprit par rapport aux sept sacrements. Les retours d'Amour adressés à Jésus et au Saint-Esprit. »**

The entry explicitly discusses the Sacrament of Penance and confession. It states that through the sacrament Christ's Blood acts on the repentant sinner to wash, beautify, heal and strengthen the soul and restore lost graces; it later speaks explicitly of confession and describes the sacrament as offering life.

The returned entry is therefore **highly relevant to the query's subject while contradicting its asserted proposition**.

Observed features:

- top dense score: `0.8912556818026742`
- dense rank: `1`
- BM25 rank: `15`
- channels: `2`
- V1 decision: `possible`

## 3. Root-cause adjudication

This is not evidence of:

- wrong corpus binding;
- missing current-corpus coverage;
- vector corruption;
- nondeterministic inference;
- RRF implementation drift;
- wrong source-mode filtering.

It demonstrates a limitation of the **V1 acceptance definition**.

Dense semantic similarity and lexical BM25 measure relatedness. They do not establish whether a retrieved passage **supports, refutes or merely discusses** a proposition. Requiring a semantically related but false in-domain proposition to abstain turns a retrieval-quality gate into an entailment/truth-verification gate.

For the product function **Recherche par le sens**, a relevant passage that corrects an inaccurate memory can be useful and should not automatically be classified as a retrieval failure.

## 4. Governance consequence

V1 remains permanently recorded as **FAIL_ENGINEERING_ONLY**. Its blind holdouts are now revealed and must never be reused as blind evidence.

No QUALIFIED status may be derived from V1.

A successor qualification cycle may be started only if:

1. its objective is explicitly retrieval relevance, not doctrinal entailment;
2. the retrieval/ranking mechanics remain frozen;
3. the confidence copy remains epistemically neutral and does not imply that a user's formulation is true;
4. new blind negatives are frozen before their outcomes are observed;
5. previously revealed doctrinal probes are treated only as truth-neutral retrieval/safety evidence, not as new blind negatives;
6. any successor failure is recorded without post-hoc query-specific exceptions.
