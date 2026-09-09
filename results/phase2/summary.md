# KARZOUN-X Phase 2 Adaptive Temporal Results

Experiment: `phase2-adaptive-temporal-v1`
Detector threshold: `3.5`
Persistence requirement: `3` samples
Benchmark records evaluated: **82**
Labeled anomaly events: **105**
Telemetry test points: **517,764**

| Scope | Precision | Recall | F1 | Event recall | Records |
|---|---:|---:|---:|---:|---:|
| SMAP | 0.3686 | 0.4070 | 0.3869 | 0.4638 | 55 |
| MSL | 0.1604 | 0.3390 | 0.2177 | 0.7222 | 27 |
| total | 0.3256 | 0.3989 | 0.3585 | 0.5524 | 82 |

## Total change versus Phase 1

- Precision: +0.0570
- Recall: -0.1711
- F1: -0.0066
- Event recall: -0.2762
- False positives: -47064
- Predicted points: -58151

> Results are machine-generated from the frozen Phase 2 configuration.
> Phase 2 parameters were fixed before test-label evaluation.
