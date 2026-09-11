# KARZOUN-X Phase 9 Hard-Stress Local LLM Results

Experiment: `phase9-hard-stress-local-llm-v1`
Model: `qwen3:14b-q4_K_M` via local Ollama
Synthetic stress cases: **60**

| Metric | Result |
|---|---:|
| Parse success | 1.0000 |
| Policy-conformant | 0.4333 |
| Safe defer | 0.2917 |
| Adversarial evidence resistance | 1.0000 |
| Unsafe-action proposal rate | 0.0000 |
| Unsafe false authorization | n/a |
| Mean latency (s) | 24.6927 |

## Results by stress type

| Stress type | N | Policy conformant | Unsafe proposal |
|---|---:|---:|---:|
| adversarial_evidence | 12 | 1.0000 | 0.0000 |
| ambiguous_dual_signature | 12 | 0.1667 | 0.0000 |
| conflicting_retrieval | 12 | 0.0000 | 0.0000 |
| missing_evidence | 12 | 0.0000 | 0.0000 |
| out_of_distribution | 12 | 1.0000 | 0.0000 |

> This is a synthetic hard-stress benchmark. It evaluates a precommitted fail-safe response policy, not flight readiness.
> Retrieved evidence is deliberately perturbed in some cases; source labels are used for scenario construction/scoring only.
