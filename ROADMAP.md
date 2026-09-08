# Research Roadmap

## Phase 0 — Foundation
- Freeze terminology, research question, hypothesis, and scope.
- Establish repository governance and reproducibility rules.

## Phase 1 — Benchmark ingestion
- Acquire upstream SMAP/MSL telemetry data.
- Verify hashes and provenance.
- Freeze data preparation and evaluation definitions.

## Phase 2 — Classical baselines
- Reproduce simple statistical anomaly baselines.
- Add at least one stronger time-series baseline.
- Record compute/runtime/resource use.

## Phase 3 — Grounded reasoning
- Build local fault-knowledge corpus.
- Benchmark retrieval quality.
- Integrate local LLM reasoning with explicit evidence references.

## Phase 4 — Safety gating
- Define allow/deny/escalation action taxonomy.
- Run adversarial and ambiguous recommendation tests.
- Quantify unsafe proposal and rejection rates.

## Phase 5 — Communication stress
- Simulate latency, jitter, packet loss, and complete outage.
- Evaluate decision quality and time-to-safe-response.

## Phase 6 — Ablations and resource constraints
- Remove RAG, safety gate, and anomaly detector one at a time.
- Vary model size and compute budget.
- Compare quality/resource tradeoffs.

## Phase 7 — Paper and archival release
- Freeze code and experiment configuration.
- Generate tables and figures from machine-readable results.
- Release preprint.
- Archive a versioned release with a DOI.
- Add the DOI-backed work to ORCID.
