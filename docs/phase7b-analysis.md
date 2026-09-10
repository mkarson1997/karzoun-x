# Phase 7B End-to-End Analysis

Phase 7B is the first expanded local-LLM experiment that executes the synthetic detector, optional retrieval, local Qwen3 reasoning, deterministic safety gate, and communication-delay analysis in one benchmark harness.

## Valid execution

- Experiment: `phase7b-end-to-end-local-llm-v1`
- Frozen configuration SHA-256: `caa72650628425e6f9248f0f9b1853c8bbc51f372c150c6ac7de3a7ea5b9388e`
- Model: `qwen3:14b-q4_K_M`
- Ollama: `0.33.3`
- Python: `3.11.9`
- Scenarios per condition: `36`
- Conditions: `llm_no_rag` and `karzoun_x_full`
- Local result commit: `8ffab178a4635aeef54142c0bfcb8df28d63406d`
- CI for the result commit: GitHub Actions run `34486399042`, conclusion `success`

The benchmark completed all 72 scheduled calls. Structured response parsing succeeded for every call. No automatic retries were used, and ground-truth fault labels were used only for scoring.

## Main comparison

| Metric | No RAG | Full KARZOUN-X |
|---|---:|---:|
| Detector trigger rate | 1.0000 | 1.0000 |
| Parse success rate | 1.0000 | 1.0000 |
| Diagnosis accuracy | 1.0000 | 1.0000 |
| Expected-action match | 0.1667 | 1.0000 |
| Diagnosis + expected action | 0.1667 | 1.0000 |
| Expected-evidence match | n/a | 1.0000 |
| Safety allow rate | 1.0000 | 1.0000 |
| Unsafe/unknown proposal rate | 0.0000 | 0.0000 |
| End-to-end success | 0.1667 | 1.0000 |
| Mean model latency | 20.9429 s | 23.1414 s |
| Median model latency | 19.7785 s | 23.0229 s |
| Mean generation throughput | 5.1329 tok/s | 5.3349 tok/s |

On this synthetic benchmark, retrieval did not alter fault-class accuracy because both conditions classified all 36 cases correctly. Its measurable effect was on action selection and evidence grounding: expected-action match increased from 6/36 to 36/36, and the full condition selected the expected evidence document in 36/36 cases. The mean latency increase associated with the full condition was approximately 2.20 seconds per case.

## Difficulty slices

The full condition achieved diagnosis, action, evidence, and end-to-end success rates of 1.0000 on each of the 12 clean, 12 distractor, and 12 partial-information cases.

This uniform result is useful implementation evidence but also indicates that the current synthetic task remains highly separable for this model and retrieval corpus. It should not be presented as evidence of real-spacecraft diagnostic accuracy. A stronger paper therefore requires harder ambiguous, conflicting, out-of-distribution, and policy-edge cases rather than simply increasing the number of similarly separable examples.

## Communication interpretation

Using measured full-condition inference latency as the compute component, the deterministic counterfactual timing model produced the following mean ground-dependent completion times:

| Reference profile | Mean completion |
|---|---:|
| Zero propagation delay | 23.1414 s |
| Mars-near, 240 s one-way | 503.1414 s |
| Mars-far, 1440 s one-way | 2903.1414 s |
| Ground-link outage | unavailable |

These values isolate propagation delay and are not measurements of a live mission network. They do not include DSN scheduling, relay delay, packet loss, human approval, or different ground compute resources.

## Publication interpretation

Phase 7B supports a narrow claim: within the frozen synthetic benchmark, adding the local retrieval context to the same local model materially improved expected diagnostic-action selection and evidence grounding while preserving successful parsing and deterministic safety authorization. It does not establish flight readiness, real-spacecraft validity, general reliability, or superiority to state-of-the-art fault-management systems.

The next experimental requirement is resource characterization on the local hardware, followed by a deliberately harder stress suite and statistical/ablation analysis before manuscript finalization.
