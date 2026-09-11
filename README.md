# KARZOUN-X

**Resource-Aware, Safety-Gated Local AI for Autonomous Spacecraft Fault Diagnosis**

[![Research status: DOI-backed preprint](https://img.shields.io/badge/research-DOI--backed%20preprint-blueviolet)](https://doi.org/10.5281/zenodo.22710335)
[![Preprint DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22710335.svg)](https://doi.org/10.5281/zenodo.22710335)
[![Software DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22708005.svg)](https://doi.org/10.5281/zenodo.22708005)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/code-Apache--2.0-green)](LICENSE)

KARZOUN-X is an open research project investigating whether a **locally deployed language model**, augmented with **retrieval-augmented generation (RAG)**, a deterministic **epistemic evidence-sufficiency gate**, and deterministic **action-safety constraints**, can support spacecraft fault diagnosis and low-risk decision support when Earth communication is delayed or unavailable.

The canonical public manuscript is a DOI-backed Zenodo preprint. The project remains a reproducible research prototype, not flight software. It separates real telemetry anomaly detection from synthetic diagnosis/action evaluation and preserves machine-generated experiment artifacts, raw model responses, hashes, environment metadata, and negative results for audit.

## Archival records

- **Canonical preprint v0.1.0-rc2:** https://doi.org/10.5281/zenodo.22710335
- **Preprint concept DOI (all versions):** https://doi.org/10.5281/zenodo.22708261
- **Software release v0.1.0-rc1:** https://doi.org/10.5281/zenodo.22708005
- **Software concept DOI:** https://doi.org/10.5281/zenodo.22708004
- **ORCID:** https://orcid.org/0009-0006-2752-7744

The preprint DOI and software DOI are intentionally distinct research outputs.

## Research question

> Can a locally deployed LLM augmented with retrieval and deterministic evidence/action constraints improve spacecraft fault diagnosis and decision support during long communication delays or loss of Earth connectivity?

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
Epistemic Evidence Gate
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

## Completed experiment program

KARZOUN-X now includes the original Phase 1-10 preprint program and the Phase 11-13 follow-up program.

| Area | Evidence |
|---|---|
| Real telemetry anomaly detection | SMAP/MSL benchmark, 82 benchmark records, 517,764 evaluated test points |
| Detector iteration | Three auditable statistical detector experiments, including a retained mixed result |
| Synthetic retrieval/safety mechanics | Held-out and expanded deterministic fault scenarios |
| Local LLM reasoning | Local Ollama experiments with schema-constrained Qwen3 models |
| RAG ablation | Paired no-RAG versus full-evidence comparison |
| Communication delay/outage | Deterministic local versus ground-dependent timing analysis |
| Resource characterization | Cold/warm latency, CPU, process-family memory, model size and Ollama-reported VRAM allocation |
| Hard-stress behavior | Ambiguity, conflicting retrieval, missing evidence, OOD telemetry, adversarial evidence |
| Epistemic mitigation | 108 newly held-out paired cases with frozen evidence-sufficiency thresholds |
| Model/resource ablation | Identical 36-case benchmark across Qwen3 4B, 8B and 14B local models |
| Final statistics | Wilson intervals, exact paired McNemar tests and resource/quality Pareto analysis |

Detailed provenance is maintained in [`experiments/RESULTS_INDEX.md`](experiments/RESULTS_INDEX.md) and under [`results/`](results/).

## Selected results

### Real SMAP/MSL telemetry

The strongest of the first three detector runs was Phase 3, with total pointwise:

- precision: **0.3257**
- recall: **0.5366**
- F1: **0.4054**
- event recall: **0.7333**

Phase 3 is reported as **exploratory**, because its design followed inspection of earlier benchmark results.

### Paired local-LLM RAG comparison

On the 36-scenario-per-condition Phase 7B synthetic benchmark:

- diagnosis accuracy: **36/36** with and without RAG
- expected-action match without RAG: **6/36 = 16.7%**
- expected-action match with full KARZOUN-X: **36/36 = 100%**
- full-system evidence match: **36/36 = 100%**

A retrospective exact McNemar synthesis produced `p = 1.8626e-09` for the paired action-selection difference. This quantifies the effect **on this synthetic benchmark** and is not a claim of real-spacecraft superiority.

### Phase 9 hard-stress boundary

Phase 9 intentionally made the reasoning task harder. Overall fail-safe policy conformance fell to **26/60 = 43.3%**.

- out-of-distribution cases: **12/12** policy conformant
- tested adversarial-evidence cases: **12/12** policy conformant
- ambiguous dual-signature cases: **2/12** policy conformant
- conflicting-retrieval cases: **0/12** policy conformant
- missing-evidence cases: **0/12** policy conformant
- explicitly unsafe action proposals: **0/60**

This negative result motivated a separate evidence-sufficiency mitigation instead of being hidden.

### Phase 11 held-out epistemic-gate mitigation

Phase 11 was designed after Phase 9 but frozen **before** executing new held-out seeds `7701`, `7702`, and `7703`. A single local-LLM response per case was scored both before and after the deterministic epistemic gate, avoiding a second stochastic model call.

Across **108 newly held-out synthetic cases**:

- baseline policy conformance: **57/108 = 52.78%**
- gated policy conformance: **108/108 = 100%**
- absolute improvement: **+47.22 percentage points**
- known-case preservation: **36/36 = 100%**
- required-defer capture: **72/72 = 100%**
- exact paired McNemar: **p = 8.8818e-16**
- unsafe false authorizations: **0**

The result is deliberately scoped to the frozen synthetic benchmark. The gate uses observable telemetry/evidence agreement, not ground-truth labels.

### Phase 12 three-model quality/resource ablation

All three local models were evaluated on the **same 36 synthetic scenarios** and the unchanged Phase 11 gate:

| Model | Gated policy | Known preserve | Required defer | Warm mean | Throughput | Peak process RSS | Ollama VRAM |
|---|---:|---:|---:|---:|---:|---:|---:|
| `qwen3:4b` | 35/36 = **97.22%** | 11/12 = **91.67%** | 24/24 = **100%** | **8.227 s** | **18.602 tok/s** | **4.184 GiB** | **2.960 GiB** |
| `qwen3:8b` | 36/36 = **100%** | 12/12 = **100%** | 24/24 = **100%** | **9.051 s** | **14.864 tok/s** | **6.423 GiB** | **5.187 GiB** |
| `qwen3:14b-q4_K_M` | 36/36 = **100%** | 12/12 = **100%** | 24/24 = **100%** | **26.380 s** | **4.730 tok/s** | **10.656 GiB** | **6.113 GiB** |

Phase 13 identifies **small and medium** as Pareto-efficient under the study's joint objective of maximizing gated conformance while minimizing warm latency and peak model-process-family RSS. Pairwise model differences are not statistically significant on this 36-case-per-model benchmark, so the result supports a resource/quality trade-off rather than a universal ranking.

### Final Phase 13 statistical synthesis

Phase 13 reports Wilson 95% intervals and paired exact tests. In particular:

- Phase 11 baseline conformance 95% Wilson interval: **0.4343-0.6194**
- Phase 11 gated conformance 95% Wilson interval: **0.9657-1.0000**
- 4B gated conformance: **35/36 = 0.9722 [0.8583, 0.9951]**
- 8B gated conformance: **36/36 = 1.0000 [0.9036, 1.0000]**
- 14B gated conformance: **36/36 = 1.0000 [0.9036, 1.0000]**

These statistics remain synthetic and single-host where applicable. They do not establish flight readiness or operational spacecraft safety.

## Dataset

The real-data track uses the public SMAP/MSL anomaly benchmark associated with Telemanom. Dataset files are not redistributed by default. Acquisition instructions, source hashes, and benchmark caveats are documented in [`data/README.md`](data/README.md).

SMAP/MSL is used for **anomaly detection only**. It does not provide detailed root-cause and recovery-action labels for every anomaly, so diagnosis/action claims come from a separate synthetic testbed with known labels.

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
├── data/                     # acquisition/provenance instructions
├── experiments/              # frozen configurations + results index
├── results/                  # machine-generated experiment artifacts
├── paper/                    # manuscripts, bibliography, figures, submission material
├── docs/                     # architecture, protocols, analyses, incidents
├── tests/
└── .github/workflows/
```

## Research status

**Stage:** DOI-backed public preprint + completed Phase 11-13 follow-up + journal-submission manuscript candidate.

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
- [x] archived software release candidate with real DOI
- [x] canonical public preprint v0.1.0-rc2 with DOI
- [x] Phase 11 held-out epistemic-gate experiment completed and archived
- [x] Phase 12 three-model local resource/quality ablation completed and archived
- [x] Phase 13 final statistical synthesis completed
- [x] journal-submission manuscript v1 generated from machine-readable results
- [x] cover letter, highlights, declarations and data/code statement generated
- [ ] resolve or explicitly document the remaining private Dependabot moderate alert
- [ ] promote software metadata/release to stable v1.0.0
- [ ] publish the final v1 manuscript as a new Zenodo preprint version after proofread
- [ ] add DOI-backed work to ORCID
- [ ] submit the final manuscript to a peer-reviewed venue

## Scientific integrity

KARZOUN-X distinguishes between:

1. **real telemetry anomaly-detection results**;
2. **synthetic diagnosis/action experiments**;
3. **deterministic counterfactual communication analysis**;
4. **single-host resource measurements**;
5. **retrospective statistical synthesis**;
6. **held-out mitigation experiments designed after the earlier failure analysis**.

Negative and mixed findings are retained rather than hidden. The repository does not claim flight qualification, NASA endorsement, mission deployment, or certified autonomous superiority.

See [`RESEARCH_ETHICS.md`](RESEARCH_ETHICS.md), [`paper/manuscript_v1.md`](paper/manuscript_v1.md), and [`experiments/RESULTS_INDEX.md`](experiments/RESULTS_INDEX.md).

## Citation

For the research manuscript, cite the current canonical public preprint:

> Karzoun, Mahmoud. (2026). *KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture for Autonomous Spacecraft Fault Diagnosis Under Communication Delay* (v0.1.0-rc2). Zenodo. https://doi.org/10.5281/zenodo.22710335

For the archived software release, use DOI **10.5281/zenodo.22708005**. Machine-readable citation metadata is available in [`CITATION.cff`](CITATION.cff).

## Author

**Mahmoud Karzoun**  
ORCID: `0009-0006-2752-7744`

## License

Code is licensed under the **Apache License 2.0**. Unless otherwise stated, manuscript text and original research figures are released under **CC BY 4.0**.

## Disclaimer

KARZOUN-X is experimental research software. It is **not flight software**, is not certified for safety-critical operation, and must not be used to control real spacecraft or other safety-critical systems without independent engineering validation, verification, certification, and mission-specific authorization.
