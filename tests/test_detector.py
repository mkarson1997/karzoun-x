import numpy as np

from karzoun_x.anomaly_detection import (
    AdaptiveRobustDetector,
    RobustZScoreDetector,
    apply_persistence_filter,
)


def test_robust_zscore_flags_large_excursion() -> None:
    detector = RobustZScoreDetector(threshold=3.5).fit([1.0, 1.01, 0.99, 1.02, 0.98, 1.0])
    result = detector.predict_one(1.3)
    assert result.is_anomaly is True
    assert result.score >= result.threshold


def test_adaptive_detector_uses_std_when_robust_scale_collapses() -> None:
    values = [0.0] * 99 + [1.0]
    detector = AdaptiveRobustDetector(threshold=3.5).fit(values)
    assert detector.scale_source == "std-fallback"
    assert detector.scale > 0.0


def test_adaptive_detector_flags_clear_excursion() -> None:
    detector = AdaptiveRobustDetector(threshold=3.5).fit(
        [1.0, 1.01, 0.99, 1.02, 0.98, 1.0]
    )
    result = detector.predict_one(1.3)
    assert result.is_anomaly is True


def test_persistence_filter_removes_short_runs() -> None:
    flags = np.array([False, True, False, True, True, True, False, True, True])
    filtered = apply_persistence_filter(flags, min_consecutive=3)
    assert filtered.tolist() == [
        False,
        False,
        False,
        True,
        True,
        True,
        False,
        False,
        False,
    ]


def test_persistence_filter_keeps_trailing_run() -> None:
    filtered = apply_persistence_filter([False, True, True, True], min_consecutive=3)
    assert filtered.tolist() == [False, True, True, True]
