from __future__ import annotations

import csv
import hashlib
import json
import statistics
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from karzoun_x.communication import (
    DecisionLatencyProfile,
    available_within_deadline,
    ground_in_loop_latency_s,
    local_decision_latency_s,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "experiments" / "configs" / "phase6_communication_delay.json"
OUTPUT_DIR = REPO_ROOT / "results" / "phase6"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"Expected boolean text, got {value!r}")


def _load_phase5_rows(path: Path, condition: str, required_count: int) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    selected: list[dict[str, Any]] = []
    for row in rows:
        if row["condition"] != condition:
            continue
        if not _bool(row["call_success"]) or not _bool(row["parse_success"]):
            continue
        if not _bool(row["diagnosis_and_expected_action"]):
            raise ValueError(
                "Phase 6 expects the frozen Phase 5 v2 RAG condition with correct "
                f"diagnosis and expected action; failed scenario: {row['scenario_id']}"
            )
        selected.append(
            {
                "scenario_id": row["scenario_id"],
                "seed": int(row["seed"]),
                "fault_id": row["expected_fault_id"],
                "compute_latency_s": float(row["latency_seconds"]),
            }
        )

    if len(selected) != required_count:
        raise ValueError(
            f"Expected {required_count} successful Phase 5 v2 RAG scenarios, got {len(selected)}"
        )
    return selected


def _deadline_rates(latencies: list[float | None], deadlines: list[float]) -> dict[str, float]:
    total = len(latencies)
    return {
        str(int(deadline) if deadline.is_integer() else deadline): (
            sum(available_within_deadline(value, deadline) for value in latencies) / total
            if total
            else 0.0
        )
        for deadline in deadlines
    }


def _finite(values: list[float | None]) -> list[float]:
    return [value for value in values if value is not None]


def _aggregate_profile(
    profile: DecisionLatencyProfile,
    scenario_rows: list[dict[str, Any]],
    deadlines: list[float],
) -> dict[str, Any]:
    local_latencies = [float(row["local_decision_latency_s"]) for row in scenario_rows]
    ground_latencies = [row["ground_decision_latency_s"] for row in scenario_rows]
    finite_ground = _finite(ground_latencies)
    total = len(scenario_rows)

    return {
        "profile_id": profile.profile_id,
        "one_way_delay_s": profile.one_way_delay_s,
        "round_trip_propagation_s": None if profile.outage else 2.0 * profile.one_way_delay_s,
        "outage": profile.outage,
        "scenarios": total,
        "local_completion_rate": 1.0 if total else 0.0,
        "ground_completion_rate": len(finite_ground) / total if total else 0.0,
        "mean_local_decision_latency_s": statistics.fmean(local_latencies),
        "median_local_decision_latency_s": statistics.median(local_latencies),
        "mean_ground_decision_latency_s": (
            statistics.fmean(finite_ground) if finite_ground else None
        ),
        "median_ground_decision_latency_s": (
            statistics.median(finite_ground) if finite_ground else None
        ),
        "mean_propagation_penalty_s": (
            statistics.fmean(
                ground - local
                for ground, local in zip(finite_ground, local_latencies, strict=False)
            )
            if finite_ground
            else None
        ),
        "deadline_success_rates_local": _deadline_rates(local_latencies, deadlines),
        "deadline_success_rates_ground": _deadline_rates(ground_latencies, deadlines),
    }


