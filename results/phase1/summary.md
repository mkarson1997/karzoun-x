# KARZOUN-X Phase 1 Baseline Results

Experiment: `phase1-robust-zscore-v1`  
Detector: robust z-score (MAD), threshold `3.5`  
Benchmark records evaluated: **82**  
Labeled anomaly events: **105**  
Telemetry test points: **517,764**

| Scope | Precision | Recall | F1 | Event recall | Records |
|---|---:|---:|---:|---:|---:|
| SMAP | 0.2972 | 0.5819 | 0.3934 | 0.7971 | 55 |
| MSL | 0.1449 | 0.4825 | 0.2228 | 0.8889 | 27 |
| Total | 0.2685 | 0.5700 | 0.3651 | 0.8286 | 82 |

These values were generated automatically by GitHub Actions run `34337918870` from the frozen Phase 1 configuration. The fixed threshold was declared before evaluation; no score was manually edited.

## Provenance

- Source dataset: public SMAP/MSL benchmark distributed on Kaggle from the Telemanom/NASA JPL anomaly-detection work.
- Dataset archive SHA-256: `6084d3ee3906381f2c98aa3773b6b2d77c82413503faa78f962196582e873733`
- Labels SHA-256: `057ce2d6c8875982bf4e5404aefea14efdcbce413d80826d2b737c95b59b7539`
- Experiment config SHA-256: `af06f715a46a90e1efc5c0c037e805bdd28cbe36ac1f4e20565aab8bb197448a`
- Workflow run: https://github.com/mkarson1997/karzoun-x/actions/runs/34337918870
- Source commit evaluated: `ff07c4027214d168f7034c5abc194fdce9b117eb`
- Artifact SHA-256: `be4db9fefe18c52de90615b731f0d8dfc2dfbda2d951b0092408159629567b38`

## Interpretation

This deliberately simple detector catches **87 of 105 labeled anomaly events**, but its pointwise precision is low because it produces many false-positive points. That is useful as a weak transparent baseline: later temporal and AI-assisted methods must improve precision and F1 without sacrificing event coverage.

The upstream metadata contains a repeated `P-2` record. Phase 1 preserves the source benchmark rows exactly rather than silently rewriting labels. Future benchmark reporting will distinguish benchmark records from unique channel identifiers.
