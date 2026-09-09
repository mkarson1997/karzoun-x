import random

import pytest

from karzoun_x.communication import (
    CommunicationProfile,
    DecisionLatencyProfile,
    available_within_deadline,
    ground_in_loop_latency_s,
    local_decision_latency_s,
)


def test_outage_never_delivers() -> None:
    delivered, delay = CommunicationProfile(outage=True).simulated_delivery(random.Random(1))
    assert delivered is False
    assert delay == float("inf")


def test_zero_loss_delivers() -> None:
    delivered, delay = CommunicationProfile(one_way_delay_s=10).simulated_delivery(random.Random(1))
    assert delivered is True
    assert delay == 10


def test_ground_in_loop_adds_round_trip_delay() -> None:
    profile = DecisionLatencyProfile(profile_id="mars-reference", one_way_delay_s=240.0)
    assert local_decision_latency_s(25.0) == 25.0
    assert ground_in_loop_latency_s(25.0, profile) == 505.0


def test_ground_outage_has_no_completion_time() -> None:
    profile = DecisionLatencyProfile(profile_id="outage", outage=True)
    assert ground_in_loop_latency_s(25.0, profile) is None
    assert available_within_deadline(None, 60.0) is False


def test_invalid_latency_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        local_decision_latency_s(-1.0)
    with pytest.raises(ValueError):
        DecisionLatencyProfile(profile_id="bad", one_way_delay_s=-1.0)
    with pytest.raises(ValueError):
        available_within_deadline(1.0, -1.0)
