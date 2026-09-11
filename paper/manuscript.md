# KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture for Autonomous Spacecraft Fault Diagnosis Under Communication Delay

**Mahmoud Karzoun**  
ORCID: 0009-0006-2752-7744

> Status: working manuscript with the experiment program through Phase 10 completed. The current evidence supports a research prototype and a preprint manuscript, not flight qualification or certified autonomous control.

## Abstract

Deep-space operations motivate greater onboard autonomy because long propagation delays, constrained bandwidth, and intermittent or unavailable links can make immediate ground intervention impractical. KARZOUN-X is a research architecture that combines telemetry anomaly detection, local retrieval-augmented generation (RAG), a locally deployed language model, deterministic action gating, communication-delay analysis, and auditable decision traces for spacecraft fault diagnosis and low-risk decision support. The study deliberately separates probabilistic reasoning from action authorization.

Three detector experiments on the public SMAP/MSL benchmark establish a transparent telemetry reference. The strongest exploratory detector achieved total pointwise F1 `0.4054` and event recall `0.7333` across 82 benchmark records and 517,764 evaluated test points. A separate synthetic fault testbed was then used to evaluate retrieval, reasoning, safety, communication, and resource behavior without inventing root-cause labels for the real telemetry data. On an expanded paired 36-scenario local-LLM comparison, expected action selection increased from `6/36` without RAG to `36/36` with the full KARZOUN-X evidence path, while diagnosis remained `36/36` in both conditions. A retrospective exact McNemar analysis gave `p = 1.86×10^-9` for this paired synthetic action-selection difference. Deterministic communication analysis showed that a measured local decision latency near 27 s remains local during ground-link outage, whereas a ground-dependent path becomes unavailable; Mars-reference propagation adds hundreds to thousands of seconds. Enhanced single-host instrumentation measured a 9.822 GiB peak model-process-family RSS, 9.456 GiB Ollama-reported model size, and 6.113 GiB Ollama-reported VRAM allocation.

Crucially, a precommitted 60-case hard-stress experiment broke the earlier perfect synthetic scores: overall fail-safe policy conformance was only `26/60 = 0.4333`. The model handled all tested out-of-distribution and adversarial-evidence cases correctly but rarely abstained under ambiguous signatures, conflicting retrieval, or missing evidence. No explicitly unsafe action was proposed in that run, yet the failures show that action-hazard gating is not equivalent to epistemic safety. KARZOUN-X therefore supports a narrower conclusion: local RAG can materially improve action grounding on separable cases, but evidence sufficiency and uncertainty handling remain central unresolved requirements before stronger autonomy claims are justified.

## 1. Introduction

Autonomous spacecraft must detect and respond to off-nominal behavior while operating under strict safety, compute, energy, and communication constraints. Modern mission-operations research increasingly treats onboard planning, fault management, and adaptable autonomy as important capabilities for missions that cannot depend on continuous low-latency ground supervision [@castano2022operations; @jplOpsAutonomy; @nasa2026mbsefm; @nasa2026medos].

Large language models introduce a different capability: flexible interpretation of heterogeneous context and natural-language technical evidence. Recent work has already explored LLMs as spacecraft-like operators and as components of autonomous spacecraft-control research environments [@carrasco2025llmspacecraft; @jain2026autonomousreasoning]. KARZOUN-X therefore does **not** claim to be the first use of an LLM for spacecraft autonomy. Its narrower research question is whether a local model can be useful for fault diagnosis and low-risk decision support when it is grounded in retrieved evidence, constrained by deterministic action policy, and evaluated under delayed or unavailable Earth communication.

The architecture is intentionally hybrid. A probabilistic model may propose a diagnosis and next step, but it does not receive direct authority to execute arbitrary actions. A deterministic gate evaluates the proposed action after model inference. This distinction is important because a plausible explanation, a correct diagnosis, a safe recommendation, and an authorized action are different properties.

### Contributions of this study

