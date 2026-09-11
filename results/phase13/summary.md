# KARZOUN-X Phase 13 Final Statistical Synthesis

## Phase 11 epistemic-gate mitigation

- baseline policy conformance: **57/108 = 0.5278 [0.4343, 0.6194]**
- gated policy conformance: **108/108 = 1.0000 [0.9657, 1.0000]**
- known-case preservation: **36/36 = 1.0000 [0.9036, 1.0000]**
- required-defer capture: **72/72 = 1.0000 [0.9493, 1.0000]**
- paired exact McNemar p: **8.881784197e-16**

## Phase 12 model/resource ablation

| Model | Gated policy with Wilson 95% CI | Known preservation | Required defer |
|---|---|---|---|
| small | 35/36 = 0.9722 [0.8583, 0.9951] | 11/12 = 0.9167 [0.6461, 0.9851] | 24/24 = 1.0000 [0.8620, 1.0000] |
| medium | 36/36 = 1.0000 [0.9036, 1.0000] | 12/12 = 1.0000 [0.7575, 1.0000] | 24/24 = 1.0000 [0.8620, 1.0000] |
| large | 36/36 = 1.0000 [0.9036, 1.0000] | 12/12 = 1.0000 [0.7575, 1.0000] | 24/24 = 1.0000 [0.8620, 1.0000] |

### Pairwise exact McNemar tests

- `small_vs_medium`: discordant left-only=0, right-only=1, p=1
- `small_vs_large`: discordant left-only=0, right-only=1, p=1
- `medium_vs_large`: discordant left-only=0, right-only=0, p=1

### Pareto-efficient model labels

`medium`, `small`

> Pareto efficiency here jointly maximizes gated policy conformance while minimizing warm mean latency and peak model-process-family RSS.

> These statistics support the stated synthetic and single-host scope only; they do not establish flight readiness or operational spacecraft safety.
