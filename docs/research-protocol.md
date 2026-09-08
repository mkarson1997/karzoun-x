# Research Protocol v0.1

## Primary question

Can a locally deployed, resource-constrained LLM augmented with retrieval and deterministic safety constraints improve autonomous spacecraft fault diagnosis and decision support during long communication delays or loss of Earth connectivity?

## Primary comparison

- A: anomaly detector only
- B: local LLM only
- C: local LLM + RAG
- D: KARZOUN-X full stack

## Primary outcomes

1. event-level anomaly detection F1
2. diagnostic accuracy on a frozen labeled scenario set
3. unsupported/hallucinated diagnostic claim rate
4. unsafe-action proposal rate
5. unsafe-action authorization rate
6. median and p95 decision latency
7. peak process memory

## Communication conditions

At minimum:

- no added delay
- moderate delay
- long delay
- intermittent packet loss
- total ground outage

Exact delay values will be frozen before the primary experiment and recorded in experiment configuration files.

## Reproducibility requirements

Each reported result must include:

- git commit SHA
- dataset source/version and integrity hash where possible
- model name and quantization
- dependency lock or environment export
- operating system and hardware summary
- random seed(s)
- command/config used to produce the result

## Statistical reporting

Where repeated runs are meaningful, report central tendency and dispersion rather than a single favorable run. Multiple-comparison or uncertainty handling will be documented before inferential claims are made.

## Claim discipline

The manuscript must distinguish exploratory results from pre-specified primary outcomes. Any post-hoc metric discovered after inspecting results should be labeled exploratory.
