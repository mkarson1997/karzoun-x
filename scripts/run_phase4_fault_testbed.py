from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from karzoun_x.evaluation.telemetry_benchmark import sha256_file
from karzoun_x.rag.retriever import LocalRetriever
from karzoun_x.safety import SafetyGate
from karzoun_x.simulator import generate_scenarios, knowledge_documents
from karzoun_x.types import GateDecision

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "experiments" / "configs" / "phase4_fault_testbed.json"
OUTPUT_DIR = REPO_ROOT / "results" / "phase4"


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _markdown(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    return "\n".join(
        [
            "# KARZOUN-X Phase 4 Synthetic Fault Testbed Results",
            "",
            f"Experiment: `{summary['experiment_id']}`",
            f"Held-out scenarios evaluated: **{summary['heldout_scenarios']}**",
            f"Fault classes: **{summary['fault_classes']}**",
            "",
            "| Metric | Result |",
            "|---|---:|",
            f"| Retrieval top-1 accuracy | {metrics['retrieval_top1_accuracy']:.4f} |",
            f"| Retrieval top-3 recall | {metrics['retrieval_top3_recall']:.4f} |",
            f"| Safe-action allow rate | {metrics['safe_action_allow_rate']:.4f} |",
            f"| Unsafe-action block rate | {metrics['unsafe_action_block_rate']:.4f} |",
            (
                "| Unsafe-action false-allow rate | "
                f"{metrics['unsafe_action_false_allow_rate']:.4f} |"
            ),
            "",
            "> This is a deterministic synthetic research testbed, not real flight telemetry.",
            (
                "> It validates retrieval and safety mechanics; "
                "it does not validate LLM diagnosis yet."
            ),
            "",
        ]
    )


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    heldout_seeds = [int(seed) for seed in config["testbed"]["heldout_seeds"]]
    scenarios = generate_scenarios(heldout_seeds)
    retriever = LocalRetriever(knowledge_documents())
    gate = SafetyGate()
    top_k = int(config["retrieval"]["top_k"])

    rows: list[dict[str, Any]] = []
    top1_hits = 0
    top3_hits = 0
    safe_allows = 0
    unsafe_blocks = 0
    unsafe_false_allows = 0

    for scenario in scenarios:
        evidence = retriever.search(scenario.telemetry_context, top_k=top_k)
        retrieved_ids = [item.document_id for item in evidence]
        top1_hit = bool(retrieved_ids and retrieved_ids[0] == scenario.expected_document_id)
        top3_hit = scenario.expected_document_id in retrieved_ids
        safe_result = gate.evaluate(scenario.safe_action)
        unsafe_result = gate.evaluate(scenario.unsafe_action)
        unsafe_blocked = unsafe_result.decision in {GateDecision.DENY, GateDecision.ESCALATE}
        unsafe_false_allowed = unsafe_result.decision == GateDecision.ALLOW

        top1_hits += int(top1_hit)
        top3_hits += int(top3_hit)
        safe_allows += int(safe_result.decision == GateDecision.ALLOW)
        unsafe_blocks += int(unsafe_blocked)
        unsafe_false_allows += int(unsafe_false_allowed)

        rows.append(
            {
                "scenario_id": scenario.scenario_id,
                "seed": scenario.seed,
                "fault_id": scenario.fault_id,
                "subsystem": scenario.subsystem,
                "telemetry_context": scenario.telemetry_context,
                "expected_document_id": scenario.expected_document_id,
                "retrieved_document_ids": "|".join(retrieved_ids),
                "top1_hit": top1_hit,
                "top3_hit": top3_hit,
                "safe_action": scenario.safe_action.name,
                "safe_decision": safe_result.decision.value,
                "unsafe_action": scenario.unsafe_action.name,
                "unsafe_decision": unsafe_result.decision.value,
                "unsafe_blocked": unsafe_blocked,
            }
        )

    total = len(rows)
    metrics = {
        "retrieval_top1_accuracy": _rate(top1_hits, total),
        "retrieval_top3_recall": _rate(top3_hits, total),
        "safe_action_allow_rate": _rate(safe_allows, total),
        "unsafe_action_block_rate": _rate(unsafe_blocks, total),
        "unsafe_action_false_allow_rate": _rate(unsafe_false_allows, total),
    }
    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "experiment_id": config["experiment_id"],
        "study_role": config["study_role"],
        "config_sha256": sha256_file(CONFIG_PATH),
        "heldout_seeds": heldout_seeds,
        "heldout_scenarios": total,
        "fault_classes": len(config["testbed"]["fault_classes"]),
        "retrieval": config["retrieval"],
        "safety": config["safety"],
        "integrity": config["integrity"],
        "metrics": metrics,
        "counts": {
            "retrieval_top1_hits": top1_hits,
            "retrieval_top3_hits": top3_hits,
            "safe_action_allows": safe_allows,
            "unsafe_action_blocks": unsafe_blocks,
            "unsafe_action_false_allows": unsafe_false_allows,
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "summary.md").write_text(_markdown(summary), encoding="utf-8")
    with (OUTPUT_DIR / "per_scenario.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("KARZOUN_X_PHASE4_RESULT=" + json.dumps(summary, separators=(",", ":")))
    print((OUTPUT_DIR / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
