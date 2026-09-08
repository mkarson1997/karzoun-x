# Research Integrity and Responsible Use

KARZOUN-X is a research prototype for studying AI-assisted fault diagnosis in simulated or historical spacecraft telemetry settings.

## Non-negotiable rules

1. **No fabricated results.** Numbers in papers, README files, posts, or presentations must come from reproducible experiments or be clearly marked as illustrative examples.
2. **No false institutional affiliation.** The project must not imply employment by, endorsement from, collaboration with, or approval by NASA, JPL, ESA, a university, or any other institution unless formally true and documented.
3. **No flight-readiness claim.** Prototype behavior on historical or simulated data does not establish flight safety, reliability, or certification.
4. **Traceable evidence.** Where the LLM makes a diagnostic claim, experiments should preserve the retrieved evidence and model output needed for auditing.
5. **Safety separation.** Probabilistic reasoning is advisory. Deterministic constraints govern whether an action may proceed in the research simulator.
6. **Reproducibility.** Experimental configuration, code version, dataset provenance, random seeds, model identifiers, and hardware/runtime details should be recorded.
7. **Negative results are results.** Failures, regressions, and null findings should not be hidden merely because they weaken the hypothesis.

## Responsible-use boundary

Do not deploy this code on real spacecraft, robots, industrial controllers, vehicles, medical devices, or other safety-critical systems. Any real-world deployment would require domain-specific engineering, verification, validation, cybersecurity review, certification, and authorized operational oversight.
