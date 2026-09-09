from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DecisionLatencyProfile:
    """Deterministic communication profile for decision-latency studies."""

    profile_id: str
    one_way_delay_s: float = 0.0
    outage: bool = False

    def __post_init__(self) -> None:
        if not self.profile_id.strip():
            raise ValueError("profile_id must not be empty")
        if not math.isfinite(self.one_way_delay_s) or self.one_way_delay_s < 0:
            raise ValueError("one_way_delay_s must be a finite non-negative number")


def local_decision_latency_s(compute_latency_s: float) -> float:
    """Return onboard decision latency when reasoning is executed locally."""

    if not math.isfinite(compute_latency_s) or compute_latency_s < 0:
        raise ValueError("compute_latency_s must be a finite non-negative number")
    return float(compute_latency_s)


def ground_in_loop_latency_s(
    compute_latency_s: float,
    profile: DecisionLatencyProfile,
) -> float | None:
    """Return decision availability time for a ground-dependent round trip.

    The same compute latency is used for local and hypothetical ground reasoning so
    the comparison isolates propagation delay. An outage returns ``None`` because
    the round trip cannot complete.
    """

    local_latency = local_decision_latency_s(compute_latency_s)
    if profile.outage:
        return None
    return local_latency + (2.0 * profile.one_way_delay_s)


def available_within_deadline(latency_s: float | None, deadline_s: float) -> bool:
    """Return whether a decision is available within a finite deadline."""

    if not math.isfinite(deadline_s) or deadline_s < 0:
        raise ValueError("deadline_s must be a finite non-negative number")
    return latency_s is not None and latency_s <= deadline_s
