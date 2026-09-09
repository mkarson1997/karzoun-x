from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from karzoun_x.anomaly_detection.stability_aware import StabilityAwareDetector
from karzoun_x.rag.retriever import LocalRetriever
from karzoun_x.safety import SafetyGate
from karzoun_x.simulator import generate_robustness_scenarios, knowledge_documents
from karzoun_x.types import GateDecision

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "experiments" / "configs" / "phase7a_robustness.json"
OUTPUT_DIR = REPO_ROOT / "results" / "phase7a"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rate(rows: list[dict[str, Any]], key: str) -> float:
    return sum(bool(row[key]) for row in rows) / len(rows) if rows else 0.0


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    nominal_points = sum(int(row["nominal_points"]) for row in rows)
    nominal_false_points = sum(int(row["nominal_false_points"]) for row in rows)
    return {
        "scenarios": len(rows),
        "detector_scenario_trigger_rate": _rate(rows, "detector_triggered"),
        "nominal_false_trigger_point_rate": (
            nominal_false_points / nominal_points if nominal_points else 0.0
        ),
        "retrieval_top1_accuracy": _rate(rows, "retrieval_top1_correct"),
        "retrieval_top3_recall": _rate(rows, "retrieval_top3_correct"),
        "expected_safe_action_allow_rate": _rate(rows, "safe_action_allowed"),
        "unsafe_action_block_rate": _rate(rows, "unsafe_action_blocked"),
        "integrated_mechanics_success_rate": _rate(rows, "integrated_mechanics_success"),
        "nominal_points": nominal_points,
        "nominal_false_points": nominal_false_points,
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# KARZOUN-X Phase 7A Expanded Robustness Results",
        "",
        f"Experiment: `{summary['experiment_id']}`",
        f"Synthetic scenarios: **{summary['overall']['scenarios']}**",
        "",
        (
            "Phase 7A expands the synthetic mechanics testbed before the next local-LLM run. "
            "Explicit fault labels are removed from telemetry text, and cases include clean, "
            "distractor, and partial-information variants. No language model participates in "
            "this phase."
        ),
        "",
        (
            "| Scope | Scenarios | Detector trigger | Nominal false-point rate | Retrieval top-1 | "
            "Retrieval top-3 | Safe allow | Unsafe block | Integrated success |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    scopes = [("overall", summary["overall"])] + [
        (difficulty, summary["by_difficulty"][difficulty])
        for difficulty in sorted(summary["by_difficulty"])
    ]
    for label, metrics in scopes:
        lines.append(
            "| {label} | {scenarios} | {detector:.4f} | {false_rate:.4f} | {top1:.4f} | "
            "{top3:.4f} | {safe:.4f} | {unsafe:.4f} | {integrated:.4f} |".format(
                label=label,
                scenarios=metrics["scenarios"],
                detector=metrics["detector_scenario_trigger_rate"],
                false_rate=metrics["nominal_false_trigger_point_rate"],
                top1=metrics["retrieval_top1_accuracy"],
                top3=metrics["retrieval_top3_recall"],
                safe=metrics["expected_safe_action_allow_rate"],
                unsafe=metrics["unsafe_action_block_rate"],
                integrated=metrics["integrated_mechanics_success_rate"],
            )
        )

    lines.extend(
        [
            "",
            (
                "> Phase 7A is a deterministic synthetic robustness test. It validates expanded "
                "detector/retrieval/safety mechanics only and is not evidence of spacecraft or "
                "language-model performance."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    seeds = [int(seed) for seed in config["seeds"]]
    difficulties = tuple(str(value) for value in config["difficulties"])
    scenarios = generate_robustness_scenarios(seeds, difficulties)
    expected_count = int(config["expected_scenarios"])
    if len(scenarios) != expected_count:
        raise ValueError(f"Expected {expected_count} scenarios, got {len(scenarios)}")

    retriever = LocalRetriever(knowledge_documents())
    gate = SafetyGate()
    detector_threshold = float(config["detector"]["threshold"])
    retrieval_top_k = int(config["retrieval"]["top_k"])
    rows: list[dict[str, Any]] = []

    for scenario in scenarios:
        detector = StabilityAwareDetector(threshold=detector_threshold).fit(
            list(scenario.detector_train)
        )
        predictions = [detector.predict_one(value) for value in scenario.detector_test]
        nominal_predictions = predictions[: scenario.anomaly_start_index]
        fault_predictions = predictions[scenario.anomaly_start_index :]
        nominal_false_points = sum(result.is_anomaly for result in nominal_predictions)
        detector_triggered = any(result.is_anomaly for result in fault_predictions)

        evidence = retriever.search(
            scenario.telemetry_context,
            top_k=retrieval_top_k,
        )
        retrieved_ids = [item.document_id for item in evidence]
        top1_correct = bool(retrieved_ids) and retrieved_ids[0] == scenario.expected_document_id
        top3_correct = scenario.expected_document_id in retrieved_ids

        safe_result = gate.evaluate(scenario.safe_action)
        unsafe_result = gate.evaluate(scenario.unsafe_action)
        safe_allowed = safe_result.decision == GateDecision.ALLOW
        unsafe_blocked = unsafe_result.decision != GateDecision.ALLOW
        integrated_success = (
            detector_triggered and top3_correct and safe_allowed and unsafe_blocked
        )

        rows.append(
            {
                "scenario_id": scenario.scenario_id,
                "seed": scenario.seed,
                "difficulty": scenario.difficulty,
                "fault_id": scenario.fault_id,
                "subsystem": scenario.subsystem,
                "detector_scale_source": detector.scale_source,
                "detector_triggered": detector_triggered,
                "nominal_points": len(nominal_predictions),
                "nominal_false_points": nominal_false_points,
                "retrieved_document_ids": ";".join(retrieved_ids),
                "retrieval_top1_correct": top1_correct,
                "retrieval_top3_correct": top3_correct,
                "safe_action": scenario.safe_action.name,
                "safe_decision": safe_result.decision.value,
                "safe_action_allowed": safe_allowed,
                "unsafe_action": scenario.unsafe_action.name,
                "unsafe_decision": unsafe_result.decision.value,
                "unsafe_action_blocked": unsafe_blocked,
                "integrated_mechanics_success": integrated_success,
                "telemetry_context": scenario.telemetry_context,
            }
        )

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["difficulty"])].append(row)

    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "experiment_id": config["experiment_id"],
        "study_role": config["study_role"],
        "config_sha256": _sha256(CONFIG_PATH),
        "overall": _aggregate(rows),
        "by_difficulty": {name: _aggregate(items) for name, items in sorted(grouped.items())},
        "integrity": config["integrity"],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT_DIR / "summary.md").write_text(_markdown(summary), encoding="utf-8")
    with (OUTPUT_DIR / "per_scenario.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print("KARZOUN_X_PHASE7A_RESULT=" + json.dumps(summary, separators=(",", ":")))
    print((OUTPUT_DIR / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
