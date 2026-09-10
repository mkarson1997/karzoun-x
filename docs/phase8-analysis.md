# Phase 8 Resource Benchmark Analysis

Phase 8 measured the full local KARZOUN-X path on a single Windows machine using 18 synthetic cases and a frozen protocol. The run completed all 18 cases successfully and preserved raw responses and resource samples.

## Valid execution

- Experiment: `phase8-resource-benchmark-v1`
- Frozen config SHA-256: `05a81a0eab8fd6a13f3ca64b775ddce120085d947673f3c185e2014b33710cac`
- Source commit executed: `c806d9673b1994e39fec01db2d0b38c2f2e856f0`
- Result commit: `69df26079cd853b962809fa38f6de023d69b182a`
- Result-commit CI: GitHub Actions `34497544736`, conclusion `success`
- Model: `qwen3:14b-q4_K_M` via Ollama `0.33.3`
- Python: `3.11.9`
- Synthetic cases: `18`
- Raw resource samples: `720`
- Automatic retries: none

## Performance results

| Metric | Result |
|---|---:|
| End-to-end success | 1.0000 |
| Mean latency | 21.575 s |
| Median latency | 20.607 s |
| P95 latency | 49.308 s |
| Cold-start latency | 49.308 s |
| Warm mean latency | 19.944 s |
| Mean generation throughput | 5.860 tok/s |

The first call followed a verified Ollama model unload and was therefore treated as the cold-start case. It took 49.308 s, while the remaining 17 calls averaged 19.944 s. This large cold-start penalty is relevant to deployment design because keeping the model resident can materially change time-to-decision.

## System resource observations

| Metric | Result |
|---|---:|
| Mean system CPU | 49.575% |
| Peak system CPU | 95.1% |
| Peak system memory used | 27,592,134,656 bytes |
| Peak sampled Ollama RSS | 74,756,096 bytes |
| NVIDIA GPU telemetry | unavailable |

The system-level CPU and memory measurements are valid observations of the host during the benchmark, but they include unrelated operating-system and foreground activity. They should not be interpreted as exclusive KARZOUN-X resource consumption.

The sampled Ollama RSS value is retained exactly as measured but should not be used as an estimate of total model memory. On this Windows/Ollama configuration the sampler matched process names containing `ollama`, while the model may use separate runner/server processes or memory mappings not represented by that number. A follow-up instrumentation pass is required before making a process-memory claim.

NVIDIA telemetry was unavailable because `nvidia-smi` could not be located by the runner. Consequently, Phase 8 v1 makes no GPU-utilization, VRAM, or GPU-power claim.

## Publication interpretation

Phase 8 v1 supports a narrow single-machine latency and host-load characterization. It establishes a measured cold-start penalty, warm inference latency, generation throughput, and system-level CPU/memory observations. It does **not** yet establish total model RSS, GPU resource use, energy efficiency, flight-hardware suitability, or cross-machine generality.

A follow-up Phase 8B instrumentation replication is therefore planned before the resource-aware manuscript claim is finalized. Phase 8B will account for Ollama/llama/runner process families and query Ollama's `/api/ps` endpoint for model size and reported VRAM allocation even when `nvidia-smi` is unavailable.