1. An open, reproducible research architecture combining anomaly detection, local RAG, local LLM reasoning, deterministic safety gating, communication-delay analysis, and audit artifacts.
2. A transparent separation between real telemetry anomaly-detection evaluation and synthetic diagnosis/action evaluation, avoiding unsupported root-cause labels for SMAP/MSL.
3. Paired local-LLM experiments isolating the effect of retrieved evidence on diagnosis and action selection.
4. Deterministic communication-delay and outage analyses using measured local inference latency rather than invented compute latency.
5. Single-host resource characterization with process-family and Ollama model-allocation instrumentation.
6. A precommitted hard-stress benchmark that explicitly tests ambiguity, conflicting retrieval, missing evidence, out-of-distribution telemetry, and adversarial evidence.
7. Preservation of negative and mixed findings, including a failed Phase 5 v1 response protocol, a mixed detector experiment, and weak hard-stress abstention behavior.

## 2. Related Work

### 2.1 Spacecraft telemetry anomaly detection

Hundman et al. introduced a widely used spacecraft telemetry anomaly-detection benchmark based on SMAP and MSL telemetry and evaluated LSTM forecasting with nonparametric dynamic thresholding [@hundman2018detecting]. KARZOUN-X uses the public benchmark as an anomaly-detection reference, but the detector work in this paper is intentionally simple and interpretable rather than positioned as state of the art. The purpose is to provide a transparent trigger layer and to expose detector trade-offs before evaluating the reasoning architecture.

A key methodological boundary is preserved throughout this work: the SMAP/MSL benchmark supplies anomaly intervals and anonymized telemetry, not detailed root-cause diagnoses and recovery-action labels for every event. Consequently, real telemetry is used for anomaly detection, while diagnosis, retrieval grounding, and action-safety metrics are evaluated on a separate synthetic testbed with known labels.

### 2.2 Autonomous fault management and mission operations

JPL work on operations for autonomous spacecraft emphasizes planning and execution capabilities that reduce dependence on continuous Earth-based decision making [@castano2022operations; @jplOpsAutonomy]. NASA technology work likewise treats fault management, model-based system knowledge, and onboard autonomous operations as important ingredients for increasingly independent missions [@nasa2026mbsefm; @nasa2026medos].

KARZOUN-X does not replace these established fault-management paradigms. It studies a complementary diagnostic-assistance layer in which a language model can synthesize telemetry context and retrieved technical evidence while deterministic software retains authority over action admission.

### 2.3 Language models for spacecraft autonomy

Carrasco et al. evaluated LLMs as autonomous spacecraft operators in a Kerbal Space Program environment [@carrasco2025llmspacecraft]. Jain and Linares subsequently described an LLM framework for autonomous spacecraft-control reasoning with reinforcement-learning methods [@jain2026autonomousreasoning]. These studies demonstrate that LLM-based space-operations research already exists and make broad priority claims inappropriate.

KARZOUN-X focuses on a narrower systems question: **local, evidence-grounded fault diagnosis and low-risk decision support under communication delay, with deterministic action gating and explicit resource measurement**. It also places special emphasis on failure analysis when retrieval itself becomes misleading or incomplete.

### 2.4 Safety-constrained AI decision support

For this study, three concepts are kept separate:

- **recommendation**: a model-generated diagnosis or proposed next step;
- **authorization**: a deterministic policy decision on whether a proposed action may proceed;
- **control**: actual command execution on a physical system.

KARZOUN-X implements the first two only in a synthetic research environment and does not implement flight control. This separation also clarifies a central Phase 9 result: a deterministic action gate can contain explicitly hazardous actions while still allowing a low-risk action that is epistemically unjustified. Action safety and reasoning correctness therefore require separate metrics.

## 3. Research Questions

### RQ1
Does retrieved local evidence improve the quality of local-LLM diagnosis and action selection relative to the same model without RAG?

### RQ2
What safety properties are provided by deterministic action gating, and what failure modes remain outside that boundary?

### RQ3
How does delayed or unavailable ground communication change time-to-decision for local versus ground-dependent decision paths?

### RQ4
What latency and resource footprint are observed when the full local reasoning path runs on a single commodity host?

### RQ5
How robust is the local reasoning path when evidence is ambiguous, conflicting, absent, adversarially phrased, or outside the known fault catalogue?

## 4. KARZOUN-X Architecture

The evaluated architecture is:

`Telemetry → Anomaly Detection → Local Retrieval → Local LLM → Deterministic Safety Gate → Allowed Low-Risk Action / Denial / Escalation`

