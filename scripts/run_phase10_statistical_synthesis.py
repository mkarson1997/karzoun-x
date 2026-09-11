from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE7B_CSV = REPO_ROOT / "results/phase7b/per_response.csv"
PHASE8_SUMMARY = REPO_ROOT / "results/phase8/summary.json"
PHASE8B_SUMMARY = REPO_ROOT / "results/phase8b/summary.json"
PHASE9_CSV = REPO_ROOT / "results/phase9/per_response.csv"
PHASE9_SUMMARY = REPO_ROOT / "results/phase9/summary.json"
OUTPUT_DIR = REPO_ROOT / "results/phase10"
Z_95 = 1.959963984540054


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def _wilson(successes: int, total: int) -> dict[str, float | int]:
    if total <= 0:
        raise ValueError("Wilson interval requires a positive total.")
    p = successes / total
    z2 = Z_95 * Z_95
    denominator = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denominator
    half = (
        Z_95
        * math.sqrt(p * (1.0 - p) / total + z2 / (4.0 * total * total))
        / denominator
    )
    return {
        "successes": successes,
        "total": total,
        "rate": p,
        "wilson_95_low": max(0.0, center - half),
        "wilson_95_high": min(1.0, center + half),
    }


def _exact_mcnemar(discordant_a: int, discordant_b: int) -> dict[str, float | int]:
    n = discordant_a + discordant_b
    if n == 0:
        return {
            "discordant_a": discordant_a,
            "discordant_b": discordant_b,
            "discordant_total": 0,
            "two_sided_exact_p": 1.0,
        }
    tail = min(discordant_a, discordant_b)
    cumulative = sum(math.comb(n, k) for k in range(tail + 1)) / (2**n)
    return {
        "discordant_a": discordant_a,
        "discordant_b": discordant_b,
        "discordant_total": n,
        "two_sided_exact_p": min(1.0, 2.0 * cumulative),
    }


def _phase7b_ablation(rows: list[dict[str, str]]) -> dict[str, Any]:
    paired: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        paired[row["scenario_id"]][row["condition"]] = row

    complete_pairs = {
        scenario_id: pair
        for scenario_id, pair in paired.items()
        if {"llm_no_rag", "karzoun_x_full"}.issubset(pair)
    }
    if not complete_pairs:
        raise ValueError("No complete Phase 7B condition pairs were found.")

    no_rag_correct = 0
    full_correct = 0
    no_rag_only = 0
    full_only = 0
    for pair in complete_pairs.values():
        no_rag = _bool(pair["llm_no_rag"]["expected_action_match"])
        full = _bool(pair["karzoun_x_full"]["expected_action_match"])
        no_rag_correct += int(no_rag)
        full_correct += int(full)
        no_rag_only += int(no_rag and not full)
        full_only += int(full and not no_rag)

    total = len(complete_pairs)
    return {
        "paired_scenarios": total,
        "no_rag_expected_action": _wilson(no_rag_correct, total),
        "full_karzoun_x_expected_action": _wilson(full_correct, total),
        "absolute_rate_difference": (full_correct - no_rag_correct) / total,
        "mcnemar_exact": _exact_mcnemar(no_rag_only, full_only),
    }


def _phase9_stress(rows: list[dict[str, str]]) -> dict[str, Any]:
    total = len(rows)
    conformant = sum(_bool(row["policy_conformant"]) for row in rows)
    unsafe = sum(_bool(row["unsafe_action_proposal"]) for row in rows)
    defer_rows = [row for row in rows if row["expected_fault_id"] == "unknown"]
    defer_ok = sum(_bool(row["policy_conformant"]) for row in defer_rows)

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["stress_type"]].append(row)

    by_stress = {}
    for name, items in sorted(grouped.items()):
        successes = sum(_bool(row["policy_conformant"]) for row in items)
        by_stress[name] = _wilson(successes, len(items))

    return {
        "policy_conformance": _wilson(conformant, total),
        "safe_defer": _wilson(defer_ok, len(defer_rows)),
        "unsafe_action_proposals": _wilson(unsafe, total),
        "by_stress_type": by_stress,
    }


def _resource_replication(
    phase8: dict[str, Any],
    phase8b: dict[str, Any],
) -> dict[str, Any]:
    v1 = phase8["model_metrics"]
    v2 = phase8b["model_metrics"]
    return {
        "phase8_mean_latency_seconds": v1["mean_latency_seconds"],
        "phase8b_mean_latency_seconds": v2["mean_latency_seconds"],
        "mean_latency_difference_seconds": (
            v2["mean_latency_seconds"] - v1["mean_latency_seconds"]
        ),
        "phase8_warm_mean_latency_seconds": v1["warm_mean_latency_seconds"],
        "phase8b_warm_mean_latency_seconds": v2["warm_mean_latency_seconds"],
        "warm_mean_latency_difference_seconds": (
            v2["warm_mean_latency_seconds"] - v1["warm_mean_latency_seconds"]
        ),
        "interpretation": (
            "Descriptive single-host replication only; Phase 8 and Phase 8B used "
            "different synthetic seeds and are not treated as paired inferential samples."
        ),
    }


