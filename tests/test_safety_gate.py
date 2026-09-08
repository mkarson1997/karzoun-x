from karzoun_x.safety import SafetyGate
from karzoun_x.types import CandidateAction, GateDecision


def test_safe_read_only_action_is_allowed() -> None:
    result = SafetyGate().evaluate(
        CandidateAction("run_read_only_diagnostic", 1, "collect evidence")
    )
    assert result.decision is GateDecision.ALLOW


def test_explicitly_denied_action_is_denied() -> None:
    result = SafetyGate().evaluate(CandidateAction("fire_thruster", 1, "test"))
    assert result.decision is GateDecision.DENY


def test_unknown_action_fails_closed() -> None:
    result = SafetyGate().evaluate(CandidateAction("unknown_actuator_command", 1, "test"))
    assert result.decision is GateDecision.ESCALATE
