from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from karzoun_x.types import AnomalyResult


@dataclass(slots=True)
class AdaptiveRobustDetector:
    """Training-only robust detector with a stable scale fallback.

    Phase 1 used MAD directly. Several benchmark channels have a collapsed
    training MAD, so tiny departures can become extreme scores. This detector
    keeps the median center but estimates scale from MAD and IQR, falling back
    to standard deviation only when both robust scales collapse.
    """

    threshold: float = 3.5
    epsilon: float = 1e-9
    _median: float | None = None
    _scale: float | None = None
    _scale_source: str | None = None

    def fit(self, values: list[float] | np.ndarray) -> AdaptiveRobustDetector:
        arr = np.asarray(values, dtype=float).reshape(-1)
        arr = arr[np.isfinite(arr)]
        if arr.size < 3:
            raise ValueError("At least 3 finite values are required to fit the detector.")

        self._median = float(np.median(arr))
        mad = float(np.median(np.abs(arr - self._median)))
        q25, q75 = np.percentile(arr, [25.0, 75.0])
        iqr = float(q75 - q25)

        mad_sigma = 1.4826 * mad
        iqr_sigma = iqr / 1.349 if iqr > 0.0 else 0.0
        robust_scale = max(mad_sigma, iqr_sigma)

        if robust_scale > self.epsilon:
            self._scale = robust_scale
            self._scale_source = "robust-max(mad,iqr)"
        else:
            std = float(np.std(arr))
            self._scale = max(std, self.epsilon)
            self._scale_source = "std-fallback" if std > self.epsilon else "epsilon-floor"
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
        is_anomaly = score >= self.threshold
        explanation = (
            f"adaptive-robust-z={score:.3f}; threshold={self.threshold:.3f}; "
            f"scale={self.scale:.6g} ({self.scale_source})"
        )
        return AnomalyResult(
            score=score,
            is_anomaly=is_anomaly,
            threshold=self.threshold,
            explanation=explanation,
        )


def apply_persistence_filter(
    flags: list[bool] | np.ndarray,
    min_consecutive: int = 3,
) -> np.ndarray:
    """Keep anomaly runs that persist for at least ``min_consecutive`` samples."""

    if min_consecutive < 1:
        raise ValueError("min_consecutive must be at least 1.")

    values = np.asarray(flags, dtype=bool).reshape(-1)
    if min_consecutive == 1:
        return values.copy()

    filtered = np.zeros(values.shape, dtype=bool)
    run_start: int | None = None

    for index, is_anomaly in enumerate(values):
        if is_anomaly and run_start is None:
            run_start = index
            continue
        if not is_anomaly and run_start is not None:
            if index - run_start >= min_consecutive:
                filtered[run_start:index] = True
            run_start = None

    if run_start is not None and len(values) - run_start >= min_consecutive:
        filtered[run_start:] = True

    return filtered
