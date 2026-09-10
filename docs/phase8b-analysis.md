# Phase 8B Resource Instrumentation Analysis

Phase 8B was added after the Phase 8 v1 observability review showed that the parent Ollama process RSS and missing `nvidia-smi` telemetry were not sufficient to support a defensible model-memory claim. Phase 8 v1 remains immutable and is retained as the original timing/system-load run.

Phase 8B repeated the 18-case local benchmark on a new deterministic seed and expanded instrumentation to the Ollama/runner process family plus Ollama `/api/ps`. The machine-generated run completed all 18 synthetic cases successfully. Mean end-to-end latency was 22.724 s, median latency was 22.118 s, cold-start latency was 47.532 s, warm mean latency was 21.264 s, and mean generation throughput was 5.599 tok/s.

The improved process accounting observed a peak process-family RSS of 10,546,618,368 bytes (9.822 GiB). Ollama `/api/ps` reported a model size of 10,153,550,149 bytes (9.456 GiB) and a VRAM allocation of 6,564,253,531 bytes (6.113 GiB). Mean system CPU was 51.515% and peak system CPU was 91.0%. The matched process family included `ollama.exe`, `ollama app.exe`, and `llama-server.exe`.

These measurements strengthen the resource-aware characterization, but they do not establish flight-hardware feasibility. `/api/ps` VRAM is an Ollama-reported allocation rather than an independent hardware-sensor measurement, because `nvidia-smi` remained unavailable in this environment. System-wide memory and CPU also include unrelated host activity. The experiment is a single-machine Windows characterization of a synthetic workload, not a spacecraft hardware benchmark.

For publication, Phase 8 v1 should be cited for the original timing/system-load run and Phase 8B for the corrected process-family/model-allocation instrumentation. The 0.070 GiB parent-process RSS from Phase 8 v1 must not be presented as total model memory.
