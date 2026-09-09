from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from karzoun_x.anomaly_detection import StabilityAwareDetector
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
CONFIG_PATH = REPO_ROOT / "experiments" / "configs" / "phase3_stability_aware.json"
PHASE1_RESULTS_PATH = REPO_ROOT / "results" / "phase1" / "summary.json"
PHASE2_RESULTS_PATH = REPO_ROOT / "results" / "phase2" / "summary.json"
OUTPUT_DIR = REPO_ROOT / "results" / "phase3"


def _evaluate_record(
    channel: LabeledChannel,
    train_files: dict[str, Path],
    test_files: dict[str, Path],
    threshold: float,
) -> dict[str, Any]:
    train_path = train_files.get(channel.channel_id)
    test_path = test_files.get(channel.channel_id)
    if train_path is None or test_path is None:
        raise FileNotFoundError("Missing train/test telemetry arrays for a benchmark record.")

    train = load_series(train_path)
    test = load_series(test_path)
    detector = StabilityAwareDetector(threshold=threshold).fit(train)
    scores = np.fromiter((detector.score(float(value)) for value in test), dtype=float)
    prediction_np = scores >= threshold
    truth = truth_mask(len(test), channel.anomaly_sequences)
    metrics = pointwise_metrics(truth, prediction_np.tolist())
    hit_count, event_total = event_hits(
        channel.anomaly_sequences,
        set(np.flatnonzero(prediction_np).tolist()),
    )

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
        "predicted_points": int(prediction_np.sum()),
        "max_score": float(scores.max(initial=0.0)),
        "scale": detector.scale,
        "scale_source": detector.scale_source,
        **asdict(metrics),
    }


def _deltas(current: dict[str, Any], reference: dict[str, Any]) -> dict[str, float | int]:
    return {
        "precision": float(current["precision"]) - float(reference["precision"]),
        "recall": float(current["recall"]) - float(reference["recall"]),
        "f1": float(current["f1"]) - float(reference["f1"]),
        "event_recall": float(current["event_recall"]) - float(reference["event_recall"]),
        "false_positives": int(current["false_positives"]) - int(reference["false_positives"]),
        "predicted_points": int(current["predicted_points"]) - int(reference["predicted_points"]),
    }


def _markdown(summary: dict[str, Any]) -> str:
    total = summary["aggregate"]["total"]
    detector = summary["detector"]
    p1 = summary["comparison"]["phase1_total_delta"]
    p2 = summary["comparison"]["phase2_total_delta"]
    lines = [
        "# KARZOUN-X Phase 3 Stability-Aware Results",
        "",
        f"Experiment: `{summary['experiment_id']}`",
        f"Detector threshold: `{detector['threshold']}`",
        "Study role: exploratory iterative refinement; not a confirmatory untouched holdout.",
        f"Benchmark records evaluated: **{total['channels']}**",
        f"Labeled anomaly events: **{total['labeled_events']}**",
        f"Telemetry test points: **{total['test_points']:,}**",
        "",
        "| Scope | Precision | Recall | F1 | Event recall | Records |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for scope in ("SMAP", "MSL", "total"):
        metrics = summary["aggregate"].get(scope)
        if metrics is not None:
            lines.append(
                "| {scope} | {precision:.4f} | {recall:.4f} | {f1:.4f} | "
                "{event_recall:.4f} | {channels} |".format(scope=scope, **metrics)
            )
    lines.extend(
        [
            "",
            "## Total change versus Phase 1",
            f"- Precision: {p1['precision']:+.4f}",
            f"- Recall: {p1['recall']:+.4f}",
            f"- F1: {p1['f1']:+.4f}",
            f"- Event recall: {p1['event_recall']:+.4f}",
            f"- False positives: {p1['false_positives']:+d}",
            "",
            "## Total change versus Phase 2",
            f"- Precision: {p2['precision']:+.4f}",
            f"- Recall: {p2['recall']:+.4f}",
            f"- F1: {p2['f1']:+.4f}",
            f"- Event recall: {p2['event_recall']:+.4f}",
            f"- False positives: {p2['false_positives']:+d}",
            "",
            "> Results are machine-generated from the frozen Phase 3 configuration.",
            (
                "> Phase 3 was designed after observing prior phases, "
                "so it is reported as exploratory."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    phase1 = json.loads(PHASE1_RESULTS_PATH.read_text(encoding="utf-8"))
    phase2 = json.loads(PHASE2_RESULTS_PATH.read_text(encoding="utf-8"))
    dataset = config["dataset"]
    labels_path = repo_path(REPO_ROOT, str(dataset["labels_path"]))
    train_files = npy_files(repo_path(REPO_ROOT, str(dataset["train_dir"])))
    test_files = npy_files(repo_path(REPO_ROOT, str(dataset["test_dir"])))
    threshold = float(config["detector"]["threshold"])
    channels = load_labeled_channels(labels_path)
    if not channels:
        raise RuntimeError("No labeled channels found.")

    rows = [_evaluate_record(channel, train_files, test_files, threshold) for channel in channels]
    by_spacecraft: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_spacecraft.setdefault(str(row["spacecraft"]), []).append(row)
    aggregate = {name: aggregate_rows(group) for name, group in sorted(by_spacecraft.items())}
    aggregate["total"] = aggregate_rows(rows)
    total = aggregate["total"]

    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "experiment_id": config["experiment_id"],
        "study_role": config["study_role"],
        "config_sha256": sha256_file(CONFIG_PATH),
        "labels_sha256": sha256_file(labels_path),
        "dataset_source": dataset["source"],
        "detector": config["detector"],
        "integrity": config["integrity"],
        "aggregate": aggregate,
        "scale_source_counts": dict(
            sorted(Counter(str(row["scale_source"]) for row in rows).items())
        ),
        "comparison": {
            "phase1_reference": phase1["experiment_id"],
            "phase1_total_delta": _deltas(total, phase1["aggregate"]["total"]),
            "phase2_reference": phase2["experiment_id"],
            "phase2_total_delta": _deltas(total, phase2["aggregate"]["total"]),
        },
        "metadata_length_mismatches": [
            row["channel_id"] for row in rows if not row["length_matches_metadata"]
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    with (OUTPUT_DIR / "per_record.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    (OUTPUT_DIR / "summary.md").write_text(_markdown(summary), encoding="utf-8")

    print("KARZOUN_X_PHASE3_RESULT=" + json.dumps(summary, separators=(",", ":")))
    print((OUTPUT_DIR / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