The anomaly detector operates as a trigger. The retriever supplies local knowledge documents. The language model produces a schema-constrained diagnosis, rationale, evidence identifier, and proposed action. The `SafetyGate` then independently evaluates the action against a small deterministic research policy. Raw model output, retrieved-document identifiers, scores, timing, and environment metadata are preserved for audit.

The architecture is local-first by design. External model APIs are not required by the evaluated inference path. Communication-delay experiments compare local decision availability with a counterfactual ground-dependent path; they do not simulate a full Deep Space Network stack.

## 5. Data and Experimental Design

### 5.1 Real SMAP/MSL telemetry

The real-data detector experiments use the public SMAP/MSL anomaly dataset associated with Telemanom [@hundman2018detecting]. Detector statistics are fit only on each benchmark record's training telemetry, and predictions are evaluated against published anomaly intervals in the test split.

The downloaded dataset archive used in the frozen runs had SHA-256 `6084d3ee3906381f2c98aa3773b6b2d77c82413503faa78f962196582e873733`; the extracted labels had SHA-256 `057ce2d6c8875982bf4e5404aefea14efdcbce413d80826d2b737c95b59b7539`. The experiments preserve an upstream repeated `P-2` metadata row rather than silently modifying source metadata, so this manuscript reports 82 *benchmark records* and 517,764 evaluated test points.

### 5.2 Synthetic fault catalogue

Diagnosis and action experiments use a deterministic research testbed with six interpretable fault families:

- battery undervoltage;
- thermal overtemperature;
- reaction-wheel saturation;
- star-tracker dropout;
- transmitter-power anomaly;
- sensor stuck value.

Each synthetic case provides controlled telemetry context and, when appropriate, an expected evidence document and low-risk diagnostic action. The catalogue does not represent a certified spacecraft model or operational procedure.

### 5.3 Local model and structured response contract

Valid local-LLM experiments use `qwen3:14b-q4_K_M` through local Ollama, temperature `0.0`, `think=false`, a fixed maximum output budget of 220 tokens, and JSON-schema constrained output. The model returns:

`fault_id`, `action`, `rationale`, and `evidence_document_id`.

Phase 5 v1 is retained as an audit incident rather than a performance result because a thinking-enabled response contract consumed the output budget without returning a usable final response. Phase 5 v2 corrected the transport contract while preserving the held-out scenarios and scoring targets.

### 5.4 Retrieval and action policy

The evaluated retriever is deterministic lexical token overlap with `top_k=3`. This simplicity makes the evidence path auditable but limits generalization. The deterministic safety policy explicitly allows a small set of low-risk diagnostic actions and denies or escalates high-severity or unknown actions.

### 5.5 Hard-stress suite

Phase 9 was frozen before execution and contains 60 deterministic cases across two seeds, six source fault families, and five stress types:

1. ambiguous dual signatures;
2. conflicting retrieval;
3. out-of-distribution telemetry;
4. adversarial evidence containing an embedded unsafe instruction;
5. missing evidence.

For ambiguous, conflicting, missing, and out-of-distribution conditions, the precommitted fail-safe response is `fault_id="unknown"`, `action="collect_more_telemetry"`, and `evidence_document_id="none"`. Retrieved evidence is explicitly framed as untrusted reference data that cannot override higher-level policy.

### 5.6 Resource instrumentation

Phase 8 measured local timing and system load. Phase 8B was designed after Phase 8 exposed incomplete Ollama process visibility on Windows. The follow-up therefore samples the model process family and queries Ollama `/api/ps` for reported model size and VRAM allocation. Direct `nvidia-smi` utilization and power telemetry were unavailable and are not inferred.

## 6. Metrics and Statistical Treatment

### 6.1 Detection

Pointwise precision, recall, F1, false positives, false negatives, and event recall are reported for SMAP/MSL. An anomaly event is counted as detected if at least one predicted anomaly point intersects the labeled interval.

### 6.2 Reasoning and retrieval

Local-LLM experiments report parse success, diagnosis accuracy, expected-action match, diagnosis-plus-action match, evidence-document match, latency, and generation throughput. End-to-end success requires all precommitted components for the evaluated condition to succeed.

### 6.3 Safety and uncertainty

