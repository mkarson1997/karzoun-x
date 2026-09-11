# KARZOUN-X Phase 10 Statistical Synthesis

This is a retrospective statistical synthesis of already-frozen experiment results. It does not create new model outputs and is not a preregistered confirmatory trial.

## Phase 7B retrieval ablation

- No-RAG expected-action match: 6/36 = 0.1667 (95% Wilson 0.0787–0.3189).
- Full KARZOUN-X expected-action match: 36/36 = 1.0000 (95% Wilson 0.9036–1.0000).
- Absolute paired rate difference: 83.3%.
- Exact two-sided McNemar p-value: `1.863e-09` with 0 no-RAG-only and 30 full-system-only correct pairs.

The paired test quantifies the action-selection difference on this synthetic testbed; it does not establish external validity for real spacecraft operations.

## Phase 9 hard-stress uncertainty

- Overall policy conformance: 26/60 = 0.4333 (95% Wilson 0.3157–0.5590).
- Safe defer on precommitted-unknown cases: 14/48 = 0.2917 (95% Wilson 0.1824–0.4318).
- Unsafe-action proposals: 0/60 = 0.0000 (95% Wilson 0.0000–0.0602).

| Stress family | Policy conformance with 95% Wilson interval |
|---|---:|
| adversarial_evidence | 12/12 = 1.0000 (95% Wilson 0.7575–1.0000) |
| ambiguous_dual_signature | 2/12 = 0.1667 (95% Wilson 0.0470–0.4480) |
| conflicting_retrieval | 0/12 = 0.0000 (95% Wilson 0.0000–0.2425) |
| missing_evidence | 0/12 = 0.0000 (95% Wilson 0.0000–0.2425) |
| out_of_distribution | 12/12 = 1.0000 (95% Wilson 0.7575–1.0000) |

## Resource replication

- Phase 8 mean latency: `21.575 s`; Phase 8B: `22.724 s`.
- Phase 8 warm mean: `19.944 s`; Phase 8B: `21.264 s`.
- Descriptive single-host replication only; Phase 8 and Phase 8B used different synthetic seeds and are not treated as paired inferential samples.

## Interpretation

The combined evidence supports two simultaneous conclusions. First, retrieved evidence strongly changed action selection on the clean/separable Phase 7B benchmark. Second, Phase 9 shows that the same local model is not reliably calibrated to abstain when evidence is ambiguous, conflicting, or missing. Deterministic action gating prevented explicitly hazardous proposals in the observed stress run, but it cannot by itself guarantee epistemic correctness for low-risk diagnostic actions.
