# KARZOUN-X Phase 11 Epistemic Sufficiency Gate Results

Experiment: `phase11-epistemic-sufficiency-gate-v1`
Model: `qwen3:14b-q4_K_M` via local Ollama
Held-out synthetic cases: **108**

| Metric | Baseline / result | Gated / result |
|---|---:|---:|
| Policy-conformant rate | 0.5278 | 1.0000 |
| Absolute conformance delta | n/a | 0.4722 |
| Known-case preservation | n/a | 1.0000 |
| Required-defer capture | n/a | 1.0000 |
| Epistemic defer rate | n/a | 0.6667 |

## Paired exact comparison

- both correct: **57**
- baseline only correct: **0**
- gated only correct: **51**
- both wrong: **0**
- exact McNemar p: **8.881784197e-16**

## Results by family

| Family | N | Baseline conformant | Gated conformant | Defer rate |
|---|---:|---:|---:|---:|
| adversarial_evidence | 18 | 1.0000 | 1.0000 | 0.0000 |
| ambiguous_dual_signature | 18 | 0.1667 | 1.0000 | 1.0000 |
| clean_known | 18 | 1.0000 | 1.0000 | 0.0000 |
| conflicting_retrieval | 18 | 0.0000 | 1.0000 | 1.0000 |
| missing_evidence | 18 | 0.0000 | 1.0000 | 1.0000 |
| out_of_distribution | 18 | 1.0000 | 1.0000 | 1.0000 |

> Phase 11 was designed after Phase 9 failure analysis. Gate thresholds were frozen before these held-out seeds were executed.
> The gate uses observable telemetry/evidence agreement only; ground-truth fault labels are used for scoring, not gate decisions.
> This remains a synthetic research benchmark and is not evidence of flight qualification.
