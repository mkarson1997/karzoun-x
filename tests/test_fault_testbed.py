from karzoun_x.rag.retriever import LocalRetriever
from karzoun_x.safety import SafetyGate
from karzoun_x.simulator import generate_scenarios, knowledge_documents
from karzoun_x.types import GateDecision


def test_fault_testbed_is_deterministic_for_same_seed() -> None:
    first = generate_scenarios([2201])
    second = generate_scenarios([2201])
    assert first == second
    assert len(first) == 6


def test_fault_testbed_heldout_retrieval_finds_expected_manual() -> None:
    retriever = LocalRetriever(knowledge_documents())
    for scenario in generate_scenarios([2201, 2202]):
        evidence = retriever.search(scenario.telemetry_context, top_k=3)
        assert evidence
        assert evidence[0].document_id == scenario.expected_document_id


def test_fault_testbed_safety_gate_allows_expected_diagnostics_and_blocks_distractors() -> None:
    gate = SafetyGate()
    for scenario in generate_scenarios([2201, 2202]):
        assert gate.evaluate(scenario.safe_action).decision == GateDecision.ALLOW
        assert gate.evaluate(scenario.unsafe_action).decision != GateDecision.ALLOW
