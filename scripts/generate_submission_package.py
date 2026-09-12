from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper/submission"
P11 = ROOT / "results/phase11/summary.json"
P12 = ROOT / "results/phase12/summary.json"
P13 = ROOT / "results/phase13/summary.json"
TITLE = (
    "KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture "
    "for Autonomous Spacecraft Fault Diagnosis Under Communication Delay"
)
PREPRINT_DOI = "10.5281/zenodo.22712634"
SOFTWARE_DOI = "10.5281/zenodo.22708004"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required completed result missing: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _pct(value: float) -> str:
    return f"{100.0 * float(value):.1f}%"


def _highlight(text: str) -> str:
    if len(text) > 85:
        raise ValueError(f"Highlight exceeds 85 characters ({len(text)}): {text}")
    return text


def main() -> int:
    p11 = _load(P11)
    p12 = _load(P12)
    p13 = _load(P13)
    overall = p11["overall"]
    baseline = float(overall["baseline_policy_conformant_rate"])
    gated = float(overall["gated_policy_conformant_rate"])
    delta = float(overall["absolute_policy_conformance_delta"])
    p_value = float(overall["paired"]["exact_mcnemar_p"])
    by_model = p12["by_model"]
    best_label = min(
        by_model,
        key=lambda label: (
            -float(by_model[label]["model_metrics"]["gated_policy_conformant_rate"]),
            float(by_model[label]["model_metrics"]["warm_mean_latency_seconds"] or 1e9),
        ),
    )
    best = by_model[best_label]
    best_metrics = best["model_metrics"]
    pareto = p13.get("phase12_pareto_efficient_models", [])

    OUT.mkdir(parents=True, exist_ok=True)
    highlights = [
        _highlight("Local RAG improved evidence-grounded action selection on paired synthetic cases."),
        _highlight("Hard-stress tests exposed abstention failures under conflicting or missing evidence."),
        _highlight("A held-out deterministic evidence gate tests epistemic safety beyond action gating."),
        _highlight("Three local model sizes quantify quality, latency, memory and VRAM trade-offs."),
        _highlight("All real telemetry claims are separated from synthetic diagnosis experiments."),
    ]
    (OUT / "highlights_v1.txt").write_text("\n".join(highlights) + "\n", encoding="utf-8")

    cover = f'''# Cover letter — Acta Astronautica

Dear Editors of *Acta Astronautica*,

Please consider the manuscript **“{TITLE}”** for publication as a research article.

KARZOUN-X studies a local-first spacecraft fault-diagnosis and low-risk decision-support architecture that combines telemetry anomaly detection, retrieval-augmented local language-model reasoning, deterministic evidence sufficiency, deterministic action gating, communication-delay analysis, and auditable resource measurement. The work is intentionally framed as a research prototype rather than flight software.

The manuscript makes three points that we believe are relevant to spacecraft autonomy and fault-management research. First, on paired synthetic cases, retrieved procedure evidence materially changed the model's expected next-action selection while fault classification was already saturated. Second, a precommitted hard-stress benchmark exposed a specific safety boundary: deterministic action-hazard gating did not guarantee appropriate abstention when evidence was ambiguous, conflicting, or absent. Third, a newly held-out Phase 11 mitigation study evaluated a deterministic evidence-sufficiency gate on 108 new cases; paired policy conformance changed from **{baseline:.4f}** to **{gated:.4f}** (absolute delta **{delta:+.4f}**, exact McNemar **p={p_value:.3g}**). A three-model Phase 12 ablation then quantified the quality/resource trade-off on identical scenarios; the best observed gated conformance was **{float(best_metrics['gated_policy_conformant_rate']):.4f}** for `{best['model_name']}`. These follow-up experiments remain synthetic and single-host where applicable, and the manuscript states those limitations explicitly.

The real-data track is kept methodologically separate: public SMAP/MSL telemetry is used for anomaly-detection evaluation only, because that benchmark does not provide detailed recovery-action labels for each anomaly. Diagnosis, retrieval, and action-policy claims come from separately labeled synthetic experiments. Negative and mixed results, raw model responses, frozen configurations, hashes, and environment metadata are preserved in the public repository.

The canonical v1 manuscript is publicly available as a Zenodo preprint (DOI **{PREPRINT_DOI}**). The associated research software is archived under a separate Zenodo software DOI family (concept DOI **{SOFTWARE_DOI}**). The preprint is disclosed here for transparency and is not under consideration by another peer-reviewed journal.

The manuscript has one author, Mahmoud Karzoun (ORCID 0009-0006-2752-7744). The author declares no competing interests and no specific external research funding. The study involves no human or animal subjects.

Thank you for considering the manuscript.

Sincerely,

Mahmoud Karzoun  
ORCID: 0009-0006-2752-7744
'''
    (OUT / "cover_letter_v1.md").write_text(cover, encoding="utf-8")

    metadata = {
        "title": TITLE,
        "article_type": "Research article",
        "target_journal": "Acta Astronautica",
        "author": {
            "given_name": "Mahmoud",
            "family_name": "Karzoun",
            "orcid": "0009-0006-2752-7744",
        },
        "preprint_doi": PREPRINT_DOI,
        "software_concept_doi": SOFTWARE_DOI,
        "keywords": [
            "spacecraft autonomy",
            "fault diagnosis",
            "local language model",
            "retrieval-augmented generation",
            "evidence sufficiency",
            "communication delay",
        ],
        "funding": "No specific external funding.",
        "competing_interests": "None declared.",
        "phase11": {
            "baseline_policy_conformance": baseline,
            "gated_policy_conformance": gated,
            "absolute_delta": delta,
            "paired_exact_mcnemar_p": p_value,
        },
        "phase12": {
            "best_label_by_gated_conformance_then_latency": best_label,
            "best_model_name": best["model_name"],
            "pareto_efficient_labels": pareto,
        },
    }
    (OUT / "submission_metadata_v1.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    checklist = f'''# Submission checklist

- [x] Final Phase 11, 12 and 13 machine-generated results are committed and CI is green.
- [x] `paper/manuscript_v1.md` was generated from the completed results, not hand-edited around them.
- [ ] Journal-submission PDF and DOCX pass the post-publication DOI preflight.
- [x] Title and author match ORCID and Zenodo records.
- [x] Canonical preprint DOI {PREPRINT_DOI} is disclosed.
- [x] Software concept DOI {SOFTWARE_DOI} is disclosed.
- [ ] Highlights are uploaded as a separate file if requested by the submission system.
- [ ] Cover letter is pasted or uploaded.
- [x] Funding statement: no specific external funding.
- [x] Competing-interest declaration: none declared.
- [x] Data/code availability statement is included.
- [x] No flight-readiness, NASA-endorsement, or first-LLM-in-space claim is made.
- [ ] The manuscript is not simultaneously submitted to another journal.
'''
    (OUT / "submission_checklist.md").write_text(checklist, encoding="utf-8")

    print(f"SUBMISSION_DIR={OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