def _pct(value: float) -> str:
    return f"{100.0 * value:.1f}%"


def _interval(item: dict[str, float | int]) -> str:
    return (
        f"{int(item['successes'])}/{int(item['total'])} = "
        f"{float(item['rate']):.4f} "
        f"(95% Wilson {float(item['wilson_95_low']):.4f}–"
        f"{float(item['wilson_95_high']):.4f})"
    )


def _render(summary: dict[str, Any]) -> str:
    ablation = summary["phase7b_rag_ablation"]
    stress = summary["phase9_hard_stress"]
    mcnemar = ablation["mcnemar_exact"]
    resources = summary["resource_replication"]

    lines = [
        "# KARZOUN-X Phase 10 Statistical Synthesis",
        "",
        "This is a retrospective statistical synthesis of already-frozen experiment results. It does not create new model outputs and is not a preregistered confirmatory trial.",
        "",
        "## Phase 7B retrieval ablation",
        "",
        f"- No-RAG expected-action match: {_interval(ablation['no_rag_expected_action'])}.",
        f"- Full KARZOUN-X expected-action match: {_interval(ablation['full_karzoun_x_expected_action'])}.",
        f"- Absolute paired rate difference: {_pct(ablation['absolute_rate_difference'])}.",
        f"- Exact two-sided McNemar p-value: `{float(mcnemar['two_sided_exact_p']):.3e}` with {int(mcnemar['discordant_a'])} no-RAG-only and {int(mcnemar['discordant_b'])} full-system-only correct pairs.",
        "",
        "The paired test quantifies the action-selection difference on this synthetic testbed; it does not establish external validity for real spacecraft operations.",
        "",
        "## Phase 9 hard-stress uncertainty",
        "",
        f"- Overall policy conformance: {_interval(stress['policy_conformance'])}.",
        f"- Safe defer on precommitted-unknown cases: {_interval(stress['safe_defer'])}.",
        f"- Unsafe-action proposals: {_interval(stress['unsafe_action_proposals'])}.",
        "",
        "| Stress family | Policy conformance with 95% Wilson interval |",
        "|---|---:|",
    ]
    for name, item in stress["by_stress_type"].items():
        lines.append(f"| {name} | {_interval(item)} |")
    lines.extend(
        [
            "",
            "## Resource replication",
            "",
            f"- Phase 8 mean latency: `{resources['phase8_mean_latency_seconds']:.3f} s`; Phase 8B: `{resources['phase8b_mean_latency_seconds']:.3f} s`.",
            f"- Phase 8 warm mean: `{resources['phase8_warm_mean_latency_seconds']:.3f} s`; Phase 8B: `{resources['phase8b_warm_mean_latency_seconds']:.3f} s`.",
            f"- {resources['interpretation']}",
            "",
            "## Interpretation",
            "",
            "The combined evidence supports two simultaneous conclusions. First, retrieved evidence strongly changed action selection on the clean/separable Phase 7B benchmark. Second, Phase 9 shows that the same local model is not reliably calibrated to abstain when evidence is ambiguous, conflicting, or missing. Deterministic action gating prevented explicitly hazardous proposals in the observed stress run, but it cannot by itself guarantee epistemic correctness for low-risk diagnostic actions.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    phase7b_rows = _read_csv(PHASE7B_CSV)
    phase9_rows = _read_csv(PHASE9_CSV)
    phase8 = _read_json(PHASE8_SUMMARY)
    phase8b = _read_json(PHASE8B_SUMMARY)
    phase9_summary = _read_json(PHASE9_SUMMARY)

    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "experiment_id": "phase10-statistical-synthesis-v1",
        "study_role": "retrospective statistical synthesis of completed KARZOUN-X experiments",
        "phase7b_rag_ablation": _phase7b_ablation(phase7b_rows),
        "phase9_hard_stress": _phase9_stress(phase9_rows),
        "phase9_source_config_sha256": phase9_summary["config_sha256"],
        "resource_replication": _resource_replication(phase8, phase8b),
        "integrity": {
            "no_new_model_calls": True,
            "source_results_unchanged": True,
            "retrospective_not_preregistered": True,
            "wilson_confidence_level": 0.95,
            "mcnemar_test": "exact two-sided binomial",
            "synthetic_results_not_flight_readiness": True,
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "summary.md").write_text(_render(summary), encoding="utf-8")
    print("KARZOUN_X_PHASE10_RESULT=" + json.dumps(summary, separators=(",", ":")))
    print((OUTPUT_DIR / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
