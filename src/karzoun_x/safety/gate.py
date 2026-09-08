from __future__ import annotations

from dataclasses import dataclass, field

from karzoun_x.types import CandidateAction, GateDecision, SafetyResult


@dataclass(slots=True)
class SafetyGate:
    """Deterministic allow/deny/escalate policy for simulator actions."""

    max_authorized_severity: int = 2
    explicitly_denied_actions: set[str] = field(
        default_factory=lambda: {
            "disable_life_support",
            "fire_thruster",
            "deploy_pyrotechnic",
            "erase_flight_software",
            "override_thermal_protection",
        }
    )
    explicitly_safe_actions: set[str] = field(
        default_factory=lambda: {
            "collect_more_telemetry",
            "increase_logging",
            "request_subsystem_status",
            "run_read_only_diagnostic",
        }
    )

    def evaluate(self, action: CandidateAction) -> SafetyResult:
        normalized = action.name.strip().lower()

        if normalized in self.explicitly_denied_actions:
            return SafetyResult(GateDecision.DENY, "Action is explicitly denied by policy.")

        if normalized in self.explicitly_safe_actions and action.severity <= self.max_authorized_severity:
            return SafetyResult(GateDecision.ALLOW, "Low-risk diagnostic action allowed by policy.")

        if action.severity > self.max_authorized_severity:
            return SafetyResult(
                GateDecision.ESCALATE,
                "Action severity exceeds autonomous authorization threshold.",
            )

        return SafetyResult(
            GateDecision.ESCALATE,
            "Unknown action requires explicit review; policy fails closed.",
        )
