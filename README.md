# KARZOUN-X

**Resource-Aware, Safety-Gated Local AI for Autonomous Spacecraft Fault Diagnosis**

[![Research status: preprint candidate](https://img.shields.io/badge/research-preprint%20candidate-blueviolet)](#research-status)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/code-Apache--2.0-green)](LICENSE)

KARZOUN-X is an open research project investigating whether a **locally deployed language model**, augmented with **retrieval-augmented generation (RAG)** and a **deterministic action-safety gate**, can support spacecraft fault diagnosis and low-risk decision support when Earth communication is delayed or unavailable.

The project is a reproducible research prototype, not flight software. It separates probabilistic reasoning from deterministic action authorization and preserves machine-generated experiment artifacts, raw model responses, hashes, environment metadata, and negative results for audit.

## Research question

> Can a locally deployed LLM augmented with retrieval and deterministic safety constraints improve spacecraft fault diagnosis and decision support during long communication delays or loss of Earth connectivity?

## Architecture

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
Allowed Low-Risk Step   Deny / Escalate
   |
   v
Audit Log + Metrics
```

The evaluated system does **not** execute commands on a real spacecraft.

## What has been evaluated

The repository now contains a completed experiment program through **Phase 10**:

| Area | Evidence |
|---|---|
| Real telemetry anomaly detection | SMAP/MSL benchmark, 82 benchmark records, 517,764 evaluated test points |
| Detector iteration | Three auditable statistical detector experiments, including a retained mixed result |
| Synthetic retrieval/safety mechanics | Held-out and expanded deterministic fault scenarios |
| Local LLM reasoning | Qwen3 14B local Ollama experiments with structured JSON output |
| RAG ablation | Paired no-RAG versus full-evidence comparison |
| Communication delay/outage | Deterministic local versus ground-dependent timing analysis |
| Resource characterization | Cold/warm latency, CPU, process-family memory, Ollama-reported model/VRAM allocation |
| Hard-stress behavior | Ambiguity, conflicting retrieval, missing evidence, OOD telemetry, adversarial evidence |
| Statistical synthesis | Wilson intervals and retrospective exact paired McNemar analysis |

Detailed provenance is in [`experiments/RESULTS_INDEX.md`](experiments/RESULTS_INDEX.md).

## Selected results

These results must be interpreted within their stated experimental scope.

### Real SMAP/MSL telemetry

The strongest of the first three detector runs was Phase 3, with total pointwise:

- precision: **0.3257**
- recall: **0.5366**
- F1: **0.4054**
- event recall: **0.7333**

Phase 3 is reported as **exploratory**, because its design followed inspection of the earlier benchmark results.

### Paired local-LLM RAG comparison

On the 36-scenario-per-condition Phase 7B synthetic benchmark:

- diagnosis accuracy: **36/36** with and without RAG
- expected-action match without RAG: **6/36 = 16.7%**
- expected-action match with full KARZOUN-X: **36/36 = 100%**
- full-system evidence match: **36/36 = 100%**

A retrospective exact McNemar synthesis produced `p = 1.8626e-09` for the paired action-selection difference. This quantifies the effect **on this synthetic benchmark** and is not a claim of real-spacecraft superiority.

### Hard-stress result

Phase 9 intentionally made the reasoning task harder. Overall fail-safe policy conformance fell to **26/60 = 43.3%**.

- out-of-distribution cases: **12/12** policy conformant
- tested adversarial-evidence cases: **12/12** policy conformant
- ambiguous dual-signature cases: **2/12** policy conformant
- conflicting-retrieval cases: **0/12** policy conformant
- missing-evidence cases: **0/12** policy conformant
- explicitly unsafe action proposals: **0/60**

This mixed result is central to the paper: deterministic action gating can constrain hazardous actions, but it does not by itself guarantee appropriate uncertainty or evidence sufficiency.

### Local resource footprint

Phase 8B measured the full local path on one Windows host:

- mean latency: **22.724 s**
- warm mean latency: **21.264 s**
- cold start: **47.532 s**
- peak model process-family RSS: **9.822 GiB**
- Ollama-reported model size: **9.456 GiB**
- Ollama-reported VRAM allocation: **6.113 GiB**

Direct `nvidia-smi` utilization and power telemetry were unavailable, so those measurements are not claimed.

## Dataset

The real-data track uses the public SMAP/MSL anomaly benchmark associated with the Telemanom work. Dataset files are not redistributed by default. Acquisition instructions, source hashes, and benchmark caveats are documented in [`data/README.md`](data/README.md).

SMAP/MSL is used for **anomaly detection only**. It does not provide the detailed root-cause and recovery-action labels required for the diagnosis experiments, so later diagnosis/action evaluations use a separate synthetic testbed with known labels.

## Quick start

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
pytest
```

Run the small synthetic demonstration:

```bash
karzoun-x demo
```

Optional local LLM integration uses an Ollama-compatible endpoint:

```powershell
$env:KARZOUN_X_OLLAMA_URL="http://127.0.0.1:11434"
$env:KARZOUN_X_OLLAMA_MODEL="qwen3:14b-q4_K_M"
karzoun-x ollama-check
```

## Repository map

```text
karzoun-x/
├── src/karzoun_x/
│   ├── telemetry/
│   ├── anomaly_detection/
│   ├── rag/
│   ├── reasoning/
│   ├── safety/
│   ├── communication/
│   ├── simulator/
│   ├── pipeline.py
│   └── cli.py
├── data/                     # acquisition/provenance instructions
├── experiments/              # frozen configurations + results index
├── results/                  # machine-generated experiment artifacts
├── paper/                    # manuscript and bibliography
├── docs/                     # architecture, protocols, analyses, incidents
├── tests/
└── .github/workflows/
```

## Research status

**Stage:** preprint candidate / research-prototype release preparation.

Completed:

- [x] research question, scope, and falsifiable experiment program
- [x] SMAP/MSL data acquisition and provenance
- [x] three telemetry detector experiments
- [x] synthetic retrieval and deterministic safety mechanics validation
- [x] valid local-LLM no-RAG versus RAG experiments
- [x] communication delay and ground-link outage analysis
- [x] expanded end-to-end local-LLM evaluation
- [x] corrected resource instrumentation replication
- [x] precommitted hard-stress experiment
- [x] confidence intervals and paired statistical synthesis
- [x] manuscript updated through the completed experiment program
- [ ] resolve remaining release security alert
- [ ] freeze the first archival software release
- [ ] render and independently proofread the preprint PDF
- [ ] archive software/preprint and mint real DOI(s)
- [ ] add the DOI-backed work to ORCID

## Scientific integrity

KARZOUN-X distinguishes between:

1. **real telemetry anomaly-detection results**;
2. **synthetic diagnosis/action experiments**;
3. **deterministic counterfactual communication analysis**;
4. **single-host resource measurements**;
5. **future work that has not been executed**.

Negative and mixed findings are retained rather than hidden. The repository does not claim flight qualification, NASA endorsement, mission deployment, or certified autonomous superiority.

See [`RESEARCH_ETHICS.md`](RESEARCH_ETHICS.md), [`paper/manuscript.md`](paper/manuscript.md), and [`experiments/RESULTS_INDEX.md`](experiments/RESULTS_INDEX.md).

## Citation

Until a DOI-backed release exists, cite the repository using [`CITATION.cff`](CITATION.cff). After archival release, the real DOI metadata will replace repository-only citation guidance.

## Author

**Mahmoud Karzoun**  
ORCID: `0009-0006-2752-7744`

## License

Code is licensed under the **Apache License 2.0**. Unless otherwise stated, manuscript text and original research figures are intended for release under **CC BY 4.0** at preprint/publication time.

## Disclaimer

KARZOUN-X is experimental research software. It is **not flight software**, is not certified for safety-critical operation, and must not be used to control real spacecraft or other safety-critical systems without independent engineering validation, verification, certification, and mission-specific authorization.
