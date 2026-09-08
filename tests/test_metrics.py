import pytest

from karzoun_x.evaluation import event_recall, pointwise_metrics


def test_pointwise_metrics() -> None:
    metrics = pointwise_metrics(
        [False, True, True, False],
        [False, True, False, True],
    )
    assert metrics.precision == pytest.approx(0.5)
    assert metrics.recall == pytest.approx(0.5)
    assert metrics.f1 == pytest.approx(0.5)


def test_event_recall_counts_interval_hit_once() -> None:
    recall = event_recall(((10, 20), (30, 40)), {15, 16, 50})
    assert recall == pytest.approx(0.5)
