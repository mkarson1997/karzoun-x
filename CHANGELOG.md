# Changelog

All notable project changes are documented here.

## 0.1.0-rc1 - 2026-09-11

### Research program
- completed three auditable SMAP/MSL telemetry detector experiments
- added held-out and expanded synthetic spacecraft fault testbeds
- completed local Qwen3 no-RAG versus RAG comparisons with preserved raw responses
- added deterministic communication-delay and ground-link-outage analysis
- completed end-to-end detector + retrieval + local LLM + safety-gate experiments
- added corrected single-host process-family and Ollama resource instrumentation
- completed a precommitted 60-case hard-stress benchmark covering ambiguity, conflicting retrieval, missing evidence, out-of-distribution telemetry, and adversarial evidence
- added retrospective Wilson confidence intervals and an exact paired McNemar synthesis

### Scientific integrity
- retained Phase 2 as a mixed detector result rather than hiding the recall regression
- retained Phase 3 as exploratory because its design followed inspection of earlier benchmark outcomes
- retained the failed Phase 5 v1 response protocol as an audit incident instead of reporting its zero scores as model performance
- separated real SMAP/MSL anomaly detection from synthetic diagnosis/action claims
- documented Phase 9 failures of epistemic abstention under ambiguous, conflicting, and missing evidence
- kept flight-readiness and certified-safety claims explicitly out of scope

### Reproducibility
- machine-generated results stored under `results/`
- frozen experiment configurations and provenance indexed in `experiments/RESULTS_INDEX.md`
- raw local-model responses retained for local-LLM experiments
- environment, timing, and resource artifacts retained where applicable
- CI uses pinned, hash-verified binary dependencies
- added a reproducible PDF/DOCX preprint build and preflight workflow

### Paper
- expanded the manuscript through Phase 10
- filled related-work framing and clarified novelty relative to prior LLM spacecraft-operator research
- added executed RAG ablation, communication, resource, hard-stress, statistical, safety, limitation, and conclusion sections
- expanded bibliography with spacecraft autonomy, fault-management, and LLM-spacecraft references
- added publication figures and completed a 14-page A4 preprint proofread pass

## 0.1.0-alpha - 2026-09-08

### Added
- initial reproducible research scaffold
- robust z-score telemetry anomaly baseline
- deterministic safety gate
- communication-delay simulator
- local lexical retrieval prototype
- Ollama-compatible local LLM adapter
- end-to-end decision pipeline
- research protocol and manuscript skeleton
- CI, contribution, security, and issue templates
