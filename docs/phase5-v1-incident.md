# Phase 5 v1 incident: empty final responses from Qwen3 thinking output

## Status

Phase 5 v1 completed 24 local Ollama generation calls, but the run is **not a valid measurement of diagnostic accuracy** and must not be interpreted as a 0% model result.

The machine-generated result branch is retained for auditability:

`phase5-local-results-20260909-172700`

It is intentionally not merged into `main` as a scientific result.

## Observed evidence

For all sampled v1 records, the Ollama API metadata reported successful generation work (`eval_count=220`) and `done_reason="length"`, while the captured final `response` field was empty. The model consumed the configured output budget, but the benchmark parser received no final answer to score.

This pattern is consistent with a thinking-capable Qwen3 model emitting reasoning separately from the final response. The v1 request did not explicitly set the Ollama `think` field and only read the `response` field.

## Root cause

The issue was an experiment-interface mismatch, not evidence that the model failed all diagnostic cases:

1. Qwen3 is a thinking-capable model.
2. Ollama separates thinking output from the final answer.
3. The v1 request did not explicitly disable thinking.
4. The fixed `num_predict=220` budget was exhausted before a final `response` was produced.
5. The parser therefore received an empty string for every case.

## Protocol correction for v2

Phase 5 v2 changes only the response transport contract:

- explicitly sets `think=false`;
- uses Ollama JSON-schema structured output;
- keeps the same local model, temperature, `num_predict=220`, held-out seeds, fault catalogue, RAG method, safety gate, and scoring targets;
- records both the final `response` and the separate `thinking` field for auditability;
- records real request latency even when response parsing fails;
- prints per-case progress so long local inference is visible.

The protocol amendment is declared in `experiments/configs/phase5_local_llm_v2.json` before the v2 result is accepted.

## Scientific handling

The v1 branch is a failed protocol execution and should remain separate from model-performance tables. The valid Phase 5 comparison will use the v2 runner and will be reported only after machine-generated v2 outputs are inspected and preserved.
