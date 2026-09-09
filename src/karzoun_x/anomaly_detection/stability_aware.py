from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from karzoun_x.types import AnomalyResult


@dataclass(slots=True)
class StabilityAwareDetector:
    """Phase 1-compatible robust detector with a training-only stability fallback.

    The detector keeps the Phase 1 MAD scoring rule whenever the training MAD is
    informative. If the MAD collapses while the training series still has finite
    variance, standard deviation is used instead. Constant training channels keep
    the Phase 1-compatible epsilon floor. No test labels are consulted during fit.
    """

    threshold: float = 3.5
    epsilon: float = 1e-9
    _median: float | None = None
    _scale: float | None = None
    _scale_source: str | None = None

    def fit(self, values: list[float] | np.ndarray) -> StabilityAwareDetector:
        arr = np.asarray(values, dtype=float).reshape(-1)
        arr = arr[np.isfinite(arr)]
        if arr.size < 3:
            raise ValueError("At least 3 finite values are required to fit the detector.")

        self._median = float(np.median(arr))
        mad = float(np.median(np.abs(arr - self._median)))

        if mad > self.epsilon:
            self._scale = mad / 0.6745
            self._scale_source = "mad"
            return self

        std = float(np.std(arr))
        if std > self.epsilon:
            self._scale = std
            self._scale_source = "std-fallback"
        else:
            self._scale = self.epsilon / 0.6745
            self._scale_source = "epsilon-floor"
        return self

    @property
    def scale_source(self) -> str:
        if self._scale_source is None:
            raise RuntimeError("Detector must be fit before scale metadata is read.")
        return self._scale_source

    @property
    def scale(self) -> float:
        if self._scale is None:
            raise RuntimeError("Detector must be fit before scale metadata is read.")
        return self._scale

    def score(self, value: float) -> float:
        if self._median is None or self._scale is None:
            raise RuntimeError("Detector must be fit before scoring.")
        return float(abs(value - self._median) / self._scale)

    def predict_one(self, value: float) -> AnomalyResult:
        score = self.score(value)
        return AnomalyResult(
            score=score,
            is_anomaly=score >= self.threshold,
            threshold=self.threshold,
            explanation=(
                f"stability-aware-z={score:.3f}; threshold={self.threshold:.3f}; "
                f"scale={self.scale:.6g} ({self.scale_source})"
            ),
        )
