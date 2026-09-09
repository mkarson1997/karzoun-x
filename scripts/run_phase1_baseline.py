from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from karzoun_x.anomaly_detection.robust_zscore import RobustZScoreDetector
from karzoun_x.datasets.telemanom import LabeledChannel, load_labeled_channels
from karzoun_x.evaluation.metrics import pointwise_metrics

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "experiments" / "configs" / "phase1_robust_zscore.json"
OUTPUT_DIR = REPO_ROOT / "results" / "phase1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_path(relative_path: str) -> Path:
    candidate = (REPO_ROOT / relative_path).resolve()
    try:
        candidate.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"Configured path must remain inside the repository: {relative_path!r}") from exc
    return candidate


def _npy_files(directory: Path) -> dict[str, Path]:
    resolved_directory = directory.resolve()
    files: dict[str, Path] = {}
    for path in resolved_directory.iterdir():
        if not path.is_file() or path.suffix != ".npy":
            continue
        resolved = path.resolve()
        if resolved.parent != resolved_directory:
            raise ValueError(f"Telemetry file escaped the expected directory: {path}")
        files[path.stem] = resolved
    return files


def _series(path: Path) -> np.ndarray:
    values = np.load(path, allow_pickle=False)
    if values.ndim == 1:
        return values.astype(float, copy=False)
    if values.ndim == 2 and values.shape[1] >= 1:
        return values[:, 0].astype(float, copy=False)
    raise ValueError(f"Unsupported telemetry array shape: {values.shape}")


def _truth_mask(length: int, sequences: tuple[tuple[int, int], ...]) -> list[bool]:
    truth = [False] * length
    for start, end in sequences:
        if start >= length:
            continue
        clipped_end = min(end, length - 1)
        for index in range(start, clipped_end + 1):
            truth[index] = True
    return truth


def _event_hits(
    sequences: tuple[tuple[int, int], ...], predicted_indices: set[int]
) -> tuple[int, int]:
    hits = sum(
        any(index in predicted_indices for index in range(start, end + 1))
        for start, end in sequences
    )
    return hits, len(sequences)


def _metrics_from_counts(tp: int, fp: int, fn: int) -> dict[str, float | int]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
    }


def _evaluate_channel(
    channel: LabeledChannel,
    train_files: dict[str, Path],
    test_files: dict[str, Path],
    threshold: float,
) -> dict[str, Any]:
    train_path = train_files.get(channel.channel_id)
    test_path = test_files.get(channel.channel_id)
    if train_path is None or test_path is None:
        raise FileNotFoundError(f"Missing train/test telemetry arrays for a benchmark record.")

    train = _series(train_path)
    test = _series(test_path)
    detector = RobustZScoreDetector(threshold=threshold).fit(train)

    scores = np.fromiter((detector.score(float(value)) for value in test), dtype=float)
    prediction_np = scores >= threshold
    prediction = prediction_np.tolist()
    truth = _truth_mask(len(test), channel.anomaly_sequences)
    metrics = pointwise_metrics(truth, prediction)
    predicted_indices = set(np.flatnonzero(prediction_np).tolist())
    event_hits, event_total = _event_hits(channel.anomaly_sequences, predicted_indices)

    return {
        "channel_id": channel.channel_id,
        "spacecraft": channel.spacecraft,
        "train_points": int(len(train)),
        "test_points": int(len(test)),
        "metadata_num_values": channel.num_values,
        "length_matches_metadata": int(len(test)) == channel.num_values,
        "labeled_events": event_total,
        "event_hits": event_hits,
        "event_recall": event_hits / event_total if event_total else 0.0,
        "predicted_points": int(prediction_np.sum()),
        "max_score": float(scores.max(initial=0.0)),
        **asdict(metrics),
    }


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(int(row["true_positives"]) for row in rows)
    fp = sum(int(row["false_positives"]) for row in rows)
    fn = sum(int(row["false_negatives"]) for row in rows)
    event_hits = sum(int(row["event_hits"]) for row in rows)
    event_total = sum(int(row["labeled_events"]) for row in rows)
    return {
        **_metrics_from_counts(tp, fp, fn),
        "event_hits": event_hits,
        "labeled_events": event_total,
        "event_recall": event_hits / event_total if event_total else 0.0,
        "channels": len(rows),
        "test_points": sum(int(row["test_points"]) for row in rows),
        "predicted_points": sum(int(row["predicted_points"]) for row in rows),
    }


def _markdown(summary: dict[str, Any]) -> str:
    total = summary["aggregate"]["total"]
    lines = [
        "# KARZOUN-X Phase 1 Baseline Results",
        "",
        f"Experiment: `{summary['experiment_id']}`",
        f"Detector: robust z-score (MAD), threshold `{summary['threshold']}`",
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
            "> These are machine-generated baseline results, not manually edited scores.",
            "> The fixed threshold was declared before evaluation in the experiment config.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    dataset = config["dataset"]
    labels_path = _repo_path(str(dataset["labels_path"]))
    train_dir = _repo_path(str(dataset["train_dir"]))
    test_dir = _repo_path(str(dataset["test_dir"]))
    threshold = float(config["detector"]["threshold"])

    train_files = _npy_files(train_dir)
    test_files = _npy_files(test_dir)
    channels = load_labeled_channels(labels_path)
    if not channels:
        raise RuntimeError("No labeled channels found.")

    rows = [
        _evaluate_channel(channel, train_files, test_files, threshold) for channel in channels
    ]
    by_spacecraft: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_spacecraft.setdefault(str(row["spacecraft"]), []).append(row)

    aggregate = {name: _aggregate(group) for name, group in sorted(by_spacecraft.items())}
    aggregate["total"] = _aggregate(rows)

    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "experiment_id": config["experiment_id"],
        "config_sha256": _sha256(CONFIG_PATH),
        "labels_sha256": _sha256(labels_path),
        "dataset_source": dataset["source"],
        "threshold": threshold,
        "detector": config["detector"],
        "integrity": config["integrity"],
        "aggregate": aggregate,
        "metadata_length_mismatches": [
            row["channel_id"] for row in rows if not row["length_matches_metadata"]
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUTPUT_DIR / "summary.json"
    csv_path = OUTPUT_DIR / "per_channel.csv"
    markdown_path = OUTPUT_DIR / "summary.md"

    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    markdown_path.write_text(_markdown(summary), encoding="utf-8")

    print("KARZOUN_X_PHASE1_RESULT=" + json.dumps(summary, separators=(",", ":")))
    print(markdown_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
