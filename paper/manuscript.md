# KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture for Autonomous Spacecraft Fault Diagnosis Under Communication Delay

**Mahmoud Karzoun**  
ORCID: 0009-0006-2752-7744

> Status: working manuscript. Phase 1, Phase 2, and Phase 3 telemetry experiments have been executed; full KARZOUN-X reasoning, safety, communication-delay, and resource experiments remain in progress.

## Abstract

Deep-space spacecraft increasingly require onboard autonomy because communication latency, bandwidth constraints, and intermittent connectivity can limit immediate ground intervention. This work proposes KARZOUN-X, a research architecture that combines telemetry anomaly detection, local retrieval-augmented generation, a resource-constrained local language model, and a deterministic safety gate for spacecraft fault diagnosis and decision support. The system is designed to separate probabilistic diagnostic reasoning from action authorization and to preserve evidence for auditability. We define an evaluation protocol using historical spacecraft telemetry and simulated communication constraints. Three machine-generated detector experiments on the public SMAP/MSL benchmark establish transparent anomaly-detection reference points. Phase 2 substantially reduced false positives but lost too much anomaly coverage. Phase 3 retained a training-only robust scoring rule with a stability fallback and achieved the best total F1 of the first three experiments while reducing false positives relative to Phase 1. Because Phase 3 was designed after prior benchmark results had been inspected, it is reported as exploratory rather than as an untouched confirmatory result. Full-system conclusions are deferred until the retrieval, language-model, safety-gate, communication-delay, and resource experiments are complete.

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

The initial benchmark uses the public SMAP/MSL telemetry anomaly dataset distributed from the Telemanom/NASA JPL anomaly-detection work. All three completed telemetry experiments preserve the upstream benchmark records and fit detector statistics only on the training telemetry for each record. The first telemetry column is evaluated against the published anomaly intervals in the test split.

For the completed runs, the downloaded dataset archive had SHA-256 `6084d3ee3906381f2c98aa3773b6b2d77c82413503faa78f962196582e873733`, and the extracted label file had SHA-256 `057ce2d6c8875982bf4e5404aefea14efdcbce413d80826d2b737c95b59b7539`. The upstream label metadata includes a repeated `P-2` benchmark record; the experiments preserve the source rows rather than silently rewriting them. Consequently, this manuscript uses the term *benchmark record* when reporting row counts.

The frozen Phase 1 configuration is `experiments/configs/phase1_robust_zscore.json`, whose executed content had SHA-256 `af06f715a46a90e1efc5c0c037e805bdd28cbe36ac1f4e20565aab8bb197448a`.

The frozen Phase 2 configuration is `experiments/configs/phase2_adaptive_temporal.json`, whose executed content had SHA-256 `fe761b5f3170249e798a31a2bf9dcef1f4331570937cb607feb4d52088f173b8`. Phase 2 retained a threshold of 3.5, used the training median as the center, selected the larger of MAD-derived and IQR-derived robust scale estimates, fell back to training standard deviation if both robust estimates collapsed, and required at least three consecutive flagged samples for an anomaly run to survive temporal filtering. These parameters were frozen before the Phase 2 test-label evaluation.

The frozen Phase 3 configuration is `experiments/configs/phase3_stability_aware.json`, whose executed content had SHA-256 `934b79837c0e30ab3328590f5c1e0af488d5ccaf56f075557548f9c055685fb1`. Phase 3 retained the Phase 1-compatible MAD scoring rule when training MAD was informative, used training standard deviation only when training MAD collapsed, preserved an epsilon floor for constant training channels, and applied no temporal persistence filter. Phase 3 parameters were frozen before its evaluation run, but its design was informed by the already-inspected Phase 1 and Phase 2 benchmark outcomes. It is therefore classified as exploratory iterative refinement rather than an independent confirmatory experiment.

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

### 7.3 Phase 3 stability-aware detector

Phase 3 tested a narrower stability intervention. Instead of replacing the Phase 1 scale rule globally or applying a persistence filter, it preserved the Phase 1-compatible MAD rule when the training MAD was informative and switched to training standard deviation only when MAD collapsed. Constant training channels retained an epsilon floor. The experiment used the same threshold of 3.5 and no temporal filter.

