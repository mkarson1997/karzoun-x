# KARZOUN-X Architecture

## Design objective

KARZOUN-X studies a hybrid architecture in which learned components can detect patterns and produce grounded diagnostic reasoning, but authorization of potentially consequential actions is controlled by deterministic policy.

## Components

### 1. Telemetry layer
Normalizes input streams into timestamped samples with channel identifiers and optional metadata.

### 2. Anomaly detection
Produces an anomaly score and a binary event flag. The initial baseline is intentionally simple and reproducible. Stronger models are planned for comparison.

### 3. Retrieval
Retrieves relevant fault-handling notes, subsystem constraints, and prior evidence from a local knowledge corpus. Retrieval output is passed to the reasoner and retained in the audit trace.

### 4. Local reasoner
An Ollama-compatible local language model can summarize evidence and propose a diagnosis or candidate response. The model is not treated as an authority.

### 5. Deterministic safety gate
Maps candidate actions against an allow/deny/escalate policy. High-severity actions and unknown actions are rejected or escalated by default.

### 6. Communication simulator
Injects configurable delay, jitter, packet loss, or complete loss of ground communication to evaluate autonomy assumptions.

### 7. Audit and metrics
Every experiment should preserve configuration, model identifier, retrieved evidence, proposed action, gate decision, latency, and final outcome.

## Trust boundaries

```text
Historical/simulated telemetry
        |
        v
[ statistical / learned analysis ]
        |
        v
[ probabilistic language model ]  <-- untrusted proposal generator
        |
        v
[ deterministic safety gate ]     <-- authorization boundary
        |
        v
[ research simulator only ]
```

## Safety principle

Unknown actions fail closed. A model recommendation must never silently become an authorized action simply because the language model expresses high confidence.
