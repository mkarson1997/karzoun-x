from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREPRINT_DOI = "10.5281/zenodo.22710335"


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected marker not found in {path.relative_to(ROOT)}: {old[:80]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    required = [
        ROOT / "results/phase11/summary.json",
        ROOT / "results/phase12/summary.json",
        ROOT / "results/phase13/summary.json",
        ROOT / "paper/manuscript_v1.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Stable v1 promotion requires: " + ", ".join(missing))

    pyproject = ROOT / "pyproject.toml"
    _replace(pyproject, 'version = "0.1.0rc1"', 'version = "1.0.0"')

    citation = ROOT / "CITATION.cff"
    _replace(citation, "version: 0.1.0-rc1", "version: 1.0.0")
    _replace(citation, 'doi: "10.5281/zenodo.22708005"', 'doi: "10.5281/zenodo.22708004"')
    _replace(
        citation,
        'message: "If you use KARZOUN-X in research, cite the DOI-backed preprint and the archived software release as appropriate."',
        'message: "If you use KARZOUN-X in research, cite the DOI-backed manuscript and the archived software concept DOI as appropriate."',
    )

    zenodo_path = ROOT / ".zenodo.json"
    zenodo = json.loads(zenodo_path.read_text(encoding="utf-8"))
    zenodo["description"] = (
        "Stable open research prototype for local spacecraft fault-diagnosis decision support "
        "combining telemetry anomaly detection, retrieval-augmented local LLM reasoning, "
        "deterministic epistemic evidence checks, deterministic action gating, communication-delay "
        "analysis, hard-stress evaluation, multi-model resource ablation, and auditable statistical "
        "synthesis. The software is not flight-qualified."
    )
    related = [
        item
        for item in zenodo.get("related_identifiers", [])
        if item.get("identifier") != PREPRINT_DOI
    ]
    related.append(
        {
            "identifier": PREPRINT_DOI,
            "relation": "isSupplementTo",
            "scheme": "doi",
        }
    )
    zenodo["related_identifiers"] = related
    zenodo_path.write_text(json.dumps(zenodo, indent=2) + "\n", encoding="utf-8")

    changelog = ROOT / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    marker = "All notable project changes are documented here.\n"
    if marker not in text:
        raise RuntimeError("CHANGELOG insertion marker not found.")
    v1 = '''\n## 1.0.0 - 2026-09-11\n\n### Follow-up research\n- added a deterministic epistemic evidence-sufficiency gate motivated by Phase 9 failure analysis\n- completed a newly held-out paired Phase 11 mitigation experiment\n- completed a frozen three-model Phase 12 quality/resource ablation on identical scenarios\n- added Phase 13 Wilson intervals, paired exact McNemar analyses, and Pareto synthesis\n\n### Publication and reproducibility\n- finalized a v1 journal-submission manuscript generated from machine-readable follow-up results\n- added DOI-backed citation metadata and submission materials\n- preserved the published Phase 1–10 preprint as an immutable prior version\n- retained synthetic/single-host/flight-readiness boundaries in all new claims\n\n### Stable software\n- promoted the research software package to `1.0.0` after the Phase 11–13 follow-up chain\n- kept the stable software concept DOI separate from the manuscript DOI\n'''
    if "## 1.0.0 - 2026-09-11" not in text:
        changelog.write_text(text.replace(marker, marker + v1, 1), encoding="utf-8")

    roadmap = ROOT / "ROADMAP.md"
    roadmap.write_text(
        '''# Research Roadmap\n\nKARZOUN-X has completed the original Phase 1–10 preprint program and the held-out Phase 11–13 follow-up program. The project now has a DOI-backed public preprint, DOI-backed archived software, a stable v1.0.0 research package, and a peer-reviewed submission package.\n\n## Completed\n\n- [x] Phase 1–10 original experiment program\n- [x] DOI-backed public preprint\n- [x] DOI-backed archived software release candidate\n- [x] Phase 11 held-out epistemic-gate mitigation\n- [x] Phase 12 three-model quality/resource ablation\n- [x] Phase 13 final statistical synthesis\n- [x] v1 journal-submission manuscript generated from machine-readable results\n- [x] stable software metadata promoted to v1.0.0\n- [x] journal cover letter, highlights, declarations, and data/code statement prepared\n\n## Remaining publication/account actions\n\n- [ ] Resolve or document the private Dependabot moderate alert before or immediately after stable release if it remains open\n- [ ] Create a new Zenodo preprint version for the v1 manuscript after final human proofread\n- [ ] Add DOI-backed research outputs to ORCID\n- [ ] Submit to the selected peer-reviewed journal and respond to editorial/reviewer feedback\n\n## Scientific next steps beyond the first paper\n\nIndependent replication should move beyond the small lexical synthetic catalogue toward larger physics-based or mission-representative fault benchmarks, cross-family local models, hybrid/dense retrieval, stale or contradictory procedure versions, independent detector validation, and flight-like compute constraints.\n\nThe repository must continue to separate real telemetry anomaly-detection evidence, synthetic diagnosis/action evidence, deterministic communication counterfactuals, and single-host resource measurements.\n''',
        encoding="utf-8",
    )

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace(
        "**Stage:** DOI-backed public preprint + archived software RC; follow-up safety/resource experiments frozen before execution.",
        "**Stage:** DOI-backed public preprint + completed Phase 11–13 follow-up + stable v1.0.0 research software.",
    )
    text = text.replace(
        "- [ ] execute Phase 11 and Phase 12 locally and archive machine-generated results\n- [ ] run Phase 13 final synthesis\n- [ ] resolve or document the remaining Dependabot moderate alert before stable v1.0.0\n- [ ] produce final v1.0.0 manuscript/release after follow-up results\n- [ ] add DOI-backed work to ORCID\n- [ ] submit the final manuscript to an appropriate peer-reviewed venue",
        "- [x] execute Phase 11 and Phase 12 locally and archive machine-generated results\n- [x] run Phase 13 final synthesis\n- [x] produce the v1.0.0 manuscript and stable software metadata after follow-up results\n- [ ] resolve or document the remaining private Dependabot moderate alert if still open\n- [ ] publish the v1 manuscript as a new Zenodo preprint version after final proofread\n- [ ] add DOI-backed work to ORCID\n- [ ] submit the final manuscript to an appropriate peer-reviewed venue",
    )
    readme.write_text(text, encoding="utf-8")

    print("KARZOUN-X metadata promoted to v1.0.0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
