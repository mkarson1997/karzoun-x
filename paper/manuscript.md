# KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture for Autonomous Spacecraft Fault Diagnosis Under Communication Delay

**Mahmoud Karzoun**  
ORCID: 0009-0006-2752-7744

> Status: working manuscript. Phase 1 and Phase 2 telemetry experiments have been executed; full KARZOUN-X reasoning, safety, communication-delay, and resource experiments remain in progress.

## Abstract

Deep-space spacecraft increasingly require onboard autonomy because communication latency, bandwidth constraints, and intermittent connectivity can limit immediate ground intervention. This work proposes KARZOUN-X, a research architecture that combines telemetry anomaly detection, local retrieval-augmented generation, a resource-constrained local language model, and a deterministic safety gate for spacecraft fault diagnosis and decision support. The system is designed to separate probabilistic diagnostic reasoning from action authorization and to preserve evidence for auditability. We define an evaluation protocol using historical spacecraft telemetry and simulated communication constraints. Two frozen experiments on the public SMAP/MSL benchmark establish transparent anomaly-detection reference points. The second experiment substantially reduced false positives and increased precision, but lost recall and event coverage, producing a slightly lower overall F1 score. This mixed result is retained rather than optimized away after inspection. Full-system conclusions are deferred until the remaining experiments are complete.

## 1. Introduction

Autonomous spacecraft operations require reliable detection and handling of off-nominal behavior while respecting strict safety constraints. Recent work has explored both autonomous fault-management systems and language-model-based spacecraft agents. However, a language model that can generate plausible operational advice is not equivalent to a safety-authorized controller.

KARZOUN-X investigates a hybrid approach: use local AI for evidence-grounded diagnostic assistance while preserving a deterministic authorization boundary between model output and simulated action execution.

### Contributions targeted by this study

1. A reproducible hybrid architecture for local spacecraft fault-diagnosis research.
2. Explicit separation of probabilistic reasoning and deterministic action authorization.
3. Evaluation under delayed, intermittent, and unavailable ground communication.
4. Resource-aware measurement of latency and compute requirements for local inference.
5. An open experiment protocol intended to make both positive and negative findings auditable.

## 2. Related Work

### 2.1 Spacecraft telemetry anomaly detection

TODO: summarize Telemanom and subsequent spacecraft telemetry anomaly-detection literature.

### 2.2 Autonomous fault management

TODO: summarize NASA/JPL work on autonomous fault detection, isolation, recovery, and event-driven onboard operations.

### 2.3 Language models for spacecraft autonomy

TODO: compare recent LLM-based spacecraft-agent work with the narrower KARZOUN-X fault-diagnosis and safety-gating objective.

### 2.4 Safety-constrained AI decision support

TODO: define the distinction between recommendation, authorization, and control.

## 3. Research Question and Hypotheses

### RQ1
Can a local LLM with retrieval improve diagnosis quality relative to ungrounded LLM reasoning?

### RQ2
Can deterministic safety gating reduce unsafe action authorization without eliminating useful low-risk recommendations?

### RQ3
How do communication constraints affect end-to-end decision latency and system usefulness?

### RQ4
What diagnostic quality is retained under practical local compute constraints?

## 4. KARZOUN-X Architecture

Describe telemetry ingestion, anomaly detection, local retrieval, local reasoning, deterministic safety policy, communication simulation, and audit logging.

## 5. Dataset and Experimental Setup

The initial benchmark uses the public SMAP/MSL telemetry anomaly dataset distributed from the Telemanom/NASA JPL anomaly-detection work. Both completed telemetry experiments preserve the upstream benchmark records and fit detector statistics only on the training telemetry for each record. The first telemetry column is evaluated against the published anomaly intervals in the test split.

For the completed runs, the downloaded dataset archive had SHA-256 `6084d3ee3906381f2c98aa3773b6b2d77c82413503faa78f962196582e873733`, and the extracted label file had SHA-256 `057ce2d6c8875982bf4e5404aefea14efdcbce413d80826d2b737c95b59b7539`. The upstream label metadata includes a repeated `P-2` benchmark record; the experiments preserve the source rows rather than silently rewriting them. Consequently, this manuscript uses the term *benchmark record* when reporting row counts.

The frozen Phase 1 configuration is `experiments/configs/phase1_robust_zscore.json`, whose executed content had SHA-256 `af06f715a46a90e1efc5c0c037e805bdd28cbe36ac1f4e20565aab8bb197448a`.

The frozen Phase 2 configuration is `experiments/configs/phase2_adaptive_temporal.json`, whose executed content had SHA-256 `fe761b5f3170249e798a31a2bf9dcef1f4331570937cb607feb4d52088f173b8`. Phase 2 retained a threshold of 3.5, used the training median as the center, selected the larger of MAD-derived and IQR-derived robust scale estimates, fell back to training standard deviation if both robust estimates collapsed, and required at least three consecutive flagged samples for an anomaly run to survive temporal filtering. These parameters were frozen before evaluation against test labels.

## 6. Evaluation Methodology

### Detection metrics
- pointwise precision
- pointwise recall
- pointwise F1
- event recall, where a labeled event is counted as detected if at least one point in its interval is flagged
- false-positive and false-negative counts

### Reasoning metrics
- diagnostic accuracy
- evidence support rate
- unsupported-claim rate
- latency

### Safety metrics
- unsafe-action proposal rate
- unsafe-action authorization rate
- appropriate escalation rate

