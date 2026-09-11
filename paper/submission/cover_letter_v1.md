# Cover letter — Acta Astronautica

Dear Editors of *Acta Astronautica*,

Please consider the manuscript **“KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture for Autonomous Spacecraft Fault Diagnosis Under Communication Delay”** for publication as a research article.

KARZOUN-X studies a local-first spacecraft fault-diagnosis and low-risk decision-support architecture that combines telemetry anomaly detection, retrieval-augmented local language-model reasoning, deterministic evidence sufficiency, deterministic action gating, communication-delay analysis, and auditable resource measurement. The work is intentionally framed as a research prototype rather than flight software.

The manuscript makes three points that we believe are relevant to spacecraft autonomy and fault-management research. First, on paired synthetic cases, retrieved procedure evidence materially changed the model's expected next-action selection while fault classification was already saturated. Second, a precommitted hard-stress benchmark exposed a specific safety boundary: deterministic action-hazard gating did not guarantee appropriate abstention when evidence was ambiguous, conflicting, or absent. Third, a newly held-out Phase 11 mitigation study evaluated a deterministic evidence-sufficiency gate on 108 new cases; paired policy conformance changed from **0.5278** to **1.0000** (absolute delta **+0.4722**, exact McNemar **p=8.88e-16**). A three-model Phase 12 ablation then quantified the quality/resource trade-off on identical scenarios; the best observed gated conformance was **1.0000** for `qwen3:8b`. These follow-up experiments remain synthetic and single-host where applicable, and the manuscript states those limitations explicitly.

The real-data track is kept methodologically separate: public SMAP/MSL telemetry is used for anomaly-detection evaluation only, because that benchmark does not provide detailed recovery-action labels for each anomaly. Diagnosis, retrieval, and action-policy claims come from separately labeled synthetic experiments. Negative and mixed results, raw model responses, frozen configurations, hashes, and environment metadata are preserved in the public repository.

A prior version is publicly available as a Zenodo preprint (DOI **10.5281/zenodo.22710335**). The associated research software is archived separately (DOI **10.5281/zenodo.22708005**). The preprint is disclosed here for transparency and is not under consideration by another peer-reviewed journal.

The manuscript has one author, Mahmoud Karzoun (ORCID 0009-0006-2752-7744). The author declares no competing interests and no specific external research funding. The study involves no human or animal subjects.

Thank you for considering the manuscript.

Sincerely,

Mahmoud Karzoun  
ORCID: 0009-0006-2752-7744
