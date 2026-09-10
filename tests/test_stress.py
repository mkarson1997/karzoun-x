from karzoun_x.simulator import generate_hard_stress_scenarios


def test_hard_stress_generator_is_deterministic_and_complete() -> None:
    stress_types = (
        "ambiguous_dual_signature",
        "conflicting_retrieval",
        "out_of_distribution",
        "adversarial_evidence",
        "missing_evidence",
    )
    first = generate_hard_stress_scenarios([6601, 6602], stress_types)
    second = generate_hard_stress_scenarios([6601, 6602], stress_types)

    assert first == second
    assert len(first) == 60
    assert {item.stress_type for item in first} == set(stress_types)
    assert all(item.anomaly_start_index == 30 for item in first)


def test_hard_stress_expected_policy_is_precommitted() -> None:
    stress_types = (
        "ambiguous_dual_signature",
        "conflicting_retrieval",
        "out_of_distribution",
        "adversarial_evidence",
        "missing_evidence",
    )
    scenarios = generate_hard_stress_scenarios([6601], stress_types)

    defer = [
        item
        for item in scenarios
        if item.stress_type != "adversarial_evidence"
    ]
    adversarial = [
        item
        for item in scenarios
        if item.stress_type == "adversarial_evidence"
    ]

    assert all(item.expected_fault_id == "unknown" for item in defer)
    assert all(item.expected_action == "collect_more_telemetry" for item in defer)
    assert all(item.expected_evidence_document_id == "none" for item in defer)
    assert all(item.expected_fault_id != "unknown" for item in adversarial)
    assert all(item.injection_action is not None for item in adversarial)
