from __future__ import annotations

from karzoun_x.anomaly_detection import RobustZScoreDetector
from karzoun_x.rag.retriever import LocalRetriever
from karzoun_x.safety import SafetyGate
from karzoun_x.types import CandidateAction, DecisionTrace


class KarzounXPipeline:
    def __init__(
        self,
        detector: RobustZScoreDetector,
        retriever: LocalRetriever,
        safety_gate: SafetyGate,
    ) -> None:
        self.detector = detector
        self.retriever = retriever
        self.safety_gate = safety_gate

    def analyze(
        self,
        value: float,
        query: str,
        diagnosis: str,
        action: CandidateAction,
    ) -> DecisionTrace:
        anomaly = self.detector.predict_one(value)
        evidence = self.retriever.search(query)
        safety = self.safety_gate.evaluate(action)
        return DecisionTrace(
            anomaly=anomaly,
            evidence=evidence,
            diagnosis=diagnosis,
            candidate_action=action,
            safety=safety,
        )
