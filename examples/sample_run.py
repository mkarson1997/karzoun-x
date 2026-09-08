from karzoun_x.anomaly_detection import RobustZScoreDetector
from karzoun_x.rag.retriever import KnowledgeDocument, LocalRetriever
from karzoun_x.safety import SafetyGate
from karzoun_x.types import CandidateAction


def main() -> None:
    detector = RobustZScoreDetector().fit([0.0, 0.01, -0.01, 0.0, 0.02, -0.02])
    anomaly = detector.predict_one(0.4)

    retriever = LocalRetriever(
        [
            KnowledgeDocument(
                "example",
                (
                    "For an unexplained telemetry excursion, first collect corroborating "
                    "telemetry and run read-only diagnostics."
                ),
            )
        ]
    )
    evidence = retriever.search("telemetry excursion diagnostics")

    action = CandidateAction("run_read_only_diagnostic", 1, "collect evidence")
    safety = SafetyGate().evaluate(action)

    print(anomaly)
    print(evidence)
    print(safety)


if __name__ == "__main__":
    main()