Safety metrics include unsafe-action proposal rate, deterministic gate outcome, unsafe false authorization, fail-safe policy conformance, and safe-defer rate. In Phase 9, policy conformance is stricter than action safety: a safe but unjustified action can be nonconformant.

### 6.4 Retrospective statistical synthesis

Phase 10 makes no new model calls. It computes 95% Wilson score intervals for binomial rates and an exact two-sided McNemar test for the paired Phase 7B expected-action comparison. Because Phase 10 was designed after observing the completed experiments, it is explicitly labeled **retrospective and not preregistered confirmatory inference**.

## 7. Results

### 7.1 Phase 1: transparent anomaly-detection baseline

A median-absolute-deviation robust z-score detector with threshold 3.5 produced:

| Scope | Precision | Recall | F1 | Event recall | Benchmark records |
|---|---:|---:|---:|---:|---:|
| SMAP | 0.2972 | 0.5819 | 0.3934 | 0.7971 | 55 |
| MSL | 0.1449 | 0.4825 | 0.2228 | 0.8889 | 27 |
| Total | 0.2685 | 0.5700 | 0.3651 | 0.8286 | 82 |

Across 105 labeled anomaly events it hit 87. At point level, it produced 36,938 true positives, 100,614 false positives, and 27,871 false negatives. The baseline therefore favored event coverage at the cost of a large false-alarm burden.

### 7.2 Phase 2: adaptive temporal detector

Phase 2 used conservative scale selection and required three consecutive pointwise flags:

| Scope | Precision | Recall | F1 | Event recall |
|---|---:|---:|---:|---:|
| Total | 0.3256 | 0.3989 | 0.3585 | 0.5524 |

False positives dropped from 100,614 to 53,550, but recall and event recall fell substantially. The result is retained as mixed: increased selectivity did not compensate for lost anomaly coverage.

### 7.3 Phase 3: stability-aware detector

Phase 3 preserved MAD scoring when informative and used a training-standard-deviation fallback only when MAD collapsed:

| Scope | Precision | Recall | F1 | Event recall |
|---|---:|---:|---:|---:|
| Total | 0.3257 | 0.5366 | 0.4054 | 0.7333 |

It produced 34,779 true positives, 72,008 false positives, and 30,030 false negatives, hitting 77 of 105 events. This is the strongest pointwise F1 of Phases 1–3, but it is **exploratory** because its design followed inspection of the earlier benchmark results.

### 7.4 Phase 4: held-out retrieval and safety mechanics

On 12 held-out synthetic scenarios:

| Metric | Result |
|---|---:|
| Retrieval top-1 expected-document accuracy | 1.0000 |
| Retrieval top-3 recall | 1.0000 |
| Expected low-risk action allow rate | 1.0000 |
| Unsafe-action block rate | 1.0000 |
| Unsafe-action false-allow rate | 0.0000 |

No language model participated. These perfect scores validate deterministic testbed mechanics, not diagnostic intelligence or flight readiness.

### 7.5 Phase 5 v2: local LLM with and without RAG

The corrected 12-scenario-per-condition experiment used the same local Qwen3 model in both conditions:

| Metric | No RAG | RAG top-3 |
|---|---:|---:|
| Parse success | 1.0000 | 1.0000 |
| Diagnosis accuracy | 1.0000 | 1.0000 |
| Expected action match | 0.1667 | 1.0000 |
| Diagnosis + expected action | 0.1667 | 1.0000 |
| Expected evidence match | n/a | 1.0000 |
| Unsafe/unknown proposal rate | 0.0000 | 0.0000 |
| Mean latency (s) | 24.686 | 27.159 |

RAG did not change fault-class accuracy on this separable testbed; its observed effect was on evidence-grounded action selection.

### 7.6 Phase 6: communication-delay and outage analysis

Phase 6 reuses measured Phase 5 v2 local RAG latencies without rescoring model outputs. Ground-dependent latency is modeled as local compute latency plus round-trip propagation:

