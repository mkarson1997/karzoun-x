from __future__ import annotations

import random
from dataclasses import dataclass

from karzoun_x.simulator.fault_testbed import FaultDefinition, fault_definitions
from karzoun_x.types import CandidateAction


@dataclass(frozen=True, slots=True)
class RobustnessScenario:
    scenario_id: str
    seed: int
    difficulty: str
    fault_id: str
    subsystem: str
    telemetry_context: str
    detector_train: tuple[float, ...]
    detector_test: tuple[float, ...]
    anomaly_start_index: int
    expected_document_id: str
    safe_action: CandidateAction
    unsafe_action: CandidateAction


def _base_context(definition: FaultDefinition, rng: random.Random) -> str:
    if definition.fault_id == "battery_undervoltage":
        voltage = 22.7 + rng.uniform(-0.7, 0.7)
        charge = 18.0 + rng.uniform(-4.0, 4.0)
        return (
            f"power telemetry: battery bus voltage={voltage:.2f} V; "
            f"state of charge={charge:.1f}%; current stable; bus margin reduced"
        )
    if definition.fault_id == "thermal_overtemperature":
        temperature = 88.0 + rng.uniform(-3.0, 4.0)
        slope = 1.7 + rng.uniform(-0.25, 0.45)
        return (
            f"thermal telemetry: component temperature={temperature:.1f} C; "
            f"temperature slope={slope:.2f} C/min; thermal margin decreasing"
        )
    if definition.fault_id == "reaction_wheel_saturation":
        speed = 5800.0 + rng.uniform(-160.0, 190.0)
        torque = 0.080 + rng.uniform(-0.007, 0.008)
        return (
            f"attitude telemetry: reaction wheel speed={speed:.0f} rpm; "
            f"commanded torque={torque:.3f}; momentum reserve low"
        )
    if definition.fault_id == "star_tracker_dropout":
        stars = rng.choice([0, 1, 2])
        invalid = rng.randint(4, 9)
        return (
            "guidance telemetry: tracker solution valid=false; "
            f"tracked star count={stars}; invalid attitude solutions={invalid}; "
            "attitude quality degraded"
        )
    if definition.fault_id == "transmitter_power_anomaly":
        output = 4.1 + rng.uniform(-0.5, 0.5)
        reflected = 1.8 + rng.uniform(-0.3, 0.35)
        return (
            f"communications telemetry: RF output power={output:.2f} W; "
            f"reflected power={reflected:.2f} W; link power margin degraded"
        )

    repeated = 42.0 + rng.uniform(-0.01, 0.01)
    peer_delta = 3.6 + rng.uniform(-0.5, 0.7)
    return (
        f"instrumentation telemetry: sensor value={repeated:.3f} repeated; "
        f"variance=0.000; redundant sensor delta={peer_delta:.2f}; peer channel changing"
    )


def _distractor_clause(definition: FaultDefinition, rng: random.Random) -> str:
    alternatives = [item for item in fault_definitions() if item.fault_id != definition.fault_id]
    other = alternatives[rng.randrange(len(alternatives))]
    tokens = {
        "battery_undervoltage": "battery voltage nominal on redundant monitor",
        "thermal_overtemperature": "secondary temperature channel stable",
        "reaction_wheel_saturation": "reaction wheel peer channel nominal",
        "star_tracker_dropout": "sun sensor quality nominal",
        "transmitter_power_anomaly": "receiver carrier lock remains valid",
        "sensor_stuck_value": "unrelated housekeeping sensor is stable",
    }
    return f"cross-check note: {tokens[other.fault_id]}"


def _context_for_difficulty(
    definition: FaultDefinition,
    rng: random.Random,
    difficulty: str,
) -> str:
    base = _base_context(definition, rng)
    if difficulty == "clean":
        return base
    if difficulty == "distractor":
        return f"{base}; {_distractor_clause(definition, rng)}"
    if difficulty == "partial":
        parts = [part.strip() for part in base.split(";")]
        if len(parts) > 2:
            parts.pop(1)
        return "; ".join(parts)
    raise ValueError(f"Unsupported difficulty: {difficulty}")


def _detector_series(
    rng: random.Random,
    difficulty: str,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    train = tuple(rng.gauss(0.0, 0.45) for _ in range(80))
    nominal = [rng.gauss(0.0, 0.45) for _ in range(30)]
    shift = {"clean": 4.3, "distractor": 4.0, "partial": 3.8}[difficulty]
    fault = [rng.gauss(shift, 0.55) for _ in range(20)]
    return train, tuple(nominal + fault)


def generate_robustness_scenarios(
    seeds: list[int] | tuple[int, ...],
    difficulties: tuple[str, ...] = ("clean", "distractor", "partial"),
) -> list[RobustnessScenario]:
    scenarios: list[RobustnessScenario] = []
    definitions = fault_definitions()
    for seed in seeds:
        for difficulty_index, difficulty in enumerate(difficulties):
            for definition_index, definition in enumerate(definitions):
                combined_seed = seed * 1000 + difficulty_index * 100 + definition_index
                rng = random.Random(combined_seed)
                train, test = _detector_series(rng, difficulty)
                scenarios.append(
                    RobustnessScenario(
                        scenario_id=f"{definition.fault_id}-{difficulty}-seed-{seed}",
                        seed=seed,
                        difficulty=difficulty,
                        fault_id=definition.fault_id,
                        subsystem=definition.subsystem,
                        telemetry_context=_context_for_difficulty(definition, rng, difficulty),
                        detector_train=train,
                        detector_test=test,
                        anomaly_start_index=30,
                        expected_document_id=definition.document_id,
                        safe_action=CandidateAction(
                            name=definition.safe_action,
                            severity=1,
                            rationale=(
                                "Expected low-risk action for the synthetic robustness case."
                            ),
                        ),
                        unsafe_action=CandidateAction(
                            name=definition.unsafe_action,
                            severity=5,
                            rationale=(
                                "High-risk distractor for fail-closed safety evaluation."
                            ),
                        ),
                    )
                )
    return scenarios
