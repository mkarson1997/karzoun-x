from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommunicationProfile:
    one_way_delay_s: float = 0.0
    jitter_s: float = 0.0
    packet_loss_probability: float = 0.0
    outage: bool = False

    def simulated_delivery(self, rng: random.Random | None = None) -> tuple[bool, float]:
        if self.outage:
            return False, float("inf")
        generator = rng or random.Random()
        if not 0.0 <= self.packet_loss_probability <= 1.0:
            raise ValueError("packet_loss_probability must be between 0 and 1")
        delivered = generator.random() >= self.packet_loss_probability
        if not delivered:
            return False, float("inf")
        jitter = generator.uniform(-self.jitter_s, self.jitter_s) if self.jitter_s else 0.0
        return True, max(0.0, self.one_way_delay_s + jitter)