| Profile | OWLT | Mean local decision | Mean ground-dependent decision | Ground completion |
|---|---:|---:|---:|---:|
| Zero-delay reference | 0 s | 27.159 s | 27.159 s | 1.0000 |
| Lunar reference | 1 s | 27.159 s | 29.159 s | 1.0000 |
| Mars-near reference | 240 s | 27.159 s | 507.159 s | 1.0000 |
| Mars-far reference | 1440 s | 27.159 s | 2907.159 s | 1.0000 |
| Ground-link outage | n/a | 27.159 s | unavailable | 0.0000 |

This is deterministic counterfactual timing, not a live network experiment. It isolates the propagation-delay consequence of requiring a ground round trip.

### 7.7 Phase 7A and 7B: expanded robustness and paired end-to-end comparison

Phase 7A expanded deterministic mechanics to 180 synthetic scenarios across clean, distractor, and partial-information variants. Detector scenario trigger, retrieval top-1/top-3, safe-action allow, unsafe-action block, and integrated deterministic mechanics were all `1.0000`; the nominal false-trigger point rate was `0.001296`. These results again showed that the synthetic task remained highly separable.

Phase 7B then evaluated 36 scenarios per condition with the local model:

| Metric | No RAG | Full KARZOUN-X |
|---|---:|---:|
| Diagnosis accuracy | 1.0000 | 1.0000 |
| Expected action match | 0.1667 | 1.0000 |
| Expected evidence match | n/a | 1.0000 |
| End-to-end success | 0.1667 | 1.0000 |
| Unsafe/unknown proposal rate | 0.0000 | 0.0000 |
| Mean latency (s) | 20.943 | 23.141 |

In all 30 discordant action-selection pairs, the full system was correct and the no-RAG condition was not. Phase 10's retrospective exact McNemar test yielded `p = 1.8626×10^-9`. The no-RAG expected-action rate was `6/36 = 0.1667` (95% Wilson `0.0787–0.3189`); the full-system rate was `36/36 = 1.0000` (95% Wilson `0.9036–1.0000`). These statistics quantify a large paired effect **within this synthetic benchmark** and do not establish external validity.

### 7.8 Phase 8 and 8B: single-host resource characterization

Phase 8 produced 18/18 successful full-path cases with mean latency `21.575 s`, cold-start latency `49.308 s`, warm mean `19.944 s`, and mean generation throughput `5.860 tok/s`. It also revealed that observing only the parent Ollama process badly undercounted model memory.

Phase 8B corrected the instrumentation on a new 18-case seed:

| Metric | Phase 8B |
|---|---:|
| End-to-end success | 1.0000 |
| Mean latency | 22.724 s |
| Median latency | 22.118 s |
| Cold-start latency | 47.532 s |
| Warm mean latency | 21.264 s |
| Mean generation throughput | 5.599 tok/s |
| Peak model process-family RSS | 9.822 GiB |
| Ollama-reported model size | 9.456 GiB |
| Ollama-reported VRAM allocation | 6.113 GiB |
| Mean system CPU | 51.515% |
| Peak system CPU | 91.0% |

The mean-latency difference between Phase 8 and Phase 8B was only about `+1.148 s`, and the warm-mean difference was about `+1.320 s`. These are descriptive replications on different synthetic seeds, not paired inferential samples. Direct GPU utilization and power were unavailable because `nvidia-smi` was not accessible; the VRAM number is Ollama-reported allocation rather than an independent sensor measurement.

### 7.9 Phase 9: precommitted hard-stress evaluation

Phase 9 deliberately tests conditions that should make an overconfident reasoning system fail. All 60 calls returned schema-valid responses, but overall fail-safe policy conformance fell to `26/60 = 0.4333` (95% Wilson `0.3157–0.5590`). Among the 48 cases whose correct precommitted response was uncertainty plus safe defer, only `14/48 = 0.2917` conformed (95% Wilson `0.1824–0.4318`).

| Stress family | Policy conformant | 95% Wilson interval |
|---|---:|---:|
| Adversarial evidence | 12/12 = 1.0000 | 0.7575–1.0000 |
| Out of distribution | 12/12 = 1.0000 | 0.7575–1.0000 |
| Ambiguous dual signature | 2/12 = 0.1667 | 0.0470–0.4480 |
| Conflicting retrieval | 0/12 = 0.0000 | 0.0000–0.2425 |
| Missing evidence | 0/12 = 0.0000 | 0.0000–0.2425 |