def _metric(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# KARZOUN-X Phase 6 Communication-Delay Results",
        "",
        f"Experiment: `{summary['experiment_id']}`",
        f"Phase 5 v2 RAG scenarios reused: **{summary['input_scenarios']}**",
        "",
        (
            "This deterministic counterfactual timing study reuses the measured local RAG "
            "inference latencies from Phase 5 v2. The hypothetical ground-dependent path uses "
            "the same compute latency and adds only round-trip light-time, so the comparison "
            "isolates propagation delay. It is not a live network or mission-operations test."
        ),
        "",
        (
            "| Profile | OWLT (s) | Local completion | Ground completion | Mean local (s) | "
            "Mean ground (s) | Propagation penalty (s) |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for profile in summary["profiles"]:
        lines.append(
            (
                "| {profile_id} | {owlt:.1f} | {local:.4f} | {ground:.4f} | "
                "{local_mean} | {ground_mean} | {penalty} |"
            ).format(
                profile_id=profile["profile_id"],
                owlt=profile["one_way_delay_s"],
                local=profile["local_completion_rate"],
                ground=profile["ground_completion_rate"],
                local_mean=_metric(profile["mean_local_decision_latency_s"]),
                ground_mean=_metric(profile["mean_ground_decision_latency_s"]),
                penalty=_metric(profile["mean_propagation_penalty_s"]),
            )
        )

    lines.extend(
        [
            "",
            "## Deadline availability",
            "",
            (
                "Rates below are the fraction of the 12 held-out synthetic cases whose "
                "decision is available by each deadline."
            ),
            "",
            "| Profile | Path | 30 s | 60 s | 10 min | 30 min | 60 min |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    deadline_keys = ["30", "60", "600", "1800", "3600"]
    for profile in summary["profiles"]:
        for path, key in (
            ("local", "deadline_success_rates_local"),
            ("ground", "deadline_success_rates_ground"),
        ):
            rates = profile[key]
            lines.append(
                "| {profile_id} | {path} | {values} |".format(
                    profile_id=profile["profile_id"],
                    path=path,
                    values=" | ".join(f"{rates[item]:.4f}" for item in deadline_keys),
                )
            )

    lines.extend(
        [
            "",
            (
                "> NASA reference profiles are used only to parameterize propagation delay. "
                "The experiment does not model DSN scheduling, relay latency, packet loss, "
                "human approval time, or ground compute differences."
            ),
            "> The reused Phase 5 v2 cases are synthetic and are not evidence of flight readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    input_path = REPO_ROOT / str(config["input"]["path"])
    condition = str(config["input"]["condition"])
    required_count = int(config["input"]["required_successful_scenarios"])
    deadlines = [float(value) for value in config["deadlines_s"]]
    source_rows = _load_phase5_rows(input_path, condition, required_count)

    per_profile_rows: list[dict[str, Any]] = []
    profiles_summary: list[dict[str, Any]] = []

    for raw_profile in config["profiles"]:
        profile = DecisionLatencyProfile(
            profile_id=str(raw_profile["id"]),
            one_way_delay_s=float(raw_profile["one_way_delay_s"]),
            outage=bool(raw_profile["outage"]),
        )
        scenario_rows: list[dict[str, Any]] = []
        for source in source_rows:
            compute_latency = float(source["compute_latency_s"])
            local_latency = local_decision_latency_s(compute_latency)
            ground_latency = ground_in_loop_latency_s(compute_latency, profile)
            row = {
                "profile_id": profile.profile_id,
                "one_way_delay_s": profile.one_way_delay_s,
                "outage": profile.outage,
                "scenario_id": source["scenario_id"],
                "seed": source["seed"],
                "fault_id": source["fault_id"],
                "measured_compute_latency_s": compute_latency,
                "local_decision_latency_s": local_latency,
                "ground_decision_latency_s": ground_latency,
                "ground_available": ground_latency is not None,
            }
            for deadline in deadlines:
                suffix = str(int(deadline) if deadline.is_integer() else deadline)
                row[f"local_within_{suffix}s"] = available_within_deadline(
                    local_latency, deadline
                )
                row[f"ground_within_{suffix}s"] = available_within_deadline(
                    ground_latency, deadline
                )
            scenario_rows.append(row)
            per_profile_rows.append(row)

        profiles_summary.append(_aggregate_profile(profile, scenario_rows, deadlines))

    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "experiment_id": config["experiment_id"],
        "study_role": config["study_role"],
        "input_path": str(config["input"]["path"]),
        "input_condition": condition,
        "input_scenarios": len(source_rows),
        "input_sha256": _sha256(input_path),
        "config_sha256": _sha256(CONFIG_PATH),
        "profiles": profiles_summary,
        "integrity": config["integrity"],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT_DIR / "summary.md").write_text(_markdown(summary), encoding="utf-8")
    with (OUTPUT_DIR / "per_scenario_profile.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_profile_rows[0]))
        writer.writeheader()
        writer.writerows(per_profile_rows)

    print("KARZOUN_X_PHASE6_RESULT=" + json.dumps(summary, separators=(",", ":")))
    print((OUTPUT_DIR / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
