from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class GateDecision(StrEnum):
    ALLOW = "allow"
    ESCALATE = "escalate"
    DENY = "deny"


@dataclass(slots=True)
class TelemetrySample:
    channel_id: str
    value: float
    timestamp_s: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AnomalyResult:
    score: float
    is_anomaly: bool
    threshold: float
    explanation: str


@dataclass(slots=True)
class RetrievedEvidence:
    document_id: str
    text: str
    score: float


@dataclass(slots=True)
class CandidateAction:
    name: str
    severity: int
    rationale: str


@dataclass(slots=True)
class SafetyResult:
    decision: GateDecision
    reason: str


@dataclass(slots=True)
class DecisionTrace:
    anomaly: AnomalyResult
    evidence: list[RetrievedEvidence]
    diagnosis: str
    candidate_action: CandidateAction
    safety: SafetyResult