No explicitly unsafe action was proposed (`0/60`; 95% Wilson upper bound approximately `0.0602`), and thus no unsafe action was falsely authorized. This result is encouraging for the tested action vocabulary but does **not** rescue the poor epistemic behavior. In many failed cases the model proposed an allowed low-risk action while committing to an unjustified diagnosis or failing to abstain.

The adversarial-evidence result is also narrow. The model resisted the specific tested embedded unsafe instructions in 12/12 cases; this is not evidence of resistance to arbitrary prompt injection or data poisoning.

### 7.10 Phase 10: retrospective statistical synthesis

Phase 10 made no new model calls and preserved all source results. Its purpose was to add uncertainty intervals and paired analysis without rewriting the original experiments. The most important synthesis is the tension between Phases 7B and 9:

- on clean/separable paired cases, retrieval changed expected-action selection from `16.7%` to `100%`;
- under misleading or insufficient evidence, the same model often failed to abstain;
- deterministic action gating contained the tested hazardous action vocabulary, but it could not determine whether a low-risk action was epistemically warranted.

This combination is more informative than a uniformly perfect benchmark: it identifies both a useful capability and a concrete safety boundary.

## 8. Ablation and Component Analysis

The strongest executed ablation is the paired no-RAG versus full-evidence comparison in Phase 7B. Diagnosis accuracy was saturated in both conditions, but action selection differed by 83.3 percentage points. This supports the claim that retrieved procedure evidence can materially influence the *next-step recommendation* even when the base model already recognizes the fault class.

Phase 9 acts as a retrieval-quality stress ablation. Correct retrieval is not universally beneficial simply because retrieval exists. When retrieval was intentionally conflicting, policy conformance was `0/12`; when evidence was missing it was also `0/12`. The system therefore needs a mechanism that assesses evidence sufficiency and conflict rather than treating retrieved context as automatically trustworthy.

Not-yet-executed ablations include model-size comparisons, learned versus lexical retrieval, and an independent detector trigger/no-trigger study on a new diagnosis benchmark. These remain future work rather than being implied by the current results.

## 9. Safety Analysis

### 9.1 Action-hazard containment

The deterministic gate successfully blocked deliberately high-risk actions in Phase 4. In Phase 9, the language model itself proposed no explicitly unsafe action, so the hard-stress run did not provide additional unsafe-proposal cases with which to estimate gate false-authorization performance.

The observed `0/60` unsafe proposal rate should not be reported as proof of safety. Its 95% Wilson upper bound is approximately 6.0%, and the scenario family is synthetic and small.

### 9.2 Epistemic safety

Phase 9 exposes the more important unresolved issue: the current gate reasons about *action hazard*, not *evidence adequacy*. A low-risk action can pass the gate even when the diagnosis is overconfident, retrieved evidence conflicts with telemetry, or evidence is absent. The 0% policy conformance on the tested conflicting-retrieval and missing-evidence families demonstrates this gap directly.

A stronger architecture should therefore place an evidence-sufficiency or uncertainty gate upstream of action authorization. Because that design insight comes from inspecting Phase 9, any new mechanism must be evaluated on newly frozen cases rather than retroactively treated as part of Phase 9.

## 10. Discussion

### 10.1 What RAG helped

Across Phases 5 v2 and 7B, RAG did not improve already-saturated synthetic diagnosis accuracy. Instead, its largest observed contribution was procedural grounding: the model selected the expected low-risk next action much more consistently when the relevant local manual was available. This is useful because spacecraft fault handling is not only a classification problem; identifying a plausible fault does not determine the correct next diagnostic step.

### 10.2 What RAG broke

Phase 9 demonstrates the opposite side of retrieval. A model can anchor on incorrect retrieved context, and the existence of a document does not establish its applicability. Conflicting retrieval produced the worst observed behavior, with no case following the precommitted uncertainty policy. Missing evidence also revealed overconfidence: the model commonly inferred a known fault directly from telemetry even though the study's fail-safe policy required abstention without evidence.

### 10.3 Local autonomy under communication constraints

The communication experiment does not claim that local AI makes spacecraft operations instantaneous or replaces ground teams. It shows a narrower property: local computation avoids a mandatory communication round trip. At Mars-reference delays, propagation dominates the measured local inference time; under complete outage, a ground-dependent path cannot complete at all while a local diagnostic path can remain available.

