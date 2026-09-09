# KARZOUN-X Phase 3 Stability-Aware Results

Experiment: `phase3-stability-aware-v1`
Detector threshold: `3.5`
Study role: exploratory iterative refinement; not a confirmatory untouched holdout.
Benchmark records evaluated: **82**
Labeled anomaly events: **105**
Telemetry test points: **517,764**

| Scope | Precision | Recall | F1 | Event recall | Records |
|---|---:|---:|---:|---:|---:|
| SMAP | 0.3667 | 0.5581 | 0.4426 | 0.6667 | 55 |
| MSL | 0.1474 | 0.3793 | 0.2123 | 0.8611 | 27 |
| total | 0.3257 | 0.5366 | 0.4054 | 0.7333 | 82 |

## Total change versus Phase 1
- Precision: +0.0571
- Recall: -0.0333
- F1: +0.0403
- Event recall: -0.0952
- False positives: -28606

## Total change versus Phase 2
- Precision: +0.0001
- Recall: +0.1378
- F1: +0.0468
- Event recall: +0.1810
- False positives: +18458

> Results are machine-generated from the frozen Phase 3 configuration.
> Phase 3 was designed after observing prior phases, so it is reported as exploratory.
