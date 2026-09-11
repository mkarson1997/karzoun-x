# KARZOUN-X

**Resource-Aware, Safety-Gated Local AI for Autonomous Spacecraft Fault Diagnosis**

[![Research status: DOI-backed preprint](https://img.shields.io/badge/research-DOI--backed%20preprint-blueviolet)](https://doi.org/10.5281/zenodo.22710335)
[![Preprint DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22710335.svg)](https://doi.org/10.5281/zenodo.22710335)
[![Software DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22708005.svg)](https://doi.org/10.5281/zenodo.22708005)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/code-Apache--2.0-green)](LICENSE)

KARZOUN-X is an open research project investigating whether a **locally deployed language model**, augmented with **retrieval-augmented generation (RAG)** and deterministic safety constraints, can support spacecraft fault diagnosis and low-risk decision support when Earth communication is delayed or unavailable.

The canonical public manuscript is now a DOI-backed Zenodo **preprint**. The project remains a reproducible research prototype, not flight software. It separates probabilistic reasoning from deterministic action authorization and preserves machine-generated experiment artifacts, raw model responses, hashes, environment metadata, and negative results for audit.

## Archival records

- **Canonical preprint v0.1.0-rc2:** https://doi.org/10.5281/zenodo.22710335
- **Preprint concept DOI (all versions):** https://doi.org/10.5281/zenodo.22708261
- **Software release v0.1.0-rc1:** https://doi.org/10.5281/zenodo.22708005
- **Software concept DOI:** https://doi.org/10.5281/zenodo.22708004
- **ORCID:** https://orcid.org/0009-0006-2752-7744

The preprint DOI and software DOI are intentionally distinct and cross-linked as related research outputs.

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
Epistemic Evidence Gate   # Phase 11 mitigation under evaluation
   |
   v
Deterministic Action Safety Gate
   |----------------------|
   v                      v
Allowed Low-Risk Step   Defer / Deny / Escalate
   |
   v
Audit Log + Metrics
```

The evaluated system does **not** execute commands on a real spacecraft.

## What has been evaluated

The DOI-backed preprint reports the completed experiment program through **Phase 10**:

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

Two follow-up protocols are now frozen before execution:

- **Phase 11:** held-out paired evaluation of a deterministic evidence-sufficiency / epistemic gate designed after the Phase 9 failure analysis.
- **Phase 12:** three-model local resource/quality ablation (`qwen3:4b`, `qwen3:8b`, `qwen3:14b-q4_K_M`) using the same Phase 11 gate and identical held-out scenarios.

A Phase 13 workflow will synthesize confidence intervals, paired tests, and resource/quality Pareto results after both follow-up experiments are complete.

Detailed provenance is in [`experiments/RESULTS_INDEX.md`](experiments/RESULTS_INDEX.md).

## Selected published-preprint results

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

This mixed result is central to the paper: deterministic action gating can constrain hazardous actions, but it does not by itself guarantee appropriate uncertainty or evidence sufficiency. Phase 11 is explicitly designed to test a mitigation for this failure mode on newly held-out seeds.

### Local resource footprint

Phase 8B measured the full local path on one Windows host:

- mean latency: **22.724 s**
- warm mean latency: **21.264 s**
- cold start: **47.532 s**
- peak model process-family RSS: **9.822 GiB**
- Ollama-reported model size: **9.456 GiB**
- Ollama-reported VRAM allocation: **6.113 GiB**

Direct `nvidia-smi` utilization and power telemetry were unavailable, so those measurements are not claimed. Phase 12 extends the resource study across three frozen local model sizes on the same host and scenarios.

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

**Stage:** DOI-backed public preprint + archived software RC; follow-up safety/resource experiments frozen before execution.

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
- [x] manuscript updated through Phase 10
- [x] archived software release candidate with real DOI
- [x] canonical public preprint v0.1.0-rc2 with DOI
- [x] Phase 11 protocol frozen before held-out execution
- [x] Phase 12 multi-model resource-ablation protocol frozen before execution
- [ ] execute Phase 11 and Phase 12 locally and archive machine-generated results
- [ ] run Phase 13 final synthesis
- [ ] resolve or document the remaining Dependabot moderate alert before stable v1.0.0
- [ ] produce final v1.0.0 manuscript/release after follow-up results
- [ ] add DOI-backed work to ORCID
- [ ] submit the final manuscript to an appropriate peer-reviewed venue

## Scientific integrity

KARZOUN-X distinguishes between:

1. **real telemetry anomaly-detection results**;
2. **synthetic diagnosis/action experiments**;
3. **deterministic counterfactual communication analysis**;
4. **single-host resource measurements**;
5. **retrospective analyses**;
6. **newly frozen follow-up experiments that have not yet been executed**.

Negative and mixed findings are retained rather than hidden. The repository does not claim flight qualification, NASA endorsement, mission deployment, or certified autonomous superiority.

See [`RESEARCH_ETHICS.md`](RESEARCH_ETHICS.md), [`paper/manuscript.md`](paper/manuscript.md), and [`experiments/RESULTS_INDEX.md`](experiments/RESULTS_INDEX.md).

## Citation

For the research manuscript, cite:

> Karzoun, Mahmoud. (2026). *KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture for Autonomous Spacecraft Fault Diagnosis Under Communication Delay* (v0.1.0-rc2). Zenodo. https://doi.org/10.5281/zenodo.22710335

For the archived software release, use DOI **10.5281/zenodo.22708005**. Machine-readable citation metadata is available in [`CITATION.cff`](CITATION.cff).

## Author

**Mahmoud Karzoun**  
ORCID: `0009-0006-2752-7744`

## License

Code is licensed under the **Apache License 2.0**. Unless otherwise stated, manuscript text and original research figures are released under **CC BY 4.0**.

## Disclaimer

KARZOUN-X is experimental research software. It is **not flight software**, is not certified for safety-critical operation, and must not be used to control real spacecraft or other safety-critical systems without independent engineering validation, verification, certification, and mission-specific authorization.
