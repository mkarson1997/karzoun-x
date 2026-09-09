from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from karzoun_x.anomaly_detection import AdaptiveRobustDetector, apply_persistence_filter
from karzoun_x.datasets.telemanom import LabeledChannel, load_labeled_channels
from karzoun_x.evaluation.metrics import pointwise_metrics
from karzoun_x.evaluation.telemetry_benchmark import (
    aggregate_rows,
    event_hits,
    load_series,
    npy_files,
    repo_path,
    sha256_file,
    truth_mask,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "experiments" / "configs" / "phase2_adaptive_temporal.json"
PHASE1_RESULTS_PATH = REPO_ROOT / "results" / "phase1" / "summary.json"
OUTPUT_DIR = REPO_ROOT / "results" / "phase2"


def _evaluate_record(
    channel: LabeledChannel,
    train_files: dict[str, Path],
    test_files: dict[str, Path],
    threshold: float,
    min_consecutive: int,
) -> dict[str, Any]:
    train_path = train_files.get(channel.channel_id)
    test_path = test_files.get(channel.channel_id)
    if train_path is None or test_path is None:
        raise FileNotFoundError("Missing train/test telemetry arrays for a benchmark record.")

    train = load_series(train_path)
    test = load_series(test_path)
    detector = AdaptiveRobustDetector(threshold=threshold).fit(train)

    scores = np.fromiter((detector.score(float(value)) for value in test), dtype=float)
    raw_prediction = scores >= threshold
    prediction_np = apply_persistence_filter(raw_prediction, min_consecutive=min_consecutive)
    prediction = prediction_np.tolist()
    truth = truth_mask(len(test), channel.anomaly_sequences)
    metrics = pointwise_metrics(truth, prediction)
    predicted_indices = set(np.flatnonzero(prediction_np).tolist())
    hit_count, event_total = event_hits(channel.anomaly_sequences, predicted_indices)

    return {
        "channel_id": channel.channel_id,
        "spacecraft": channel.spacecraft,
        "train_points": int(len(train)),
        "test_points": int(len(test)),
        "metadata_num_values": channel.num_values,
        "length_matches_metadata": int(len(test)) == channel.num_values,
        "labeled_events": event_total,
        "event_hits": hit_count,
        "event_recall": hit_count / event_total if event_total else 0.0,
        "raw_predicted_points": int(raw_prediction.sum()),
        "predicted_points": int(prediction_np.sum()),
        "max_score": float(scores.max(initial=0.0)),
        "scale": detector.scale,
        "scale_source": detector.scale_source,
        **asdict(metrics),
    }


def _metric_deltas(current: dict[str, Any], reference: dict[str, Any]) -> dict[str, float | int]:
    return {
        "precision": float(current["precision"]) - float(reference["precision"]),
        "recall": float(current["recall"]) - float(reference["recall"]),
        "f1": float(current["f1"]) - float(reference["f1"]),
        "event_recall": float(current["event_recall"]) - float(reference["event_recall"]),
        "predicted_points": int(current["predicted_points"]) - int(reference["predicted_points"]),
        "false_positives": int(current["false_positives"]) - int(reference["false_positives"]),
    }


def _markdown(summary: dict[str, Any]) -> str:
    total = summary["aggregate"]["total"]
    delta = summary["comparison_to_phase1"]["total_delta"]
    detector = summary["detector"]
    lines = [
        "# KARZOUN-X Phase 2 Adaptive Temporal Results",
        "",
        f"Experiment: `{summary['experiment_id']}`",
        f"Detector threshold: `{detector['threshold']}`",
        f"Persistence requirement: `{detector['persistence_min_consecutive']}` samples",
        f"Benchmark records evaluated: **{total['channels']}**",
        f"Labeled anomaly events: **{total['labeled_events']}**",
        f"Telemetry test points: **{total['test_points']:,}**",
        "",
        "| Scope | Precision | Recall | F1 | Event recall | Records |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for scope in ("SMAP", "MSL", "total"):
        metrics = summary["aggregate"].get(scope)
        if metrics is None:
            continue
        lines.append(
            "| {scope} | {precision:.4f} | {recall:.4f} | {f1:.4f} | "
            "{event_recall:.4f} | {channels} |".format(scope=scope, **metrics)
        )
    lines.extend(
        [
            "",
            "## Total change versus Phase 1",
            "",
            f"- Precision: {delta['precision']:+.4f}",
            f"- Recall: {delta['recall']:+.4f}",
            f"- F1: {delta['f1']:+.4f}",
            f"- Event recall: {delta['event_recall']:+.4f}",
            f"- False positives: {delta['false_positives']:+d}",
            f"- Predicted points: {delta['predicted_points']:+d}",
            "",
            "> Results are machine-generated from the frozen Phase 2 configuration.",
            "> Phase 2 parameters were fixed before test-label evaluation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    phase1_summary = json.loads(PHASE1_RESULTS_PATH.read_text(encoding="utf-8"))
    dataset = config["dataset"]
    labels_path = repo_path(REPO_ROOT, str(dataset["labels_path"]))
    train_dir = repo_path(REPO_ROOT, str(dataset["train_dir"]))
    test_dir = repo_path(REPO_ROOT, str(dataset["test_dir"]))
    threshold = float(config["detector"]["threshold"])
    min_consecutive = int(config["detector"]["persistence_min_consecutive"])

    train_files = npy_files(train_dir)
    test_files = npy_files(test_dir)
    channels = load_labeled_channels(labels_path)
    if not channels:
        raise RuntimeError("No labeled channels found.")

    rows = [
        _evaluate_record(
            channel,
            train_files,
            test_files,
            threshold,
            min_consecutive,
        )
        for channel in channels
    ]
    by_spacecraft: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_spacecraft.setdefault(str(row["spacecraft"]), []).append(row)

    aggregate = {
        name: aggregate_rows(group) for name, group in sorted(by_spacecraft.items())
    }
    aggregate["total"] = aggregate_rows(rows)
    phase1_total = phase1_summary["aggregate"]["total"]
    scale_sources = Counter(str(row["scale_source"]) for row in rows)

    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "experiment_id": config["experiment_id"],
        "config_sha256": sha256_file(CONFIG_PATH),
        "labels_sha256": sha256_file(labels_path),
        "dataset_source": dataset["source"],
        "detector": config["detector"],
        "integrity": config["integrity"],
        "aggregate": aggregate,
        "scale_source_counts": dict(sorted(scale_sources.items())),
        "comparison_to_phase1": {
            "reference_experiment": phase1_summary["experiment_id"],
            "reference_config_sha256": phase1_summary["config_sha256"],
            "total_delta": _metric_deltas(aggregate["total"], phase1_total),
        },
        "metadata_length_mismatches": [
            row["channel_id"] for row in rows if not row["length_matches_metadata"]
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUTPUT_DIR / "summary.json"
    csv_path = OUTPUT_DIR / "per_record.csv"
    markdown_path = OUTPUT_DIR / "summary.md"

    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    markdown_path.write_text(_markdown(summary), encoding="utf-8")

    print("KARZOUN_X_PHASE2_RESULT=" + json.dumps(summary, separators=(",", ":")))
    print(markdown_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
