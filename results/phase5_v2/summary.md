# KARZOUN-X Phase 5 v2 Local LLM Diagnostic Results

Experiment: `phase5-local-llm-diagnosis-v2`
Model: `qwen3:14b-q4_K_M` via local Ollama
Held-out synthetic scenarios per condition: **12**

Protocol correction from v1: Qwen3 thinking is explicitly disabled and Ollama JSON-schema structured output is enforced. The held-out scenarios and evaluation targets are unchanged.

| Metric | No RAG | RAG top-3 |
|---|---:|---:|
| Parse success | 1.0000 | 1.0000 |
| Diagnosis accuracy | 1.0000 | 1.0000 |
| Expected action match | 0.1667 | 1.0000 |
| Diagnosis + expected action | 0.1667 | 1.0000 |
| Safety allow rate | 1.0000 | 1.0000 |
| Unsafe/unknown proposal rate | 0.0000 | 0.0000 |
| Expected evidence match | n/a | 1.0000 |
| Mean latency (s) | 24.6858 | 27.1588 |
| Mean generation tokens/s | 5.0083 | 5.1903 |

> Ground-truth fault labels were used for scoring only and were not inserted into prompts.
> These are synthetic diagnostic results and are not evidence of flight readiness.
