from karzoun_x.anomaly_detection import RobustZScoreDetector


def test_robust_zscore_flags_large_excursion() -> None:
    detector = RobustZScoreDetector(threshold=3.5).fit([1.0, 1.01, 0.99, 1.02, 0.98, 1.0])
    result = detector.predict_one(1.3)
    assert result.is_anomaly is True
    assert result.score >= result.threshold
