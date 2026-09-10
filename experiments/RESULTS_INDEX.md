# KARZOUN-X Experiment Results Index

Frozen experiment configurations are treated as immutable after execution. Completion and provenance are recorded here rather than by editing an executed configuration. Synthetic results are explicitly separated from the real SMAP/MSL telemetry benchmark and are not evidence of flight readiness.

| Experiment | Status | Source run | Results |
|---|---|---|---|
| `phase1-robust-zscore-v1` | Completed | GitHub Actions `34337918870` | `results/phase1/` |
| `phase2-adaptive-temporal-v1` | Completed, mixed result | GitHub Actions `34340023894` | `results/phase2/` |
| `phase3-stability-aware-v1` | Completed, exploratory | GitHub Actions `34347057969` | `results/phase3/` |
| `phase4-fault-testbed-v1` | Completed, synthetic mechanics | GitHub Actions `34348018741` | `results/phase4/` |
| `phase5-local-llm-diagnosis-v1` | Failed protocol execution, audit only | Local Ollama branch `phase5-local-results-20260909-172700` | `docs/phase5-v1-incident.md` |
| `phase5-local-llm-diagnosis-v2` | Completed | Local Ollama, commit `3a175e39a1a96415c2d6c597a40391f198a24722` | `results/phase5_v2/` |
| `phase6-communication-delay-v1` | Completed | GitHub Actions `34371460382` | `results/phase6/` |
| `phase7a-expanded-robustness-v1` | Completed, synthetic mechanics | GitHub Actions `34373347451` | `results/phase7a/` |
| `phase7b-end-to-end-local-llm-v1` | Completed | Local Ollama, commit `8ffab178a4635aeef54142c0bfcb8df28d63406d` | `results/phase7b/` |
| `phase8-resource-benchmark-v1` | Protocol frozen, local execution pending | Local hardware required | `experiments/configs/phase8_resource_benchmark.json` |

## Phase 1 provenance

- Frozen config SHA-256: `af06f715a46a90e1efc5c0c037e805bdd28cbe36ac1f4e20565aab8bb197448a`
- Dataset archive SHA-256: `6084d3ee3906381f2c98aa3773b6b2d77c82413503faa78f962196582e873733`
- Labels SHA-256: `057ce2d6c8875982bf4e5404aefea14efdcbce413d80826d2b737c95b59b7539`
- Source commit: `ff07c4027214d168f7034c5abc194fdce9b117eb`
- GitHub Actions run: `34337918870`
- Artifact SHA-256: `be4db9fefe18c52de90615b731f0d8dfc2dfbda2d951b0092408159629567b38`
- Result: total precision `0.2685`, recall `0.5700`, F1 `0.3651`, event recall `0.8286`.

## Phase 2 provenance

- Frozen config SHA-256: `fe761b5f3170249e798a31a2bf9dcef1f4331570937cb607feb4d52088f173b8`
- Dataset archive SHA-256: `6084d3ee3906381f2c98aa3773b6b2d77c82413503faa78f962196582e873733`
- Labels SHA-256: `057ce2d6c8875982bf4e5404aefea14efdcbce413d80826d2b737c95b59b7539`
- Source commit: `8144e60765fd154bf9b1eebefe40badaf8bb951b`
- GitHub Actions run: `34340023894`
- Artifact SHA-256: `bc04b31fe386f9829ff0e8aaaf9659ac09e28dbb02f9f1494e285586fd6854b5`
- Result: precision improved and false positives decreased, but recall, event recall, and total F1 decreased relative to Phase 1. The mixed result is retained rather than hidden.

## Phase 3 provenance

- Frozen config SHA-256: `934b79837c0e30ab3328590f5c1e0af488d5ccaf56f075557548f9c055685fb1`
- Dataset archive SHA-256: `6084d3ee3906381f2c98aa3773b6b2d77c82413503faa78f962196582e873733`
- Labels SHA-256: `057ce2d6c8875982bf4e5404aefea14efdcbce413d80826d2b737c95b59b7539`
- Source commit: `e35aa798551eaf3213a8585617da7b883d4ffa0a`
- GitHub Actions run: `34347057969`
- Artifact SHA-256: `774df8db3e8da1ac5729dac73719b69753a41e93c1da06fab8d8e6a81b0eb8cd`
- Result: total F1 `0.4054`, the strongest of Phases 1-3, with `28,606` fewer false positives than Phase 1.
- Interpretation: exploratory only because the detector design followed inspection of earlier SMAP/MSL benchmark outcomes.

## Phase 4 provenance

- Frozen config SHA-256: `fb3bd9b084be3c3a27eb714d99f9b40771cbedd2b9895b28aba35c4ae1637f20`
- Held-out seeds: `2201`, `2202`
- Fault classes: `6`
- Held-out synthetic scenarios: `12`
- GitHub Actions run: `34348018741`
- Artifact SHA-256: `a8ce4ce8fa21d5cb1cc8824d54d9bb605b02284118369bd9f2412367dfa7fd7f`
- Result: retrieval top-1 `1.0000`, expected safe-action allow `1.0000`, unsafe-action block `1.0000`.
- Interpretation: validates deterministic testbed/retrieval/safety mechanics only.

## Phase 5 provenance

### Phase 5 v1 incident

