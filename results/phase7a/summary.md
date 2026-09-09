# KARZOUN-X Phase 7A Expanded Robustness Results

Experiment: `phase7a-expanded-robustness-v1`
Synthetic scenarios: **180**

Phase 7A expands the synthetic mechanics testbed before the next local-LLM run. Explicit fault labels are removed from telemetry text, and cases include clean, distractor, and partial-information variants. No language model participates in this phase.

| Scope | Scenarios | Detector trigger | Nominal false-point rate | Retrieval top-1 | Retrieval top-3 | Safe allow | Unsafe block | Integrated success |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| overall | 180 | 1.0000 | 0.0013 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| clean | 60 | 1.0000 | 0.0006 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| distractor | 60 | 1.0000 | 0.0022 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| partial | 60 | 1.0000 | 0.0011 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

> Phase 7A is a deterministic synthetic robustness test. It validates expanded detector/retrieval/safety mechanics only and is not evidence of spacecraft or language-model performance.
