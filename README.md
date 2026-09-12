# KARZOUN-X

**Resource-Aware, Safety-Gated Local AI for Autonomous Spacecraft Fault Diagnosis**

[![Preprint DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22712634.svg)](https://doi.org/10.5281/zenodo.22712634)
[![Software Concept DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22708004.svg)](https://doi.org/10.5281/zenodo.22708004)
[![Release](https://img.shields.io/badge/release-v1.0.0-success)](https://github.com/mkarson1997/karzoun-x/releases/tag/v1.0.0)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![Code license](https://img.shields.io/badge/code-Apache--2.0-green)](LICENSE)

KARZOUN-X is an open research project investigating whether a **locally deployed language model**, augmented with **retrieval-augmented generation (RAG)**, a deterministic **epistemic evidence-sufficiency gate**, and deterministic **action-safety constraints**, can support spacecraft fault diagnosis and low-risk decision support when Earth communication is delayed or unavailable.

The canonical public manuscript is the published **v1.0.0 Zenodo preprint**. The repository contains the completed Phase 1–13 research program, machine-generated experiment artifacts, raw local-model responses, hashes, environment metadata, negative/mixed findings, and the stable `v1.0.0` research-software release.

> **Scope:** KARZOUN-X is research software. It is not flight-qualified, not a certified spacecraft fault-protection system, and is not authorized for real spacecraft control.

## Canonical research outputs

| Output | Identifier |
|---|---|
| **Canonical preprint v1.0.0** | [10.5281/zenodo.22712634](https://doi.org/10.5281/zenodo.22712634) |
| Preprint concept DOI, all versions | [10.5281/zenodo.22708261](https://doi.org/10.5281/zenodo.22708261) |
| Prior canonical preprint rc2 | [10.5281/zenodo.22710335](https://doi.org/10.5281/zenodo.22710335) |
| **Stable software v1.0.0** | [GitHub release](https://github.com/mkarson1997/karzoun-x/releases/tag/v1.0.0) |
| Software concept DOI, all archived versions | [10.5281/zenodo.22708004](https://doi.org/10.5281/zenodo.22708004) |
| Historical software rc1 version DOI | [10.5281/zenodo.22708005](https://doi.org/10.5281/zenodo.22708005) |
| Author ORCID | [0009-0006-2752-7744](https://orcid.org/0009-0006-2752-7744) |

The manuscript and software are intentionally distinct research outputs and therefore use distinct DOI families.

## Research question

> Can a locally deployed LLM augmented with retrieval and deterministic evidence/action constraints improve spacecraft fault diagnosis and decision support during long communication delays or loss of Earth connectivity?

## Evaluated architecture

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

KARZOUN-X includes the original Phase 1–10 program and the held-out Phase 11–13 follow-up chain.

| Area | Evidence |
|---|---|
| Real telemetry anomaly detection | SMAP/MSL benchmark, 82 records, 517,764 evaluated test points |
| Detector iteration | Three auditable detector experiments, including a retained mixed result |
| Synthetic retrieval/safety mechanics | Held-out and expanded deterministic fault scenarios |
| Local LLM reasoning | Local Ollama experiments with schema-constrained Qwen3 models |
| RAG ablation | Paired no-RAG versus full-evidence comparison |
| Communication delay/outage | Deterministic local versus ground-dependent timing analysis |
| Resource characterization | Cold/warm latency, CPU, process-family memory, model size, Ollama-reported VRAM |
| Hard-stress behavior | Ambiguity, conflicting retrieval, missing evidence, OOD telemetry, adversarial evidence |
| Epistemic mitigation | 108 newly held-out paired cases with frozen evidence-sufficiency thresholds |
| Model/resource ablation | Same 36-case benchmark across Qwen3 4B, 8B and 14B local models |
| Final statistics | Wilson intervals, exact paired McNemar tests and resource/quality Pareto analysis |

Detailed provenance is maintained in [`experiments/RESULTS_INDEX.md`](experiments/RESULTS_INDEX.md) and under [`results/`](results/).

## Selected results

### Real SMAP/MSL telemetry

The strongest of the first three detector runs was Phase 3, with total pointwise precision **0.3257**, recall **0.5366**, F1 **0.4054**, and event recall **0.7333**. Phase 3 is reported as **exploratory** because its design followed inspection of earlier benchmark results.

### Paired RAG comparison

On the Phase 7B synthetic benchmark, diagnosis accuracy was **36/36** with and without RAG. Expected-action match changed from **6/36 = 16.7%** without RAG to **36/36 = 100%** with the full evidence path. All 30 discordant action-selection pairs favored the full system; retrospective exact McNemar `p = 1.8626e-09`.

This result is specific to the frozen synthetic benchmark and does not establish real-spacecraft performance.

### Phase 9 hard-stress boundary

Phase 9 deliberately challenged earlier perfect synthetic scores. Overall fail-safe policy conformance fell to **26/60 = 43.3%**. Tested OOD and adversarial-evidence cases were 12/12 conformant each, while ambiguous dual-signature cases were 2/12 and both conflicting-retrieval and missing-evidence cases were 0/12. No explicitly unsafe action was proposed in that run.

This negative result motivated the separate Phase 11 evidence-sufficiency mitigation rather than being hidden.

### Phase 11 held-out epistemic-gate mitigation

Across **108 newly held-out synthetic cases**:

- baseline policy conformance: **57/108 = 52.78%**
- gated policy conformance: **108/108 = 100%**
- improved paired cases: **51**
- worsened paired cases: **0**
- known-case preservation: **36/36**
- required-defer capture: **72/72**
- exact paired McNemar: **p = 8.88e-16**

The gate corrected the targeted abstention failure mode on this held-out synthetic benchmark. It does not establish universal spacecraft safety.

### Phase 12 model/resource ablation

| Model | Gated policy | Warm mean latency | Peak process RSS |
|---|---:|---:|---:|
| `qwen3:4b` | 35/36 = **97.22%** | **8.227 s** | **4.184 GiB** |
| `qwen3:8b` | 36/36 = **100%** | **9.051 s** | **6.423 GiB** |
| `qwen3:14b-q4_K_M` | 36/36 = **100%** | **26.380 s** | **10.656 GiB** |

In this benchmark the 8B condition matched the 14B condition's gated conformance while using lower measured memory and substantially lower warm latency. Pairwise model differences were not statistically significant at this sample size, so this is a resource/quality trade-off rather than a universal model ranking.

## Dataset boundary

The real-data track uses the public SMAP/MSL anomaly benchmark associated with Telemanom. Dataset acquisition instructions, source hashes, and benchmark caveats are documented in [`data/README.md`](data/README.md).

SMAP/MSL is used for **anomaly detection only**. It does not provide the detailed root-cause and recovery-action labels required for the later reasoning experiments, so diagnosis/action claims use a separate synthetic testbed with known labels.

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

## Publication status

Completed:

- [x] Phase 1–10 original research program
- [x] Phase 11 held-out epistemic-gate mitigation
- [x] Phase 12 three-model quality/resource ablation
- [x] Phase 13 final statistical synthesis
- [x] final v1.0.0 preprint built and visually proofread
- [x] canonical v1.0.0 preprint published on Zenodo
- [x] stable GitHub software release `v1.0.0` published
- [x] journal manuscript and submission package generated
- [ ] confirm the Zenodo software-version DOI generated for GitHub `v1.0.0`
- [ ] confirm or document the remaining private Dependabot alert state
- [ ] add DOI-backed outputs to ORCID
- [ ] submit the manuscript to Acta Astronautica

## Scientific integrity

KARZOUN-X explicitly distinguishes between:

1. **real telemetry anomaly-detection results**;
2. **synthetic diagnosis/action experiments**;
3. **deterministic communication counterfactuals**;
4. **single-host resource measurements**;
5. **retrospective statistical synthesis**;
6. **held-out mitigation experiments designed after earlier failure analysis**.

Negative and mixed findings are retained. The repository does not claim flight qualification, NASA endorsement, mission deployment, or certified autonomous superiority.

See [`RESEARCH_ETHICS.md`](RESEARCH_ETHICS.md), [`paper/manuscript_v1.md`](paper/manuscript_v1.md), and [`experiments/RESULTS_INDEX.md`](experiments/RESULTS_INDEX.md).

## Citation

For the research manuscript, cite the canonical v1 preprint:

> Karzoun, Mahmoud. (2026). *KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture for Autonomous Spacecraft Fault Diagnosis Under Communication Delay* (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.22712634

For software, use the software concept DOI **10.5281/zenodo.22708004** when referring to the software family, or the specific version DOI once the Zenodo archive for GitHub `v1.0.0` is confirmed. Machine-readable citation metadata is in [`CITATION.cff`](CITATION.cff).

## Author

**Mahmoud Karzoun**  
ORCID: [`0009-0006-2752-7744`](https://orcid.org/0009-0006-2752-7744)

## License

Code is licensed under the **Apache License 2.0**. Unless otherwise stated, manuscript text and original research figures are released under **CC BY 4.0**.

## Disclaimer

KARZOUN-X is experimental research software. It is **not flight software**, is not certified for safety-critical operation, and must not be used to control real spacecraft or other safety-critical systems without independent engineering validation, verification, certification, and mission-specific authorization.
