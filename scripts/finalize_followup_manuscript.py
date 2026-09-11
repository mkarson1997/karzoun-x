from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER = REPO_ROOT / "paper"
SOURCE = PAPER / "manuscript.md"
TARGET = PAPER / "manuscript_v1.md"
PHASE11 = REPO_ROOT / "results/phase11/summary.json"
PHASE12 = REPO_ROOT / "results/phase12/summary.json"
PHASE13 = REPO_ROOT / "results/phase13/summary.json"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required result is missing: {path.relative_to(REPO_ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _pct(value: float) -> str:
    return f"{100.0 * float(value):.1f}%"


def _num(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{float(value):.{digits}f}"


def _gib(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) / (1024**3):.3f}"


def _svg_phase11(path: Path, baseline: float, gated: float) -> None:
    width, height = 1328, 531
    left = 220
    chart_w = 900
    bar_h = 70
    scale = chart_w / 1.0
    baseline_w = max(1, int(scale * baseline))
    gated_w = max(1, int(scale * gated))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<text x="60" y="72" font-family="Arial" font-size="34" font-weight="700">Phase 11: held-out epistemic-gate mitigation</text>
<text x="60" y="122" font-family="Arial" font-size="24">Policy-conformant rate on the same 108 model responses</text>
<text x="60" y="235" font-family="Arial" font-size="26">Baseline</text>
<rect x="{left}" y="195" width="{chart_w}" height="{bar_h}" rx="8" fill="#e8e8e8"/>
<rect x="{left}" y="195" width="{baseline_w}" height="{bar_h}" rx="8" fill="#777777"/>
<text x="{left + chart_w + 25}" y="242" font-family="Arial" font-size="28">{baseline:.3f}</text>
<text x="60" y="365" font-family="Arial" font-size="26">Epistemic gate</text>
<rect x="{left}" y="325" width="{chart_w}" height="{bar_h}" rx="8" fill="#e8e8e8"/>
<rect x="{left}" y="325" width="{gated_w}" height="{bar_h}" rx="8" fill="#2b6f9f"/>
<text x="{left + chart_w + 25}" y="372" font-family="Arial" font-size="28">{gated:.3f}</text>
<text x="60" y="475" font-family="Arial" font-size="21">Synthetic held-out study; not flight qualification.</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def _svg_phase12(path: Path, by_model: dict[str, Any]) -> None:
    width, height = 1328, 531
    labels = list(by_model)
    max_latency = max(
        float(by_model[label]["model_metrics"]["warm_mean_latency_seconds"] or 0.0)
        for label in labels
    ) or 1.0
    max_rss = max(
        float(by_model[label]["resource_metrics"]["peak_model_process_family_rss_bytes"] or 0.0)
        for label in labels
    ) or 1.0
    x0 = 265
    w = 820
    rows: list[str] = []
    for index, label in enumerate(labels):
        y = 185 + index * 95
        metrics = by_model[label]["model_metrics"]
        resources = by_model[label]["resource_metrics"]
        policy = float(metrics["gated_policy_conformant_rate"])
        latency = float(metrics["warm_mean_latency_seconds"] or 0.0)
        rss = float(resources["peak_model_process_family_rss_bytes"] or 0.0)
        policy_w = int(w * policy)
        latency_marker = x0 + int(w * latency / max_latency)
        rss_text = rss / (1024**3)
        rows.append(
            f'<text x="55" y="{y + 28}" font-family="Arial" font-size="24" font-weight="700">{label}</text>'
            f'<rect x="{x0}" y="{y}" width="{w}" height="42" rx="6" fill="#ececec"/>'
            f'<rect x="{x0}" y="{y}" width="{policy_w}" height="42" rx="6" fill="#2b6f9f"/>'
            f'<line x1="{latency_marker}" y1="{y - 8}" x2="{latency_marker}" y2="{y + 50}" stroke="#111" stroke-width="4"/>'
            f'<text x="{x0 + w + 25}" y="{y + 28}" font-family="Arial" font-size="21">P={policy:.2f} · {latency:.1f}s · {rss_text:.2f} GiB</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<text x="55" y="62" font-family="Arial" font-size="34" font-weight="700">Phase 12: quality / resource trade-off</text>
<text x="55" y="106" font-family="Arial" font-size="21">Blue: gated policy conformance · black marker: warm latency · text: peak process-family RSS</text>
{''.join(rows)}
<text x="55" y="500" font-family="Arial" font-size="20">Same 36 synthetic cases per model on one host.</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def main() -> int:
    phase11 = _load(PHASE11)
    phase12 = _load(PHASE12)
    phase13 = _load(PHASE13)
    text = SOURCE.read_text(encoding="utf-8")

    p11 = phase11["overall"]
    baseline = float(p11["baseline_policy_conformant_rate"])
    gated = float(p11["gated_policy_conformant_rate"])
    delta = float(p11["absolute_policy_conformance_delta"])
    p_value = float(p11["paired"]["exact_mcnemar_p"])
    known_preserve = float(p11["known_case_preservation_rate"])
    defer_capture = float(p11["required_defer_capture_rate"])

    by_model = phase12["by_model"]
    best_label = min(
        by_model,
        key=lambda label: (
            -float(by_model[label]["model_metrics"]["gated_policy_conformant_rate"]),
            float(by_model[label]["model_metrics"]["warm_mean_latency_seconds"] or 1e9),
        ),
    )
    best = by_model[best_label]
    best_metrics = best["model_metrics"]
    best_resources = best["resource_metrics"]
    pareto = phase13.get("phase12_pareto_efficient_models", [])

    old_status = (
        "> Status: working manuscript with the experiment program through Phase 10 completed. "
        "The current evidence supports a research prototype and a preprint manuscript, not flight "
        "qualification or certified autonomous control."
    )
    new_status = (
        "> Status: journal-submission candidate with the Phase 1–13 research program completed. "
        "The evidence supports a research prototype, not flight qualification or certified "
        "autonomous control."
    )
    if old_status not in text:
        raise RuntimeError("Expected manuscript status marker not found.")
    text = text.replace(old_status, new_status, 1)

    old_abstract_tail = (
        "Crucially, a precommitted 60-case hard-stress experiment broke the earlier perfect synthetic "
        "scores: overall fail-safe policy conformance was only `26/60 = 0.4333`. The model handled all "
        "tested out-of-distribution and adversarial-evidence cases correctly but rarely abstained under "
        "ambiguous signatures, conflicting retrieval, or missing evidence. No explicitly unsafe action "
        "was proposed in that run, yet the failures show that action-hazard gating is not equivalent to "
        "epistemic safety. KARZOUN-X therefore supports a narrower conclusion: local RAG can materially "
        "improve action grounding on separable cases, but evidence sufficiency and uncertainty handling "
        "remain central unresolved requirements before stronger autonomy claims are justified."
    )
    abstract_tail = (
        "Crucially, a precommitted 60-case hard-stress experiment broke the earlier perfect synthetic "
        "scores: overall fail-safe policy conformance was only `26/60 = 0.4333`. This motivated a "
        "post-hoc-designed but prospectively frozen evidence-sufficiency gate, evaluated on 108 newly "
        f"held-out cases in Phase 11. On the same model responses, policy conformance changed from "
        f"`{baseline:.4f}` before the gate to `{gated:.4f}` after it (absolute delta `{delta:+.4f}`, "
        f"exact paired McNemar `p={p_value:.3g}`), with known-case preservation `{known_preserve:.4f}` "
        f"and required-defer capture `{defer_capture:.4f}`. A three-model single-host ablation then "
        f"quantified the quality/resource trade-off; the strongest observed gated conformance was "
        f"`{float(best_metrics['gated_policy_conformant_rate']):.4f}` for `{best['model_name']}`, with "
        f"warm mean latency `{_num(best_metrics['warm_mean_latency_seconds'])} s` and peak process-family "
        f"RSS `{_gib(best_resources['peak_model_process_family_rss_bytes'])} GiB`. These synthetic, "
        "single-host results narrow rather than eliminate the validation gap: evidence sufficiency can "
        "be made explicit and auditable, but stronger autonomy claims still require independent, "
        "mission-representative validation."
    )
    if old_abstract_tail not in text:
        raise RuntimeError("Expected abstract tail marker not found.")
    text = text.replace(old_abstract_tail, abstract_tail, 1)

    old_arch = (
        "`Telemetry → Anomaly Detection → Local Retrieval → Local LLM → Deterministic Safety Gate → "
        "Allowed Low-Risk Action / Denial / Escalation`"
    )
    new_arch = (
        "`Telemetry → Anomaly Detection → Local Retrieval → Local LLM → Epistemic Evidence Gate → "
        "Deterministic Action Safety Gate → Allowed Low-Risk Action / Defer / Denial / Escalation`"
    )
    if old_arch not in text:
        raise RuntimeError("Expected architecture marker not found.")
    text = text.replace(old_arch, new_arch, 1)

    contributions_marker = (
        "7. Preservation of negative and mixed findings, including a failed Phase 5 v1 response protocol, "
        "a mixed detector experiment, and weak hard-stress abstention behavior."
    )
    contributions = contributions_marker + (
        "\n8. A held-out paired mitigation study of deterministic evidence sufficiency after the Phase 9 "
        "failure analysis, with the design chronology explicitly disclosed."
        "\n9. A frozen three-model local resource/quality ablation and final statistical synthesis that "
        "quantifies model-size trade-offs on identical scenarios."
    )
    if contributions_marker not in text:
        raise RuntimeError("Expected contributions marker not found.")
    text = text.replace(contributions_marker, contributions, 1)

    methods = f'''### 5.7 Phase 11 evidence-sufficiency mitigation\n\nPhase 11 was designed **after** the Phase 9 failure analysis and is therefore not treated as part of the original precommitted Phase 9 protocol. The mitigation was frozen before evaluating three new held-out seeds (`7701`, `7702`, `7703`). It adds a deterministic epistemic gate upstream of action authorization. The gate receives telemetry and retrieved evidence but not the ground-truth fault label. It requires trusted evidence, a minimum independent lexical catalogue support of `0.24`, a minimum top-two support margin of `0.14`, and agreement between the trusted provided evidence and the independent catalogue top match. If any check fails, the gate deterministically returns `unknown`, `collect_more_telemetry`, and evidence id `none`.\n\nThe 108-case benchmark includes clean known faults and the five Phase 9 stress families. A single model response is generated per case and scored twice: once as the baseline response and once after deterministic epistemic gating. This paired design isolates the effect of the new gate without introducing a second stochastic model call.\n\n### 5.8 Phase 12 model-size and resource ablation\n\nPhase 12 freezes three local Ollama model choices before execution: `qwen3:4b`, `qwen3:8b`, and `qwen3:14b-q4_K_M`. Each model receives the same 36 held-out scenarios from seed `8801`, spanning clean known cases and the five hard-stress families. The Phase 11 epistemic-gate thresholds are reused without retuning. Resource sampling follows the corrected Phase 8B process-family method and also queries Ollama `/api/ps` for reported model size and VRAM allocation. Models are unloaded between conditions. All resource results remain single-host measurements.\n\n'''
    marker = "## 6. Metrics and Statistical Treatment"
    if marker not in text:
        raise RuntimeError("Metrics section marker not found.")
    text = text.replace(marker, methods + marker, 1)

    phase12_rows = []
    for label, item in by_model.items():
        m = item["model_metrics"]
        r = item["resource_metrics"]
        phase12_rows.append(
            f"| {label} / `{item['model_name']}` | {float(m['gated_policy_conformant_rate']):.4f} | "
            f"{float(m['known_case_preservation_rate']):.4f} | {float(m['required_defer_capture_rate']):.4f} | "
            f"{_num(m['warm_mean_latency_seconds'])} | {_num(m['mean_generation_tokens_per_second'])} | "
            f"{_gib(r['peak_model_process_family_rss_bytes'])} | {_gib(r['peak_ollama_reported_vram_size_bytes'])} |"
        )
    results = f'''### 7.11 Phase 11: held-out epistemic-gate mitigation\n\nPhase 11 evaluated the post-Phase-9 mitigation on 108 new synthetic cases. Because the same model response is scored before and after the deterministic gate, the comparison is paired.\n\n| Metric | Baseline | Epistemic-gated |\n|---|---:|---:|\n| Overall policy conformance | {baseline:.4f} | {gated:.4f} |\n| Absolute difference | n/a | {delta:+.4f} |\n| Known-case preservation | n/a | {known_preserve:.4f} |\n| Required-defer capture | n/a | {defer_capture:.4f} |\n| Exact paired McNemar p | n/a | {p_value:.12g} |\n\n![Held-out Phase 11 policy conformance before and after deterministic epistemic gating.](paper/figures/phase11_epistemic_gate.png){{#fig:phase11 width=88%}}\n\nThe gate was not conceived before Phase 9; it is a transparent post-hoc mitigation design followed by a prospectively frozen held-out evaluation. Its result therefore supports the specific new seeds and synthetic catalogue rather than proving general epistemic safety.\n\n### 7.12 Phase 12: model-size and resource ablation\n\nThe same 36 held-out scenarios and unchanged epistemic-gate thresholds were applied to three local model sizes on one host.\n\n| Model | Gated policy | Known preserve | Required defer | Warm mean (s) | tok/s | Peak RSS (GiB) | Ollama VRAM (GiB) |\n|---|---:|---:|---:|---:|---:|---:|---:|\n{chr(10).join(phase12_rows)}\n\n![Phase 12 model-size quality/resource trade-off on one host.](paper/figures/phase12_model_tradeoff.png){{#fig:phase12 width=95%}}\n\nThese measurements extend the meaning of *resource-aware* from a single 14B characterization to an explicit model-size trade-off, but they remain host-specific and do not represent flight compute, radiation tolerance, thermal limits, or spacecraft power budgets.\n\n### 7.13 Phase 13: final statistical synthesis\n\nPhase 13 made no new model calls. It computed Wilson 95% intervals for Phase 11/12 rates, exact paired McNemar comparisons, and a descriptive Pareto analysis that maximizes gated policy conformance while minimizing warm latency and peak process-family RSS. The Pareto-efficient Phase 12 model labels were: {', '.join(f'`{item}`' for item in pareto) if pareto else 'none'}. Model-to-model pairwise tests are exploratory unless corrected for multiplicity.\n\n'''
    marker = "## 8. Ablation and Component Analysis"
    if marker not in text:
        raise RuntimeError("Ablation section marker not found.")
    text = text.replace(marker, results + marker, 1)

    old_pending = (
        "Not-yet-executed ablations include model-size comparisons, learned versus lexical retrieval, "
        "and an independent detector trigger/no-trigger study on a new diagnosis benchmark. These remain "
        "future work rather than being implied by the current results."
    )
    new_pending = (
        "The model-size comparison is now executed in Phase 12 with frozen scenarios and unchanged "
        "epistemic-gate thresholds. Learned versus lexical retrieval and an independent detector "
        "trigger/no-trigger study on a new diagnosis benchmark remain future work and are not implied "
        "by the current results."
    )
    if old_pending in text:
        text = text.replace(old_pending, new_pending, 1)

    safety_marker = (
        "A stronger architecture should therefore place an evidence-sufficiency or uncertainty gate "
        "upstream of action authorization. Because that design insight comes from inspecting Phase 9, "
        "any new mechanism must be evaluated on newly frozen cases rather than retroactively treated as "
        "part of Phase 9."
    )
    safety_replacement = safety_marker + (
        f"\n\nPhase 11 implemented exactly that follow-up chronology. On newly held-out cases, the "
        f"deterministic evidence-sufficiency gate changed paired policy conformance from `{baseline:.4f}` "
        f"to `{gated:.4f}` while preserving `{known_preserve:.4f}` of known/adversarial cases and "
        f"capturing `{defer_capture:.4f}` of cases that required uncertainty and defer. This is evidence "
        "for the tested synthetic mitigation, not a proof that lexical evidence checks solve epistemic "
        "uncertainty in mission operations."
    )
    if safety_marker not in text:
        raise RuntimeError("Epistemic safety marker not found.")
    text = text.replace(safety_marker, safety_replacement, 1)

    old_limitation = (
        "Third, all valid LLM experiments use one quantized model family and one local serving stack. "
        "Cross-model generality has not been established."
    )
    new_limitation = (
        "Third, Phase 12 compares three sizes within the Qwen3 family on the same local Ollama serving "
        "stack. This improves model-size coverage but does not establish cross-family or cross-runtime "
        "generality."
    )
    if old_limitation in text:
        text = text.replace(old_limitation, new_limitation, 1)

    old_future = (
        "The highest-priority next experiment is a new, precommitted evaluation of **evidence sufficiency "
        "and epistemic abstention**. The design should be frozen on new seeds and new ambiguity/conflict "
        "patterns before execution. Candidate mechanisms include deterministic evidence-consistency "
        "checks, confidence/calibration rules, explicit contradiction detection, and a policy that "
        "escalates when retrieval quality is insufficient."
    )
    new_future = (
        "Phase 11 completed the first held-out evaluation of evidence sufficiency and epistemic "
        "abstention using a deterministic lexical agreement gate. The next priority is independent "
        "replication on a larger physics-based or mission-representative benchmark, together with "
        "calibration, contradiction detection, stale-document handling, and independent human or "
        "institutional review."
    )
    if old_future in text:
        text = text.replace(old_future, new_future, 1)

    conclusion_marker = (
        "The resulting claim is therefore deliberately narrow: **local RAG plus deterministic action "
        "gating is a promising architecture for auditable spacecraft fault-diagnosis research, but "
        "robust evidence-sufficiency and uncertainty handling remain necessary before stronger "
        "autonomous-operation claims are justified.**"
    )
    conclusion = (
        f"The held-out mitigation study adds one further result: the deterministic epistemic gate "
        f"changed policy conformance by `{delta:+.4f}` on 108 new synthetic cases, while the model-size "
        f"ablation exposed explicit quality/resource trade-offs on one host. The resulting claim remains "
        "deliberately narrow: **local RAG plus deterministic epistemic and action gating is a promising "
        "architecture for auditable spacecraft fault-diagnosis research, but independent, "
        "mission-representative validation remains necessary before stronger autonomous-operation claims "
        "are justified.**"
    )
    if conclusion_marker not in text:
        raise RuntimeError("Conclusion marker not found.")
    text = text.replace(conclusion_marker, conclusion, 1)

    figure_dir = PAPER / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    _svg_phase11(figure_dir / "phase11_epistemic_gate.svg", baseline, gated)
    _svg_phase12(figure_dir / "phase12_model_tradeoff.svg", by_model)

    TARGET.write_text(text, encoding="utf-8")
    print(f"MANUSCRIPT={TARGET}")
    print(f"PHASE11_BASELINE={baseline:.6f}")
    print(f"PHASE11_GATED={gated:.6f}")
    print(f"PHASE11_MCNEMAR_P={p_value:.12g}")
    print(f"PHASE12_BEST_LABEL={best_label}")
    print(f"PHASE12_PARETO={','.join(str(item) for item in pareto)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
