# KARZOUN-X Phase 5 Local LLM Diagnostic Results

Experiment: `phase5-local-llm-diagnosis-v1`
Model: `qwen3:14b-q4_K_M` via local Ollama
Held-out synthetic scenarios per condition: **12**

| Metric | No RAG | RAG top-3 |
|---|---:|---:|
| Parse success | 0.0000 | 0.0000 |
| Diagnosis accuracy | 0.0000 | 0.0000 |
| Expected action match | 0.0000 | 0.0000 |
| Diagnosis + expected action | 0.0000 | 0.0000 |
| Safety allow rate | 0.0000 | 0.0000 |
| Unsafe/unknown proposal rate | 0.0000 | 0.0000 |
| Expected evidence match | n/a | n/a |
| Mean latency (s) | 0.000 | 0.000 |
| Mean generation tokens/s | 5.431 | 5.702 |

> Ground-truth fault labels were used for scoring only and were not inserted into prompts.
> These are synthetic diagnostic results and are not evidence of flight readiness.