### Resource metrics
- CPU utilization
- peak RAM
- optional GPU/VRAM utilization
- tokens/second
- time-to-decision

## 7. Results

### 7.1 Phase 1 transparent anomaly-detection baseline

The first completed experiment uses a median-absolute-deviation robust z-score detector with a fixed threshold of 3.5. The detector is intentionally simple and serves as a weak, interpretable reference rather than a proposed state-of-the-art method. The configuration was fixed before evaluation and the scores below were generated automatically.

| Scope | Precision | Recall | F1 | Event recall | Benchmark records |
|---|---:|---:|---:|---:|---:|
| SMAP | 0.2972 | 0.5819 | 0.3934 | 0.7971 | 55 |
| MSL | 0.1449 | 0.4825 | 0.2228 | 0.8889 | 27 |
| Total | 0.2685 | 0.5700 | 0.3651 | 0.8286 | 82 |

Across 105 labeled anomaly events, the baseline hit 87 events. At the point level it produced 36,938 true positives, 100,614 false positives, and 27,871 false negatives over 517,764 evaluated test points. The low precision and relatively high event recall show the expected trade-off of a naive static detector: it often intersects anomalous intervals, but it generates too many false alarms to serve as an operational detector.

Machine-readable aggregate and per-record results are stored in `results/phase1/` and are linked to GitHub Actions run `34337918870`.

### 7.2 Phase 2 adaptive temporal detector

Phase 2 tested whether more conservative scale estimation plus a simple temporal persistence rule could suppress the high false-alarm burden observed in Phase 1 without losing too much anomaly coverage. The detector used only training telemetry to estimate its center and scale, then required three consecutive pointwise flags for a run to remain anomalous.

| Scope | Precision | Recall | F1 | Event recall | Benchmark records |
|---|---:|---:|---:|---:|---:|
| SMAP | 0.3686 | 0.4070 | 0.3869 | 0.4638 | 55 |
| MSL | 0.1604 | 0.3390 | 0.2177 | 0.7222 | 27 |
| Total | 0.3256 | 0.3989 | 0.3585 | 0.5524 | 82 |

Across the same 105 labeled events and 517,764 test points, Phase 2 hit 58 events and produced 25,851 true positives, 53,550 false positives, and 38,958 false negatives. Relative to Phase 1, precision increased by 0.0570 while false positives fell by 47,064 and the number of predicted anomaly points fell by 58,151. However, recall decreased by 0.1711, event recall decreased by 0.2762, and overall F1 decreased by 0.0066.

The result is therefore mixed rather than a successful replacement for the Phase 1 detector. The temporal rule made the system substantially more selective, but it removed too many true anomaly points and events. This negative result is retained because it identifies a concrete design constraint for later temporal methods: reducing false alarms is not sufficient if event coverage collapses.

Scale estimation also exposed a useful dataset characteristic. Across the 82 benchmark records, 54 used the robust MAD/IQR scale, 12 required a standard-deviation fallback, and 16 reached the epsilon floor because their training scale estimates collapsed. Future detector designs should explicitly account for these near-constant training channels rather than relying on a single global scoring rule.

Machine-readable aggregate and per-record Phase 2 results are stored in `results/phase2/` and are linked to GitHub Actions run `34340023894`.

### 7.3 Current interpretation

The completed telemetry experiments establish two auditable reference behaviors rather than a final detector. Phase 1 favors anomaly coverage at the cost of many false alarms. Phase 2 reduces false alarms and raises precision, but sacrifices too much recall. Neither experiment supports a claim that the complete KARZOUN-X architecture is effective, because the LLM, RAG, safety-gate, communication-delay, and resource experiments have not yet been completed.

## 8. Ablation Study

Planned ablations:

- no RAG
- no safety gate
- no anomaly detector
- smaller/larger local models
- reduced knowledge corpus
- different communication conditions

## 9. Safety Analysis

Analyze failure modes including hallucinated diagnoses, unsupported evidence, unsafe proposed actions, over-rejection by the gate, stale retrieval, and timing failures.

## 10. Limitations

The first two detectors remain intentionally simple and do not constitute state-of-the-art temporal modeling. Phase 2 demonstrates that a persistence rule can suppress false alarms while also suppressing genuine events. Additional limitations include historical/anonymized telemetry, incomplete operational context, the duplicated upstream benchmark label record, simulator-to-flight gap, model dependence, and the difference between diagnostic decision support and certified autonomous control.

Because the full SMAP/MSL test results have now been inspected for Phase 1 and Phase 2, subsequent parameter development on this same full test set must be treated as exploratory unless a clean development/holdout protocol or an independent benchmark is introduced.

## 11. Future Work

The next detector study should use a clean development/holdout protocol and investigate temporal methods that reduce isolated false alarms while preserving event coverage. Potential directions include rolling or change-point statistics, hysteresis, event merging, temporal models, model-based system knowledge, multi-agent fault isolation, formalized action policies, and hardware-in-the-loop testing. Later experiments will add retrieval-grounded local language-model reasoning, deterministic action gating, communication-delay simulation, and resource measurements.

## 12. Conclusion

To be written after the full experiment program is complete.

## Data and Code Availability

Code: https://github.com/mkarson1997/karzoun-x

Dataset provenance and acquisition instructions are documented in `data/README.md`. Phase 1 and Phase 2 result provenance is recorded in `experiments/RESULTS_INDEX.md`.

## Ethics and Disclaimer

KARZOUN-X is research software and is not flight-qualified or authorized for real spacecraft control.
