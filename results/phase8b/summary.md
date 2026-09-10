# KARZOUN-X Phase 8B Resource Instrumentation Replication

Experiment: `phase8b-resource-instrumentation-v1`
Model: `qwen3:14b-q4_K_M` via local Ollama
Measured synthetic cases: **18**

| Metric | Result |
|---|---:|
| End-to-end success | 1.0000 |
| Mean latency (s) | 22.724 |
| Median latency (s) | 22.118 |
| P95 latency (s) | 47.532 |
| Cold-start latency (s) | 47.532 |
| Warm mean latency (s) | 21.264 |
| Mean generation throughput (tok/s) | 5.599 |
| Peak process-family RSS (GiB) | 9.822 |
| Ollama reported model size (GiB) | 9.456 |
| Ollama reported VRAM allocation (GiB) | 6.113 |
| Mean system CPU (%) | 51.515 |
| Peak system CPU (%) | 91.000 |
| Peak GPU memory via nvidia-smi (MiB) | n/a |

> Phase 8B was designed after Phase 8 v1 revealed incomplete process/GPU observability.
> Model-performance metrics are secondary; this run is an instrumentation replication on one host.
> Results remain synthetic and are not evidence of flight readiness.
