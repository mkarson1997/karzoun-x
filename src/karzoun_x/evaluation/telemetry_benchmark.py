from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(repo_root: Path, relative_path: str) -> Path:
    candidate = (repo_root / relative_path).resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError as exc:
        message = f"Configured path must remain inside the repository: {relative_path!r}"
        raise ValueError(message) from exc
    return candidate


def npy_files(directory: Path) -> dict[str, Path]:
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


def load_series(path: Path) -> np.ndarray:
    values = np.load(path, allow_pickle=False)
    if values.ndim == 1:
        return values.astype(float, copy=False)
    if values.ndim == 2 and values.shape[1] >= 1:
        return values[:, 0].astype(float, copy=False)
    raise ValueError(f"Unsupported telemetry array shape: {values.shape}")


def truth_mask(length: int, sequences: tuple[tuple[int, int], ...]) -> list[bool]:
    truth = [False] * length
    for start, end in sequences:
        if start >= length:
            continue
        clipped_end = min(end, length - 1)
        for index in range(start, clipped_end + 1):
            truth[index] = True
    return truth


def event_hits(
    sequences: tuple[tuple[int, int], ...], predicted_indices: set[int]
) -> tuple[int, int]:
    hits = sum(
        any(index in predicted_indices for index in range(start, end + 1))
        for start, end in sequences
    )
    return hits, len(sequences)


def metrics_from_counts(tp: int, fp: int, fn: int) -> dict[str, float | int]:
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


def aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(int(row["true_positives"]) for row in rows)
    fp = sum(int(row["false_positives"]) for row in rows)
    fn = sum(int(row["false_negatives"]) for row in rows)
    hit_count = sum(int(row["event_hits"]) for row in rows)
    event_total = sum(int(row["labeled_events"]) for row in rows)
    result: dict[str, Any] = {
        **metrics_from_counts(tp, fp, fn),
        "event_hits": hit_count,
        "labeled_events": event_total,
        "event_recall": hit_count / event_total if event_total else 0.0,
        "channels": len(rows),
        "test_points": sum(int(row["test_points"]) for row in rows),
        "predicted_points": sum(int(row["predicted_points"]) for row in rows),
    }
    if rows and "raw_predicted_points" in rows[0]:
        result["raw_predicted_points"] = sum(
            int(row["raw_predicted_points"]) for row in rows
        )
    return result