Phase 5 v1 completed 24 Ollama generation calls but is not a model-performance result. Qwen3 consumed the fixed output budget in its separate thinking channel and returned no usable final response to the parser. The execution is retained on branch `phase5-local-results-20260909-172700` and documented in `docs/phase5-v1-incident.md`.

### Phase 5 v2 valid local-LLM comparison

- Frozen config SHA-256: `f7bfc0170413d3dca4fe75660fc5feeed139c9423b15ab3efa51bb422256f867`
- Model: `qwen3:14b-q4_K_M` via local Ollama
- Held-out seeds: `2201`, `2202`
- Scenarios per condition: `12`
- Thinking disabled; JSON-schema structured output enforced
- Result commit: `3a175e39a1a96415c2d6c597a40391f198a24722`
- No-RAG diagnosis accuracy: `1.0000`
- RAG diagnosis accuracy: `1.0000`
- No-RAG expected-action match: `0.1667`
- RAG expected-action match: `1.0000`
- RAG expected-evidence match: `1.0000`
- Unsafe/unknown proposal rate: `0.0000` in both conditions
- Interpretation: on the small synthetic testbed, RAG materially changed action selection and evidence grounding, not fault-class accuracy.

## Phase 6 provenance

- Frozen config SHA-256: `0f732aecc8d07e2362df68191dd215c6e21a2c1659641094f87f74cad18bee6c`
- Phase 5 v2 input CSV SHA-256: `6d660899fbf754d7758886c1d6d49d1379ab390c9ee3e463265591e420c8f213`
- Reused condition: `llm_rag_top3`
- Reused synthetic scenarios: `12`
- GitHub Actions run: `34371460382`
- Result commit: `b42c1769a740a46aa53991970811511aef0931c5`
- Mean measured local decision latency: `27.159 s`
- Ground-link outage: local completion `1.0000`, ground-dependent completion `0.0000`
- Interpretation: deterministic counterfactual timing analysis that isolates propagation delay. It is not a live mission-network test.

## Phase 7 provenance

### Phase 7A expanded deterministic robustness

- Frozen config SHA-256: `7d362baaf5593bf8ce8525f5dbea87be81e4c115ca8a808d3eba0c225ad69391`
- Seeds: `3301` through `3310`
- Difficulties: `clean`, `distractor`, `partial`
- Fault classes: `6`
- Synthetic scenarios: `180`
- GitHub Actions run: `34373347451`
- Result commit: `c97e232fa70742b2e030410400791dbeb69454e7`
- Detector trigger rate: `1.0000`
- Nominal false-trigger point rate: `0.001296`
- Retrieval top-1 accuracy: `1.0000`
- Retrieval top-3 recall: `1.0000`
- Expected safe-action allow rate: `1.0000`
- Unsafe-action block rate: `1.0000`
- Integrated deterministic mechanics success: `1.0000`
- Interpretation: synthetic mechanics validation with no language model.

### Phase 7B expanded end-to-end local-LLM run

- Frozen config SHA-256: `caa72650628425e6f9248f0f9b1853c8bbc51f372c150c6ac7de3a7ea5b9388e`
- Source commit executed: `aabb14273a1afe7a41fb225c9913c5dd1e69997a`
- Result commit: `8ffab178a4635aeef54142c0bfcb8df28d63406d`
- Result-commit CI: GitHub Actions `34486399042`, conclusion `success`
- Model: `qwen3:14b-q4_K_M`, Ollama `0.33.3`, Python `3.11.9`
- Scenarios per condition: `36`; total model calls: `72`
- Difficulties: `clean`, `distractor`, `partial`
- Parse success: `1.0000` in both conditions
- Diagnosis accuracy: `1.0000` in both conditions
- No-RAG expected-action match: `0.1667`
- Full KARZOUN-X expected-action match: `1.0000`
- Full expected-evidence match: `1.0000`
- No-RAG end-to-end success: `0.1667`
- Full KARZOUN-X end-to-end success: `1.0000`
- Unsafe/unknown proposal rate: `0.0000` in both conditions
- Mean latency: `20.9429 s` no-RAG, `23.1414 s` full system
- Mean generation throughput: `5.1329 tok/s` no-RAG, `5.3349 tok/s` full system
- Counterfactual mean ground latency: `503.1414 s` at 240 s one-way delay and `2903.1414 s` at 1440 s one-way delay; ground-dependent completion is `0.0000` under outage.
- Interpretation: the expanded synthetic benchmark supports a narrow effect of retrieved evidence on action selection and grounding. The uniformly perfect full-system scores also show that this synthetic task remains highly separable; harder ambiguous and out-of-distribution stress tests are required before publication claims are strengthened.

A detailed interpretation is recorded in `docs/phase7b-analysis.md`.

## Phase 8 protocol

Phase 8 is frozen before execution in `experiments/configs/phase8_resource_benchmark.json`. It characterizes the full local KARZOUN-X path on one machine using 18 synthetic cases across clean, distractor, and partial variants. The runner samples system CPU and memory, Ollama process CPU/RSS, and NVIDIA GPU utilization, memory, and power when available at 0.5-second intervals. It records cold-start latency, warm latency, P95 latency, generation throughput, and raw resource samples. The measurement is explicitly a single-machine research benchmark and not a claim about flight hardware.
