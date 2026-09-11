from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE11_DIR = REPO_ROOT / "results/phase11"
PHASE12_DIR = REPO_ROOT / "results/phase12"
OUTPUT_DIR = REPO_ROOT / "results/phase13"
Z95 = 1.959963984540054


def _bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def _wilson(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    p = successes / total
    denominator = 1.0 + (Z95**2) / total
    center = (p + (Z95**2) / (2.0 * total)) / denominator
    half = (
        Z95
        * math.sqrt((p * (1.0 - p) / total) + (Z95**2) / (4.0 * total**2))
        / denominator
    )
    return (max(0.0, center - half), min(1.0, center + half))


def _exact_mcnemar(a_only: int, b_only: int) -> float:
    n = a_only + b_only
    if n == 0:
        return 1.0
    tail = min(a_only, b_only)
    probability = sum(math.comb(n, k) for k in range(tail + 1)) / (2**n)
    return min(1.0, 2.0 * probability)


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _paired_counts(
    left: dict[str, bool],
    right: dict[str, bool],
) -> dict[str, int | float]:
    common = sorted(set(left) & set(right))
    both = sum(left[key] and right[key] for key in common)
    left_only = sum(left[key] and not right[key] for key in common)
    right_only = sum(not left[key] and right[key] for key in common)
    neither = len(common) - both - left_only - right_only
    return {
        "n": len(common),
        "both_correct": both,
        "left_only_correct": left_only,
        "right_only_correct": right_only,
        "both_wrong": neither,
        "exact_mcnemar_p": _exact_mcnemar(left_only, right_only),
    }


def _rate_summary(rows: list[dict[str, str]], key: str) -> dict[str, Any]:
    total = len(rows)
    successes = sum(_bool(row[key]) for row in rows)
    lower, upper = _wilson(successes, total)
    return {
        "successes": successes,
        "total": total,
        "rate": successes / total if total else 0.0,
        "wilson95": [lower, upper],
    }


def _pareto_models(by_model: dict[str, Any]) -> list[str]:
    labels = list(by_model)
    efficient: list[str] = []
    for label in labels:
        item = by_model[label]
        metrics = item["model_metrics"]
        resources = item["resource_metrics"]
        target = (
            float(metrics["gated_policy_conformant_rate"]),
            float(metrics["warm_mean_latency_seconds"]),
            float(resources["peak_model_process_family_rss_bytes"]),
        )
        dominated = False
        for other_label in labels:
            if other_label == label:
                continue
            other = by_model[other_label]
            om = other["model_metrics"]
            ors = other["resource_metrics"]
            candidate = (
                float(om["gated_policy_conformant_rate"]),
                float(om["warm_mean_latency_seconds"]),
                float(ors["peak_model_process_family_rss_bytes"]),
            )
            no_worse = (
                candidate[0] >= target[0]
                and candidate[1] <= target[1]
                and candidate[2] <= target[2]
            )
            strictly_better = (
                candidate[0] > target[0]
                or candidate[1] < target[1]
                or candidate[2] < target[2]
            )
            if no_worse and strictly_better:
                dominated = True
                break
        if not dominated:
            efficient.append(label)
    return efficient


def _fmt_interval(item: dict[str, Any]) -> str:
    low, high = item["wilson95"]
    return f"{item['successes']}/{item['total']} = {item['rate']:.4f} [{low:.4f}, {high:.4f}]"


def main() -> int:
    required = [
        PHASE11_DIR / "summary.json",
        PHASE11_DIR / "per_response.csv",
        PHASE12_DIR / "summary.json",
        PHASE12_DIR / "per_response.csv",
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Phase 13 requires completed machine-generated Phase 11 and Phase 12 results: "
            + ", ".join(missing)
        )

    phase11_summary = _load_json(PHASE11_DIR / "summary.json")
    phase11_rows = _load_csv(PHASE11_DIR / "per_response.csv")
    phase12_summary = _load_json(PHASE12_DIR / "summary.json")
    phase12_rows = _load_csv(PHASE12_DIR / "per_response.csv")

    phase11 = {
        "baseline": _rate_summary(phase11_rows, "baseline_policy_conformant"),
        "gated": _rate_summary(phase11_rows, "gated_policy_conformant"),
        "known_preservation": _rate_summary(
            [row for row in phase11_rows if row["expected_fault_id"] != "unknown"],
            "gated_policy_conformant",
        ),
        "required_defer": _rate_summary(
            [row for row in phase11_rows if row["expected_fault_id"] == "unknown"],
            "gated_policy_conformant",
        ),
        "paired": phase11_summary["overall"]["paired"],
    }

    rows_by_model: dict[str, list[dict[str, str]]] = {}
    for row in phase12_rows:
        rows_by_model.setdefault(row["model_label"], []).append(row)

    phase12_rates: dict[str, Any] = {}
    paired_models: dict[str, Any] = {}
    model_maps: dict[str, dict[str, bool]] = {}
    for label, rows in rows_by_model.items():
        phase12_rates[label] = {
            "gated": _rate_summary(rows, "gated_policy_conformant"),
            "known_preservation": _rate_summary(
                [row for row in rows if row["expected_fault_id"] != "unknown"],
                "gated_policy_conformant",
            ),
            "required_defer": _rate_summary(
                [row for row in rows if row["expected_fault_id"] == "unknown"],
                "gated_policy_conformant",
            ),
        }
        model_maps[label] = {
            row["scenario_id"]: _bool(row["gated_policy_conformant"])
            for row in rows
        }

    labels = list(rows_by_model)
    for index, left in enumerate(labels):
        for right in labels[index + 1 :]:
            paired_models[f"{left}_vs_{right}"] = _paired_counts(
                model_maps[left],
                model_maps[right],
            )

    pareto = _pareto_models(phase12_summary["by_model"])
    summary = {
        "schema_version": 1,
        "study_role": "final retrospective statistical synthesis after completed Phase 11 and Phase 12 experiments",
        "phase11": phase11,
        "phase12_rates": phase12_rates,
        "phase12_pairwise_exact_mcnemar": paired_models,
        "phase12_pareto_efficient_models": pareto,
        "caveats": [
            "Phase 11 and Phase 12 remain synthetic benchmarks.",
            "Phase 12 resource measurements are single-host measurements.",
            "Pairwise model tests are exploratory unless separately multiplicity-adjusted.",
            "The Phase 11 gate was designed after Phase 9 failure analysis, then evaluated on held-out seeds.",
        ],
    }

    lines = [
        "# KARZOUN-X Phase 13 Final Statistical Synthesis",
        "",
        "## Phase 11 epistemic-gate mitigation",
        "",
        f"- baseline policy conformance: **{_fmt_interval(phase11['baseline'])}**",
        f"- gated policy conformance: **{_fmt_interval(phase11['gated'])}**",
        f"- known-case preservation: **{_fmt_interval(phase11['known_preservation'])}**",
        f"- required-defer capture: **{_fmt_interval(phase11['required_defer'])}**",
        f"- paired exact McNemar p: **{float(phase11['paired']['exact_mcnemar_p']):.12g}**",
        "",
        "## Phase 12 model/resource ablation",
        "",
        "| Model | Gated policy with Wilson 95% CI | Known preservation | Required defer |",
        "|---|---|---|---|",
    ]
    for label, values in phase12_rates.items():
        lines.append(
            f"| {label} | {_fmt_interval(values['gated'])} | "
            f"{_fmt_interval(values['known_preservation'])} | "
            f"{_fmt_interval(values['required_defer'])} |"
        )
    lines.extend(["", "### Pairwise exact McNemar tests", ""])
    for name, values in paired_models.items():
        lines.append(
            f"- `{name}`: discordant left-only={values['left_only_correct']}, "
            f"right-only={values['right_only_correct']}, p={float(values['exact_mcnemar_p']):.12g}"
        )
    lines.extend(
        [
            "",
            "### Pareto-efficient model labels",
            "",
            ", ".join(f"`{label}`" for label in pareto) if pareto else "None",
            "",
            (
                "> Pareto efficiency here jointly maximizes gated policy conformance while "
                "minimizing warm mean latency and peak model-process-family RSS."
            ),
            "",
            (
                "> These statistics support the stated synthetic and single-host scope only; "
                "they do not establish flight readiness or operational spacecraft safety."
            ),
            "",
        ]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