| Scope | Precision | Recall | F1 | Event recall | Benchmark records |
|---|---:|---:|---:|---:|---:|
| SMAP | 0.3667 | 0.5581 | 0.4426 | 0.6667 | 55 |
| MSL | 0.1474 | 0.3793 | 0.2123 | 0.8611 | 27 |
| Total | 0.3257 | 0.5366 | 0.4054 | 0.7333 | 82 |

Across 517,764 test points, Phase 3 produced 34,779 true positives, 72,008 false positives, and 30,030 false negatives. It hit 77 of the 105 labeled anomaly events. Relative to Phase 1, precision increased by 0.0571, overall F1 increased by 0.0403, and false positives fell by 28,606, while recall decreased by 0.0333 and event recall decreased by 0.0952. Relative to Phase 2, precision was effectively unchanged (+0.0001), while recall increased by 0.1378, F1 increased by 0.0468, and event recall increased by 0.1810.

Phase 3 therefore provides the strongest pointwise F1 of the first three detector experiments and a better balance between selectivity and coverage than the Phase 2 persistence approach. Its scale metadata shows 49 benchmark records using MAD, 17 using the standard-deviation fallback, and 16 using the epsilon floor.

This result must not be interpreted as an independent confirmatory improvement. The Phase 3 design was developed after Phase 1 and Phase 2 test outcomes had been observed, so the same SMAP/MSL test benchmark is no longer an untouched evaluation set for design iteration. The result is retained as an auditable exploratory finding that motivates an independent diagnostic testbed and later external validation.

Machine-readable aggregate and per-record Phase 3 results are stored in `results/phase3/` and are linked to GitHub Actions run `34347057969`.

### 7.4 Current interpretation

The first three telemetry experiments now establish three auditable detector behaviors. Phase 1 favors anomaly coverage at the cost of many false alarms. Phase 2 is substantially more selective but sacrifices too much recall. Phase 3 provides the best total F1 so far and reduces false positives relative to Phase 1 while preserving substantially more coverage than Phase 2, but it is exploratory because prior results informed its design.

None of these experiments demonstrates that the complete KARZOUN-X architecture is effective. The central research contribution still requires controlled experiments for local retrieval, language-model diagnosis, deterministic safety authorization, communication-delay behavior, and resource constraints.

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

The first three detectors remain intentionally simple and do not constitute state-of-the-art temporal modeling. Phase 2 demonstrates that a persistence rule can suppress false alarms while also suppressing genuine events, and Phase 3 demonstrates an exploratory stability fallback rather than an independent benchmark result. Additional limitations include historical/anonymized telemetry, incomplete operational context, the duplicated upstream benchmark label record, simulator-to-flight gap, model dependence, and the difference between diagnostic decision support and certified autonomous control.

Because the full SMAP/MSL test results have now been inspected during iterative detector development, further tuning on this same benchmark must be treated as exploratory. A stronger claim will require a precommitted independent evaluation source, such as a separately generated held-out fault-injection testbed or another suitable external benchmark.

## 11. Future Work

The next study stage will move beyond repeated detector tuning and establish a controlled synthetic spacecraft fault-injection testbed with known fault causes, evidence documents, allowed and unsafe actions, deterministic seeds, and a precommitted held-out evaluation partition. This testbed will support direct comparison of ungrounded local language-model reasoning, retrieval-augmented reasoning, and the full safety-gated KARZOUN-X decision pipeline.

Later experiments will add communication-delay simulation, intermittent and unavailable ground links, resource measurements, model-size ablations, and independent validation of the telemetry detector. Potential detector directions include change-point statistics, hysteresis, event merging, learned temporal models, and model-based system knowledge, but these will not be presented as confirmatory improvements on the already-inspected SMAP/MSL test set without independent validation.

## 12. Conclusion

To be written after the full experiment program is complete.

## Data and Code Availability

Code: https://github.com/mkarson1997/karzoun-x

Dataset provenance and acquisition instructions are documented in `data/README.md`. Phase 1, Phase 2, and Phase 3 result provenance is recorded in `experiments/RESULTS_INDEX.md`.

## Ethics and Disclaimer

KARZOUN-X is research software and is not flight-qualified or authorized for real spacecraft control.
