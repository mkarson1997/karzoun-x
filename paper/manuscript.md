# KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture for Autonomous Spacecraft Fault Diagnosis Under Communication Delay

**Mahmoud Karzoun**  
ORCID: 0009-0006-2752-7744

> Status: working manuscript. Results sections are intentionally incomplete until reproducible experiments are run.

## Abstract

Deep-space spacecraft increasingly require onboard autonomy because communication latency, bandwidth constraints, and intermittent connectivity can limit immediate ground intervention. This work proposes KARZOUN-X, a research architecture that combines telemetry anomaly detection, local retrieval-augmented generation, a resource-constrained local language model, and a deterministic safety gate for spacecraft fault diagnosis and decision support. The system is designed to separate probabilistic diagnostic reasoning from action authorization and to preserve evidence for auditability. We define an evaluation protocol using historical spacecraft telemetry and simulated communication constraints. Empirical results will be reported only after the benchmark configuration and experiment pipeline are frozen.

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

Initial target: public SMAP/MSL telemetry anomaly benchmark distributed with Telemanom.

TODO: freeze exact channels, anomaly-event definitions, preprocessing, splits, model versions, hardware, and seeds.

## 6. Evaluation Methodology

### Detection metrics
- precision
- recall
- F1
- event-level detection score
- false alarm rate

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

**Not yet reported.** This section will be generated from frozen experiment outputs. No placeholder numbers should be interpreted as findings.

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

Expected limitations include historical/anonymized telemetry, incomplete operational context, simulator-to-flight gap, model dependence, and the difference between diagnostic decision support and certified autonomous control.

## 11. Future Work

Potential directions include richer temporal models, model-based system knowledge, multi-agent fault isolation, formalized action policies, and hardware-in-the-loop testing.

## 12. Conclusion

To be written after results are complete.

## Data and Code Availability

Code: https://github.com/mkarson1997/karzoun-x

Dataset provenance and acquisition instructions are documented in `data/README.md`.

## Ethics and Disclaimer

KARZOUN-X is research software and is not flight-qualified or authorized for real spacecraft control.