### 10.4 Resource awareness

The evaluated 14B quantized model is viable on the single commodity host used here, but it is not demonstrated on flight-like compute. A roughly 9.8 GiB process-family RSS and 6.1 GiB reported VRAM allocation are substantial for embedded systems. The phrase *resource-aware* in this work therefore means the resource cost is measured and treated as a design constraint, not that the current 14B configuration is suitable for deployment on spacecraft hardware.

## 11. Limitations and Threats to Validity

Several limitations materially constrain the conclusions.

First, SMAP/MSL supports anomaly detection but not the detailed diagnosis/action labels needed for the later reasoning experiments. Real telemetry detection and synthetic fault diagnosis are therefore separate evaluation tracks and must not be conflated.

Second, the synthetic catalogue is small. Earlier perfect scores partly reflect lexical and semantic separability rather than real operational complexity. Phase 9 was designed to challenge that weakness, but it still contains only 12 cases per stress family.

Third, all valid LLM experiments use one quantized model family and one local serving stack. Cross-model generality has not been established.

Fourth, the retrieval method is deliberately simple lexical overlap. Results may differ with dense retrieval, reranking, larger technical corpora, stale documents, or heterogeneous mission documentation.

Fifth, resource results come from one Windows desktop host. Ollama-reported VRAM allocation is not an independent GPU sensor reading, and direct GPU utilization and power were unavailable.

Sixth, communication results are deterministic propagation-delay counterfactuals. They omit packet loss, contact scheduling, bandwidth contention, ground processing queues, command validation, and full mission-network behavior.

Seventh, Phase 3 is exploratory because earlier SMAP/MSL test results informed its design. Further detector tuning on the same test benchmark would not constitute independent confirmation.

Finally, none of the experiments use flight hardware, certified flight software, or real command execution. KARZOUN-X remains decision-support research software.

## 12. Future Work

The highest-priority next experiment is a new, precommitted evaluation of **evidence sufficiency and epistemic abstention**. The design should be frozen on new seeds and new ambiguity/conflict patterns before execution. Candidate mechanisms include deterministic evidence-consistency checks, confidence/calibration rules, explicit contradiction detection, and a policy that escalates when retrieval quality is insufficient.

Additional work should include cross-model and model-size replication; dense or hybrid retrieval comparisons; a larger independent synthetic or physics-based spacecraft subsystem simulator; fault combinations and cascading faults; stale or version-conflicted procedure documents; independent detector validation; and testing on compute closer to flight constraints.

A publication-quality follow-up should also recruit an independent evaluator or dataset where possible, because the current research program was designed, executed, and interpreted within one open repository.

## 13. Conclusion

KARZOUN-X demonstrates that a local, evidence-grounded language-model path can be integrated with anomaly detection, deterministic action gating, communication-delay analysis, and auditable resource measurement. On separable synthetic cases, retrieved evidence produced a large paired improvement in expected action selection while local computation avoided mandatory ground round-trip delay. The system also operated reproducibly on a commodity host with a measurable, nontrivial resource footprint.

The hard-stress results prevent a simplistic success narrative. The same model that performed perfectly on out-of-distribution and tested adversarial-evidence cases frequently failed to abstain when signatures were ambiguous, retrieval was misleading, or evidence was missing. Deterministic action gating contained the evaluated hazardous-action vocabulary but did not solve epistemic uncertainty.

The resulting claim is therefore deliberately narrow: **local RAG plus deterministic action gating is a promising architecture for auditable spacecraft fault-diagnosis research, but robust evidence-sufficiency and uncertainty handling remain necessary before stronger autonomous-operation claims are justified.**

## Data and Code Availability

Code and machine-generated experiment artifacts are maintained in the public KARZOUN-X repository. Dataset provenance and acquisition instructions are documented in `data/README.md`, and experiment hashes, source commits, workflow runs, incidents, and result locations are recorded in `experiments/RESULTS_INDEX.md`.

## Ethics and Disclaimer

KARZOUN-X is research software. It is not flight-qualified, not a certified fault-protection system, and not authorized for real spacecraft control. Synthetic scenarios and procedures are research constructs and must not be treated as operational flight rules.
