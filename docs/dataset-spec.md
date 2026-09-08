# Phase 1 Dataset Specification

## Upstream benchmark

KARZOUN-X Phase 1 uses the public SMAP/MSL spacecraft telemetry benchmark distributed with the Telemanom project.

The upstream metadata reports:

- 55 SMAP telemetry channels
- 27 MSL telemetry channels
- 82 unique telemetry channels total
- 69 labeled SMAP anomaly sequences
- 36 labeled MSL anomaly sequences
- 105 labeled anomaly sequences total
- 496,444 telemetry values evaluated in the original benchmark

The upstream data are anonymized with respect to time, channel identifiers, and command semantics. Telemetry values are pre-scaled and the benchmark includes pre-split train/test arrays.

## Source of truth

Upstream repository:
`https://github.com/khundman/telemanom`

Labels:
`labeled_anomalies.csv`

KARZOUN-X does not treat the original Telemanom performance numbers as KARZOUN-X results. They are prior-work baselines only.

## Local data policy

Raw dataset arrays are excluded from git. Researchers acquire them locally, preserve upstream provenance, and record integrity hashes before running publication-grade experiments.

## Phase 1 freeze

The first KARZOUN-X baseline uses:

- training data only for fitting detector statistics
- labeled test intervals only for evaluation
- pointwise precision, recall, and F1
- event recall, where a labeled interval counts as detected if at least one predicted anomaly falls inside it
- per-channel and aggregate reporting

The initial robust z-score detector is a transparent sanity-check baseline, not a claim of state-of-the-art performance.
