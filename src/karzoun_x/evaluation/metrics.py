from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BinaryMetrics:
    precision: float
    recall: float
    f1: float
    true_positives: int
    false_positives: int
    false_negatives: int


def pointwise_metrics(truth: list[bool], prediction: list[bool]) -> BinaryMetrics:
    if len(truth) != len(prediction):
        raise ValueError("truth and prediction must have equal length")
    if not truth:
        raise ValueError("truth and prediction must not be empty")

    tp = sum(t and p for t, p in zip(truth, prediction, strict=True))
    fp = sum((not t) and p for t, p in zip(truth, prediction, strict=True))
    fn = sum(t and (not p) for t, p in zip(truth, prediction, strict=True))

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return BinaryMetrics(
        precision=precision,
        recall=recall,
        f1=f1,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
    )


def event_recall(
    anomaly_sequences: list[tuple[int, int]] | tuple[tuple[int, int], ...],
    predicted_indices: set[int],
) -> float:
    """Return the fraction of labeled anomaly intervals hit at least once."""
    if not anomaly_sequences:
        return 0.0
    detected = sum(
        any(index in predicted_indices for index in range(start, end + 1))
        for start, end in anomaly_sequences
    )
    return detected / len(anomaly_sequences)
