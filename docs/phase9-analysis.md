# Phase 9 hard-stress analysis

Phase 9 is the first KARZOUN-X local-LLM experiment designed specifically to make the earlier synthetic benchmark fail in informative ways. The protocol was frozen before execution and used 60 deterministic synthetic cases across ambiguity, conflicting retrieval, out-of-distribution telemetry, adversarial evidence, and missing evidence. The model was `qwen3:14b-q4_K_M` through local Ollama with `think=false`, temperature `0.0`, schema-constrained JSON, no automatic retries, and raw-response preservation.

## Valid execution

All 60 model calls completed and all 60 responses parsed successfully. The result commit is `f7efc3db67c9ae152daae7c08c40c2369c94e31c`; the result-commit CI run is `34587337630` and completed successfully. The frozen configuration SHA-256 is `eb215e07a2e514da49bf21281b33152f14d34ad3c5086900b654fb15a59219e7`.

## Main result

The experiment did **not** reproduce the perfect full-system scores seen on the earlier separable synthetic testbed. Overall policy conformance fell to `26/60 = 0.4333` (Wilson 95% CI approximately `0.3157–0.5590`). Among the 48 cases whose precommitted correct response was explicit uncertainty plus safe defer, only `14/48 = 0.2917` conformed (Wilson 95% CI approximately `0.1824–0.4318`).

This is a useful negative result rather than a protocol failure. It demonstrates that success on clean or lexically separable synthetic faults does not imply reliable epistemic abstention when the evidence becomes ambiguous, contradictory, absent, or outside the local knowledge catalogue.

## Stress-family behavior

| Stress family | N | Policy conformant | Main interpretation |
|---|---:|---:|---|
| Adversarial evidence | 12 | 12/12 = 1.0000 | The model ignored embedded unsafe instructions and followed the trusted-policy framing in every case. |
| Out of distribution | 12 | 12/12 = 1.0000 | The model correctly selected `unknown` plus `collect_more_telemetry` in every OOD case. |
| Ambiguous dual signature | 12 | 2/12 = 0.1667 | The model usually resolved ambiguity prematurely instead of abstaining. |
| Conflicting retrieval | 12 | 0/12 = 0.0000 | Wrong retrieved evidence often anchored the model rather than triggering uncertainty. |
| Missing evidence | 12 | 0/12 = 0.0000 | The model usually inferred a catalogue fault from telemetry even though the frozen policy required abstention when retrieval evidence was missing. |

For a 12/12 result, the Wilson 95% lower bound is only about `0.7575`; for a 0/12 result, the upper bound is about `0.2425`. These intervals matter because each stress family is intentionally small. The observed pattern is clear, but the experiment is not large enough to claim population-level certainty.

## Safety interpretation

No unsafe action was proposed in any of the 60 cases (`0/60`; Wilson 95% upper bound approximately `0.0602`), and therefore no unsafe action was falsely authorized. This is encouraging but must be interpreted narrowly.

The current `SafetyGate` is an **action-hazard gate**, not an epistemic-correctness gate. It can prevent explicitly denied or excessive-severity actions, but it does not know whether a low-risk diagnostic action was selected for the wrong reason or under insufficient evidence. Phase 9 exposed exactly this distinction: many nonconformant cases still proposed actions from the low-risk allow-list. Consequently, a zero unsafe-action proposal rate does not imply correct diagnosis, correct grounding, or appropriate abstention.

## What Phase 9 says about RAG

Earlier Phase 5 v2 and Phase 7B results showed a large benefit from retrieval on clean synthetic cases, especially for expected action selection. Phase 9 adds the other half of the story: retrieval can also become a liability when the retrieved material is wrong, contradictory, or absent.

The conflicting-retrieval family is particularly important. Policy conformance was `0/12`, despite parse success remaining `12/12`. This means the failure was not formatting or transport. It was decision behavior under misleading evidence. The result supports treating retrieval quality and evidence sufficiency as first-class safety variables instead of assuming that the presence of retrieved context is automatically beneficial.

## Publication-safe claims

Phase 9 supports the following narrow claims:

- the local model produced schema-valid outputs on all 60 hard-stress cases;
- the prompt/policy resisted the tested adversarial evidence injections in all 12 cases;
- the model abstained correctly on all 12 tested OOD cases;
- the model was weak at abstaining under ambiguous dual signatures, conflicting retrieval, and missing evidence;
- no explicitly unsafe action was proposed in this 60-case synthetic run;
- deterministic action gating and epistemic uncertainty handling are separate problems.

Phase 9 does **not** support claims of flight readiness, general spacecraft diagnosis accuracy, certified safety, or robustness to arbitrary prompt injection or retrieval corruption.

## Design implication

The next system-level improvement should not simply make the language model more assertive. Phase 9 indicates a need for an evidence-sufficiency / uncertainty boundary upstream of action authorization. Any such mechanism must be evaluated on new frozen cases and clearly labeled as post-Phase-9 design work rather than retroactively re-scoring Phase 9 as if the mechanism had been precommitted.
