# Research Roadmap

KARZOUN-X has completed the first experiment program through Phase 10. Historical experiment provenance is recorded in `experiments/RESULTS_INDEX.md`; this roadmap now tracks the remaining work toward the first archival software release and public preprint.

## Completed experiment program

- [x] Repository foundation, research scope, ethics, and reproducibility rules
- [x] SMAP/MSL acquisition, hashes, and anomaly-evaluation definitions
- [x] Phase 1 transparent robust-z-score baseline
- [x] Phase 2 adaptive temporal detector, retained as a mixed result
- [x] Phase 3 stability-aware exploratory detector
- [x] Phase 4 held-out synthetic retrieval/safety mechanics
- [x] Phase 5 v2 local-LLM no-RAG versus RAG comparison
- [x] Phase 6 communication-delay and outage counterfactual
- [x] Phase 7A expanded deterministic robustness suite
- [x] Phase 7B expanded local-LLM end-to-end comparison
- [x] Phase 8 and Phase 8B resource instrumentation
- [x] Phase 9 precommitted hard-stress benchmark
- [x] Phase 10 retrospective confidence intervals and paired statistical synthesis
- [x] Manuscript integrated through the completed experiment program

## First release / preprint gate

Before calling the first research package archived and citable:

- [ ] Resolve the remaining moderate Dependabot alert or document a justified exception
- [ ] Freeze software version `0.1.0`
- [ ] Run final clean CI from the release candidate
- [ ] Produce publication figures directly from machine-readable results
- [ ] Render and proofread the manuscript PDF
- [ ] Perform a final citation/reference audit
- [ ] Archive the software release and obtain a real DOI
- [ ] Archive or submit the preprint and obtain its persistent identifier
- [ ] Add the DOI-backed work to ORCID

## Post-preprint research

The primary scientific follow-up is a new, frozen evaluation of evidence sufficiency and epistemic abstention motivated by Phase 9. Other follow-ups include cross-model/model-size replication, hybrid or dense retrieval, larger independent simulators, cascading faults, stale/version-conflicted procedures, independent detector validation, and testing on more flight-like compute.

These post-preprint experiments must remain clearly separated from the frozen Phase 1–10 evidence used in the first manuscript.
