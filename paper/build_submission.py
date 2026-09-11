from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
BUILD = PAPER / ".build"
TITLE = (
    "KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture "
    "for Autonomous Spacecraft Fault Diagnosis Under Communication Delay"
)


def _run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def _render_figures() -> None:
    if shutil.which("rsvg-convert") is None:
        raise RuntimeError("rsvg-convert is required to render publication figures.")
    for svg in sorted((PAPER / "figures").glob("*.svg")):
        png = svg.with_suffix(".png")
        _run("rsvg-convert", "-w", "1800", "-o", str(png), str(svg))


def _prepare_markdown(source_path: Path) -> Path:
    source = source_path.read_text(encoding="utf-8")
    abstract_at = source.index("## Abstract")
    body = source[abstract_at:]
    body = re.sub(r"SHA-256 (`[0-9a-f]{64}`)", r"SHA-256  \n\1", body)

    insertions = {
        (
            "`Telemetry → Anomaly Detection → Local Retrieval → Local LLM → Epistemic "
            "Evidence Gate → Deterministic Action Safety Gate → Allowed Low-Risk Action / "
            "Defer / Denial / Escalation`"
        ): (
            "`Telemetry → Anomaly Detection → Local Retrieval → Local LLM → Epistemic "
            "Evidence Gate → Deterministic Action Safety Gate → Allowed Low-Risk Action / "
            "Defer / Denial / Escalation`\n\n"
            "![KARZOUN-X final evaluated research architecture. The Phase 11 epistemic "
            "evidence gate is upstream of deterministic action authorization.]"
            "(paper/figures/architecture.png){#fig:architecture width=95%}"
        ),
        (
            "This is deterministic counterfactual timing, not a live network experiment. "
            "It isolates the propagation-delay consequence of requiring a ground round trip."
        ): (
            "![Local versus ground-dependent decision time under deterministic "
            "communication-delay references. The horizontal scale is logarithmic.]"
            "(paper/figures/communication_latency.png){#fig:communication width=92%}\n\n"
            "This is deterministic counterfactual timing, not a live network experiment. "
            "It isolates the propagation-delay consequence of requiring a ground round trip."
        ),
        (
            "In all 30 discordant action-selection pairs, the full system was correct and "
            "the no-RAG condition was not."
        ): (
            "![Paired Phase 7B expected-action match with and without retrieved evidence.]"
            "(paper/figures/phase7b_rag_ablation.png){#fig:rag-ablation width=72%}\n\n"
            "In all 30 discordant action-selection pairs, the full system was correct and "
            "the no-RAG condition was not."
        ),
        "The mean-latency difference between Phase 8 and Phase 8B was only about `+1.148 s`": (
            "![Phase 8B local model memory measurements. VRAM is Ollama-reported "
            "allocation, not an independent hardware-sensor reading.]"
            "(paper/figures/resource_footprint.png){#fig:resource width=88%}\n\n"
            "The mean-latency difference between Phase 8 and Phase 8B was only about `+1.148 s`"
        ),
        (
            "No explicitly unsafe action was proposed (`0/60`; 95% Wilson upper bound "
            "approximately `0.0602`)"
        ): (
            "![Phase 9 hard-stress policy conformance by stress family. Perfect behavior "
            "on OOD and tested adversarial evidence coexists with severe abstention failures.]"
            "(paper/figures/phase9_hard_stress.png){#fig:phase9 width=92%}\n\n"
            "No explicitly unsafe action was proposed (`0/60`; 95% Wilson upper bound "
            "approximately `0.0602`)"
        ),
    }
    for needle, replacement in insertions.items():
        if needle not in body:
            raise RuntimeError(f"Expected manuscript insertion marker not found: {needle[:80]}")
        body = body.replace(needle, replacement, 1)

    body += (
        "\n\n## Funding\n\n"
        "This research did not receive any specific grant from funding agencies in the public, "
        "commercial, or not-for-profit sectors.\n\n"
        "## Declaration of Competing Interest\n\n"
        "The author declares no known competing financial interests or personal relationships "
        "that could have appeared to influence the work reported in this paper.\n\n"
        "\\newpage\n"
    )

    front = f'''---
title: "{TITLE}"
author:
  - "Mahmoud Karzoun"
date: "11 September 2026"
subtitle: "Journal-submission manuscript · KARZOUN-X v1.0.0 candidate"
lang: en
papersize: a4
fontsize: 10pt
geometry: margin=22mm
colorlinks: true
linkcolor: blue
urlcolor: blue
citecolor: blue
---

**ORCID:** 0009-0006-2752-7744  
**Prior public preprint:** DOI [10.5281/zenodo.22708262](https://doi.org/10.5281/zenodo.22708262)  
**Research status:** prototype / journal-submission candidate; not flight-qualified or certified for autonomous control.

'''
    BUILD.mkdir(parents=True, exist_ok=True)
    target = BUILD / "journal_submission.md"
    target.write_text(front + body, encoding="utf-8")
    return target


def build(source: Path, output_dir: Path) -> None:
    _render_figures()
    markdown = _prepare_markdown(source)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf = output_dir / "KARZOUN-X-journal-submission-v1.0.0.pdf"
    docx = output_dir / "KARZOUN-X-journal-submission-v1.0.0.docx"
    common = [
        "pandoc",
        str(markdown),
        "--from=markdown",
        "--standalone",
        "--citeproc",
        f"--bibliography={PAPER / 'references.bib'}",
        "--metadata=link-citations:true",
        "--metadata=reference-section-title:References",
    ]
    _run(
        *common,
        "--pdf-engine=xelatex",
        "--variable=mainfont:DejaVu Serif",
        "--variable=sansfont:DejaVu Sans",
        "--variable=monofont:DejaVu Sans Mono",
        "--variable=monofontoptions:Scale=0.82",
        "--output",
        str(pdf),
    )
    _run(*common, "--output", str(docx))
    print(f"PDF={pdf}")
    print(f"DOCX={docx}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=PAPER / "manuscript_v1.md")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist-v1")
    args = parser.parse_args()
    build(args.source.resolve(), args.output_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
