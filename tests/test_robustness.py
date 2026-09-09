from karzoun_x.simulator import generate_robustness_scenarios


def test_robustness_generator_is_deterministic_and_label_hidden() -> None:
    first = generate_robustness_scenarios([3301], ("clean", "distractor", "partial"))
    second = generate_robustness_scenarios([3301], ("clean", "distractor", "partial"))

    assert len(first) == 18
    assert first == second
    assert {item.difficulty for item in first} == {"clean", "distractor", "partial"}
    for item in first:
        assert item.fault_id not in item.telemetry_context.lower()
        assert len(item.detector_train) == 80
        assert len(item.detector_test) == 50
        assert item.anomaly_start_index == 30
