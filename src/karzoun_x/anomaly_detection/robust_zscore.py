from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from karzoun_x.types import AnomalyResult


@dataclass(slots=True)
class RobustZScoreDetector:
    """Simple robust baseline using median absolute deviation (MAD).

    This is intentionally transparent and should not be treated as a strong final baseline.
    """

    threshold: float = 3.5
    epsilon: float = 1e-9
    _median: float | None = None
    _mad: float | None = None

    def fit(self, values: list[float] | np.ndarray) -> RobustZScoreDetector:
        arr = np.asarray(values, dtype=float)
        if arr.size < 3:
            raise ValueError("At least 3 values are required to fit the detector.")
        self._median = float(np.median(arr))
        self._mad = float(np.median(np.abs(arr - self._median)))
        return self

    def score(self, value: float) -> float:
        if self._median is None or self._mad is None:
            raise RuntimeError("Detector must be fit before scoring.")
        scale = max(self._mad, self.epsilon)
        return float(0.6745 * abs(value - self._median) / scale)

    def predict_one(self, value: float) -> AnomalyResult:
        score = self.score(value)
        is_anomaly = score >= self.threshold
        explanation = (
            f"robust-z={score:.3f} compared with threshold={self.threshold:.3f}"
        )
        return AnomalyResult(
            score=score,
            is_anomaly=is_anomaly,
            threshold=self.threshold,
            explanation=explanation,
        )
