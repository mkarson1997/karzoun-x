from __future__ import annotations

import argparse
import json

from karzoun_x.anomaly_detection import RobustZScoreDetector
from karzoun_x.config import Settings
from karzoun_x.rag.retriever import KnowledgeDocument, LocalRetriever
from karzoun_x.reasoning import OllamaReasoner
from karzoun_x.safety import SafetyGate
from karzoun_x.types import CandidateAction


def _demo() -> int:
    baseline = [1.00, 1.02, 0.99, 1.01, 1.00, 0.98, 1.03, 1.01]
    detector = RobustZScoreDetector(threshold=3.5).fit(baseline)
    result = detector.predict_one(1.30)

    retriever = LocalRetriever(
        [
            KnowledgeDocument(
                "thermal-001",
                "A sudden thermal sensor excursion should first trigger verification using adjacent sensors and read-only subsystem diagnostics before any control action.",
            ),
            KnowledgeDocument(
                "power-001",
                "Power-bus anomalies require corroboration across voltage and current telemetry before isolation decisions are considered.",
            ),
        ]
    )
    evidence = retriever.search("thermal sensor excursion diagnostic")

    gate = SafetyGate(max_authorized_severity=2)
    action = CandidateAction(
        name="run_read_only_diagnostic",
        severity=1,
        rationale="Collect corroborating evidence before any consequential action.",
    )
    safety = gate.evaluate(action)

    payload = {
        "anomaly": {
            "score": round(result.score, 3),
            "is_anomaly": result.is_anomaly,
            "threshold": result.threshold,
        },
        "retrieved_evidence": [item.document_id for item in evidence],
        "candidate_action": action.name,
        "safety_decision": safety.decision.value,
        "safety_reason": safety.reason,
        "note": "Synthetic demonstration only; not a research result.",
    }
    print(json.dumps(payload, indent=2))
    return 0


def _ollama_check() -> int:
    settings = Settings()
    reasoner = OllamaReasoner(
        settings.ollama_url,
        settings.ollama_model,
        settings.request_timeout_seconds,
    )
    ok = reasoner.health()
    print(
        json.dumps(
            {
                "reachable": ok,
                "url": settings.ollama_url,
                "model": settings.ollama_model,
            },
            indent=2,
        )
    )
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="karzoun-x")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="Run a synthetic end-to-end demonstration.")
    sub.add_parser("ollama-check", help="Check the configured local Ollama endpoint.")
    args = parser.parse_args()

    if args.command == "demo":
        return _demo()
    if args.command == "ollama-check":
        return _ollama_check()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
