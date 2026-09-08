# KARZOUN-X

**Resource-Aware, Safety-Gated Local AI for Autonomous Spacecraft Fault Diagnosis**

[![Research status: prototype](https://img.shields.io/badge/research-prototype-orange)](#research-status)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/code-Apache--2.0-green)](LICENSE)

KARZOUN-X is an open research project exploring whether a **locally deployed, resource-constrained language model**, augmented with **retrieval-augmented generation (RAG)** and a **deterministic safety gate**, can improve spacecraft fault diagnosis and decision support when Earth communication is delayed, intermittent, or unavailable.

The project is intentionally designed as a reproducible research system rather than a flight-ready product. It separates probabilistic AI reasoning from deterministic action authorization so that generated recommendations can be inspected, constrained, rejected, and benchmarked.

## Research question

> Can a locally deployed, resource-constrained LLM augmented with retrieval and deterministic safety constraints improve autonomous spacecraft fault diagnosis and decision support during long communication delays or loss of Earth connectivity?

## Hypothesis

A hybrid architecture combining telemetry anomaly detection, local retrieval-augmented reasoning, and deterministic safety constraints will provide more useful and explainable fault-management decisions than standalone anomaly detection or unconstrained LLM reasoning, while reducing unsafe autonomous actions.

## Why this matters

Deep-space operations cannot always depend on immediate ground intervention. NASA continues to identify autonomous fault management, onboard event-driven operations, and resilient spacecraft autonomy as important technology needs. KARZOUN-X investigates one possible software architecture for that problem using open, reproducible experiments.

## Planned architecture

```text
Telemetry
   |
   v
Anomaly Detection
   |
   v
Local Knowledge Retrieval (RAG)
   |
   v
Local LLM Reasoner
   |
   v
Deterministic Safety Gate
   |----------------------|
   v                      v
Authorized Action     Human/Ground Review
   |
   v
Audit Log + Metrics
```

A communication simulator can inject latency, packet loss, and complete communication outages around the decision loop.

## Experimental tracks

| Track | System | Purpose |
|---|---|---|
| A | Anomaly detector only | Classical baseline |
| B | Local LLM only | Measure unconstrained reasoning behavior |
| C | Local LLM + RAG | Measure grounding benefit |
| D | KARZOUN-X: detector + RAG + LLM + safety gate + comms simulation | Full proposed architecture |

## Evaluation metrics

Planned metrics include:

- anomaly precision, recall, F1 and event-level detection quality
- diagnostic accuracy
- false-alarm rate
- unsafe-action proposal rate
- safety-gate rejection rate
- hallucination / unsupported-claim rate
- decision latency
- CPU, RAM and optional GPU/VRAM usage
- performance under simulated communication delay and outage
- explanation traceability to retrieved evidence

No result will be reported until it is produced by a reproducible experiment. **This repository does not contain fabricated benchmark results.**

## Dataset direction

The first benchmark track targets the public spacecraft telemetry anomaly data released with the Telemanom work, covering telemetry from NASA's **SMAP** spacecraft and **Mars Science Laboratory (Curiosity)**. The upstream dataset contains 82 unique telemetry channels and 105 labeled anomaly sequences.

Dataset files are not redistributed here by default. See [`data/README.md`](data/README.md) and [`scripts/download_telemanom.py`](scripts/download_telemanom.py).

## Quick start

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
pytest
```

Run a small synthetic demonstration:

```bash
karzoun-x demo
```

Optional local LLM integration uses an Ollama-compatible endpoint:

```bash
# PowerShell example
$env:KARZOUN_X_OLLAMA_URL="http://127.0.0.1:11434"
$env:KARZOUN_X_OLLAMA_MODEL="qwen3:14b-q4_K_M"
karzoun-x ollama-check
```

## Repository map

```text
karzoun-x/
├── src/karzoun_x/
│   ├── telemetry/            # telemetry data structures and loaders
│   ├── anomaly_detection/    # reproducible baseline detectors
│   ├── rag/                  # local evidence retrieval
│   ├── reasoning/            # local LLM adapters
│   ├── safety/               # deterministic authorization rules
│   ├── communication/        # delay/outage simulation
│   ├── pipeline.py           # end-to-end orchestration
│   └── cli.py                # command-line interface
├── data/                     # dataset instructions only; raw data ignored
├── experiments/              # future experiment configurations/results
├── benchmarks/               # benchmark definitions
├── paper/                    # manuscript and bibliography
├── docs/                     # architecture and research protocol
├── tests/                    # unit tests
└── .github/                  # contribution and CI templates
```

## Research status

**Stage:** preprint-oriented research prototype.

Current scope:

- [x] research question and falsifiable hypothesis
- [x] reproducible repository structure
- [x] baseline telemetry anomaly detector
- [x] deterministic safety-gate prototype
- [x] communication-delay simulator
- [x] local retrieval component
- [x] Ollama-compatible local reasoning adapter
- [x] manuscript skeleton and protocol
- [ ] ingest upstream SMAP/MSL benchmark data
- [ ] freeze benchmark split and metrics
- [ ] run baselines
- [ ] run local-LLM experiments
- [ ] complete ablation study
- [ ] report results with confidence intervals where appropriate
- [ ] release preprint
- [ ] archive a versioned release with a DOI

## Scientific integrity

KARZOUN-X distinguishes clearly between:

1. **implemented capabilities**,
2. **planned experiments**, and
3. **validated empirical findings**.

The project does not claim flight qualification, NASA endorsement, mission deployment, or validated superiority before experiments are completed. See [`RESEARCH_ETHICS.md`](RESEARCH_ETHICS.md).

## Citation

Until a DOI-backed release exists, cite the repository using [`CITATION.cff`](CITATION.cff). After a versioned archival release is created, the DOI should replace the temporary repository URL in scholarly citations.

## Author

**Mahmoud Karzoun**  
ORCID: `0009-0006-2752-7744`

## License

Code is licensed under the **Apache License 2.0**. Unless otherwise stated, research text and figures authored specifically for the manuscript are intended for later release under **CC BY 4.0** at preprint/publication time.

## Disclaimer

This is experimental research software. It is **not flight software**, is not certified for safety-critical operation, and must not be used to control real spacecraft or other safety-critical systems without independent engineering validation, verification, certification, and mission-specific authorization.
