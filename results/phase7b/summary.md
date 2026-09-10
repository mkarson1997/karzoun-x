# KARZOUN-X Phase 7B End-to-End Local LLM Results

Experiment: `phase7b-end-to-end-local-llm-v1`
Model: `qwen3:14b-q4_K_M` via local Ollama
Synthetic scenarios per condition: **36**

| Metric | No RAG | Full KARZOUN-X |
|---|---:|---:|
| Detector trigger | 1.0000 | 1.0000 |
| Parse success | 1.0000 | 1.0000 |
| Diagnosis accuracy | 1.0000 | 1.0000 |
| Expected action match | 0.1667 | 1.0000 |
| Diagnosis + expected action | 0.1667 | 1.0000 |
| Safety allow rate | 1.0000 | 1.0000 |
| Unsafe/unknown proposal rate | 0.0000 | 0.0000 |
| End-to-end success | 0.1667 | 1.0000 |
| Expected evidence match | n/a | 1.0000 |
| Mean latency (s) | 20.9429 | 23.1414 |

## Full-system results by difficulty

| Difficulty | Diagnosis | Action | Evidence | End-to-end |
|---|---:|---:|---:|---:|
| clean | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| distractor | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| partial | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Counterfactual ground-dependent timing

| Profile | OWLT (s) | Completion | Mean ground latency (s) |
|---|---:|---:|---:|
| zero_delay_reference | 0.0 | 1.0000 | 23.1414 |
| mars_near_reference | 240.0 | 1.0000 | 503.1414 |
| mars_far_reference | 1440.0 | 1.0000 | 2903.1414 |
| ground_link_outage | 0.0 | 0.0000 | n/a |

> Ground-truth fault labels are used only for scoring and are not inserted into prompts.
> Results are synthetic; communication values are deterministic counterfactual timing estimates.
> KARZOUN-X remains research software and is not flight-qualified.
