import random

from karzoun_x.communication import CommunicationProfile


def test_outage_never_delivers() -> None:
    delivered, delay = CommunicationProfile(outage=True).simulated_delivery(random.Random(1))
    assert delivered is False
    assert delay == float("inf")


def test_zero_loss_delivers() -> None:
    delivered, delay = CommunicationProfile(one_way_delay_s=10).simulated_delivery(random.Random(1))
    assert delivered is True
    assert delay == 10
