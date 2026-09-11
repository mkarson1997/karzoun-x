from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from karzoun_x.anomaly_detection.stability_aware import StabilityAwareDetector
from karzoun_x.rag.retriever import LocalRetriever
from karzoun_x.safety import EpistemicEvidenceGate, EpistemicGateConfig, SafetyGate
from karzoun_x.simulator import knowledge_documents
from karzoun_x.simulator.fault_testbed import fault_definitions
from karzoun_x.types import GateDecision
from run_phase11_epistemic_gate import (
    _call_ollama,
    _candidate_action,
    _clean_records,
    _evidence_for_record,
    _hard_records,
    _parse_response,
    _policy_conformant,
    _prompt,
    _schema,
    _token_rate,
)
from run_phase8b_resource_instrumentation import ResourceSamplerV2, _resource_summary

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "experiments/configs/phase12_model_resource_ablation.json"
OUTPUT_DIR = REPO_ROOT / "results/phase12"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run KARZOUN-X Phase 12 model/resource ablation.")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    return parser.parse_args()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _p95(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(math.ceil(0.95 * len(ordered)) - 1, 0)
    return ordered[index]


def _rate(rows: list[dict[str, Any]], key: str) -> float:
    return sum(bool(row[key]) for row in rows) / len(rows) if rows else 0.0


def _gib(value: float | None) -> float | None:
    return None if value is None else value / (1024**3)


def _metric(value: float | None, digits: int = 4) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def _unload_model(client: httpx.Client, base_url: str, model: str) -> None:
    try:
        response = client.post(
            f"{base_url}/api/generate",
            json={"model": model, "keep_alive": 0, "stream": False},
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return


def _model_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [float(row["latency_seconds"]) for row in rows if row["call_success"]]
    warm_latencies = latencies[1:] if len(latencies) > 1 else []
    speeds = [
        float(row["generation_tokens_per_second"])
        for row in rows
        if row["generation_tokens_per_second"] not in (None, "")
    ]
    known = [row for row in rows if row["expected_fault_id"] != "unknown"]
    defer = [row for row in rows if row["expected_fault_id"] == "unknown"]
    return {
        "scenarios": len(rows),
        "parse_success_rate": _rate(rows, "parse_success"),
        "baseline_policy_conformant_rate": _rate(rows, "baseline_policy_conformant"),
        "gated_policy_conformant_rate": _rate(rows, "gated_policy_conformant"),
        "known_case_preservation_rate": _rate(known, "gated_policy_conformant"),
        "required_defer_capture_rate": _rate(defer, "gated_policy_conformant"),
        "epistemic_defer_rate": _rate(rows, "epistemic_deferred"),
        "mean_latency_seconds": _mean(latencies),
        "median_latency_seconds": _median(latencies),
        "p95_latency_seconds": _p95(latencies),
        "cold_start_latency_seconds": latencies[0] if latencies else None,
        "warm_mean_latency_seconds": _mean(warm_latencies),
        "mean_generation_tokens_per_second": _mean(speeds),
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# KARZOUN-X Phase 12 Model/Resource Ablation",
        "",
        f"Experiment: `{summary['experiment_id']}`",
        f"Synthetic cases per model: **{summary['scenarios_per_model']}**",
        "",
        "| Model | Gated policy | Known preserve | Required defer | Warm mean s | tok/s | Peak RSS GiB | Model GiB | VRAM GiB |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, item in summary["by_model"].items():
        model = item["model_metrics"]
        resource = item["resource_metrics"]
        lines.append(
            f"| {label} (`{item['model_name']}`) | "
            f"{_metric(model['gated_policy_conformant_rate'])} | "
            f"{_metric(model['known_case_preservation_rate'])} | "
            f"{_metric(model['required_defer_capture_rate'])} | "
            f"{_metric(model['warm_mean_latency_seconds'], 3)} | "
            f"{_metric(model['mean_generation_tokens_per_second'], 3)} | "
            f"{_metric(_gib(resource['peak_model_process_family_rss_bytes']), 3)} | "
            f"{_metric(_gib(resource['peak_ollama_reported_model_size_bytes']), 3)} | "
            f"{_metric(_gib(resource['peak_ollama_reported_vram_size_bytes']), 3)} |"
        )
    lines.extend(
        [
            "",
            (
                "> Phase 12 compares frozen local model choices on the same synthetic "
                "scenarios and the same Phase 11 epistemic gate."
            ),
            (
                "> Measurements come from one host. Ollama-reported VRAM allocation is "
                "not a substitute for independent flight-hardware power/thermal testing."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = _parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    base_url = str(args.base_url).rstrip("/")
    seed = int(config["testbed"]["heldout_seed"])
    records = _clean_records([seed]) + _hard_records([seed])
    expected_count = int(config["testbed"]["scenarios_per_model"])
    if len(records) != expected_count:
        raise ValueError(f"Expected {expected_count} scenarios, got {len(records)}")

    documents = knowledge_documents()
    definitions = fault_definitions()
    fault_classes = sorted(item.fault_id for item in definitions)
    schema = _schema(fault_classes)
    retriever = LocalRetriever(documents)
    gate_config = config["epistemic_gate"]
    epistemic_gate = EpistemicEvidenceGate(
        documents,
        EpistemicGateConfig(
            minimum_top_support=float(gate_config["minimum_top_support"]),
            minimum_top_margin=float(gate_config["minimum_top_margin"]),
            require_provided_top_match=bool(gate_config["require_provided_top_match"]),
            untrusted_document_prefixes=tuple(gate_config["untrusted_document_prefixes"]),
        ),
    )
    action_gate = SafetyGate()
    generation = config["generation"]
    resource_config = config["resource_sampling"]
    timeout = float(generation["timeout_seconds"])
    threshold = 3.5

    all_rows: list[dict[str, Any]] = []
    all_raw: list[dict[str, Any]] = []
    all_resource_samples: list[dict[str, Any]] = []
    by_model: dict[str, Any] = {}

    with httpx.Client(timeout=timeout) as client:
        tags = client.get(f"{base_url}/api/tags")
        tags.raise_for_status()
        available = {
            str(item.get("name", ""))
            for item in tags.json().get("models", [])
            if isinstance(item, dict)
        }
        missing = [
            str(item["model_name"])
            for item in config["models"]
            if str(item["model_name"]) not in available
        ]
        if missing:
            raise RuntimeError(
                "Required Phase 12 Ollama model(s) missing: " + ", ".join(missing)
            )

        total_calls = expected_count * len(config["models"])
        global_index = 0
        for model_spec in config["models"]:
            label = str(model_spec["label"])
            model = str(model_spec["model_name"])
            _unload_model(client, base_url, model)
            time.sleep(1.0)
            model_rows: list[dict[str, Any]] = []
            sampler = ResourceSamplerV2(
                interval_seconds=float(resource_config["interval_seconds"]),
                process_name_tokens=tuple(resource_config["process_name_tokens"]),
                base_url=base_url,
                model=model,
            )
            sampler.start()
            try:
                for local_index, record in enumerate(records, start=1):
                    global_index += 1
                    detector = StabilityAwareDetector(threshold=threshold).fit(
                        list(record["detector_train"])
                    )
                    detector_triggered = any(
                        detector.predict_one(value).is_anomaly
                        for value in record["detector_test"][record["anomaly_start_index"] :]
                    )
                    evidence = _evidence_for_record(record, retriever)
                    prompt = _prompt(str(record["telemetry"]), evidence, fault_classes)
                    print(
                        f"[Phase 12] {global_index}/{total_calls} START :: {label} :: {record['scenario_id']}",
                        flush=True,
                    )
                    started_at = datetime.now(UTC).isoformat()
                    raw_text = ""
                    payload: dict[str, Any] = {}
                    parsed: dict[str, str] = {}
                    latency = 0.0
                    call_success = False
                    parse_success = False
                    error = ""
                    if detector_triggered:
                        try:
                            raw_text, payload, latency = _call_ollama(
                                client,
                                base_url,
                                model,
                                prompt,
                                schema,
                                float(generation["temperature"]),
                                int(generation["num_predict"]),
                            )
                            call_success = True
                            parsed = _parse_response(raw_text)
                            parse_success = True
                        except (httpx.HTTPError, json.JSONDecodeError, ValueError) as exc:
                            error = f"{type(exc).__name__}: {exc}"
                    else:
                        error = "Detector did not trigger; model call skipped."

                    proposed_fault = str(parsed.get("fault_id", "")).strip()
                    proposed_action = str(parsed.get("action", "")).strip()
                    proposed_evidence = str(parsed.get("evidence_document_id", "")).strip()
                    baseline_result = action_gate.evaluate(_candidate_action(proposed_action)) if parse_success else None
                    baseline_allowed = bool(
                        baseline_result and baseline_result.decision == GateDecision.ALLOW
                    )
                    baseline_conformant = bool(
                        parse_success
                        and _policy_conformant(
                            str(record["expected_fault_id"]),
                            str(record["expected_action"]),
                            str(record["expected_evidence_document_id"]),
                            proposed_fault,
                            proposed_action,
                            proposed_evidence,
                            baseline_allowed,
                        )
                    )

                    epistemic = epistemic_gate.evaluate(str(record["telemetry"]), evidence)
                    if parse_success and epistemic.sufficient:
                        final_fault = proposed_fault
                        final_action = proposed_action
                        final_evidence = proposed_evidence
                    else:
                        final_fault = "unknown"
                        final_action = "collect_more_telemetry"
                        final_evidence = "none"
                    final_result = action_gate.evaluate(_candidate_action(final_action))
                    final_allowed = final_result.decision == GateDecision.ALLOW
                    gated_conformant = bool(
                        detector_triggered
                        and _policy_conformant(
                            str(record["expected_fault_id"]),
                            str(record["expected_action"]),
                            str(record["expected_evidence_document_id"]),
                            final_fault,
                            final_action,
                            final_evidence,
                            final_allowed,
                        )
                    )

                    row = {
                        "model_label": label,
                        "model_name": model,
                        "scenario_id": record["scenario_id"],
                        "seed": record["seed"],
                        "family": record["family"],
                        "expected_fault_id": record["expected_fault_id"],
                        "expected_action": record["expected_action"],
                        "expected_evidence_document_id": record["expected_evidence_document_id"],
                        "detector_triggered": detector_triggered,
                        "call_success": call_success,
                        "parse_success": parse_success,
                        "error": error,
                        "proposed_fault_id": proposed_fault,
                        "proposed_action": proposed_action,
                        "proposed_evidence_document_id": proposed_evidence,
                        "baseline_policy_conformant": baseline_conformant,
                        "epistemic_sufficient": epistemic.sufficient,
                        "epistemic_deferred": not epistemic.sufficient,
                        "epistemic_reason": epistemic.reason,
                        "epistemic_top_score": epistemic.top_score,
                        "epistemic_score_margin": epistemic.score_margin,
                        "final_fault_id": final_fault,
                        "final_action": final_action,
                        "final_evidence_document_id": final_evidence,
                        "gated_policy_conformant": gated_conformant,
                        "latency_seconds": latency,
                        "generation_tokens_per_second": _token_rate(payload),
                        "eval_count": payload.get("eval_count"),
                        "prompt_eval_count": payload.get("prompt_eval_count"),
                    }
                    model_rows.append(row)
                    all_rows.append(row)
                    all_raw.append(
                        {
                            "model_label": label,
                            "model_name": model,
                            "scenario_id": record["scenario_id"],
                            "family": record["family"],
                            "started_at_utc": started_at,
                            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                            "provided_evidence_document_ids": [item.document_id for item in evidence],
                            "raw_response": raw_text,
                            "raw_thinking": str(payload.get("thinking", "")),
                            "parsed_response": parsed,
                            "epistemic_gate": {
                                "sufficient": epistemic.sufficient,
                                "reason": epistemic.reason,
                                "top_score": epistemic.top_score,
                                "second_score": epistemic.second_score,
                                "score_margin": epistemic.score_margin,
                            },
                        }
                    )
                    print(
                        f"[Phase 12] {global_index}/{total_calls} DONE :: {label} :: "
                        f"gated={gated_conformant} :: {latency:.2f}s",
                        flush=True,
                    )
            finally:
                sampler.stop()

            for sample in sampler.samples:
                all_resource_samples.append(
                    {"model_label": label, "model_name": model, **sample}
                )
            by_model[label] = {
                "model_name": model,
                "model_metrics": _model_metrics(model_rows),
                "resource_metrics": _resource_summary(sampler.samples),
            }
            _unload_model(client, base_url, model)
            time.sleep(1.0)

    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "experiment_id": config["experiment_id"],
        "study_role": config["study_role"],
        "config_sha256": _sha256(CONFIG_PATH),
        "scenarios_per_model": expected_count,
        "total_model_calls": len(all_rows),
        "by_model": by_model,
        "integrity": config["integrity"],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "summary.md").write_text(_markdown(summary), encoding="utf-8")
    with (OUTPUT_DIR / "per_response.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)
    with (OUTPUT_DIR / "raw_responses.jsonl").open("w", encoding="utf-8") as handle:
        for item in all_raw:
            handle.write(json.dumps(item, sort_keys=True) + "\n")
    if all_resource_samples:
        with (OUTPUT_DIR / "resource_samples.csv").open("w", encoding="utf-8", newline="") as handle:
            fieldnames = sorted({key for row in all_resource_samples for key in row})
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_resource_samples)

    print("KARZOUN_X_PHASE12_RESULT=" + json.dumps(summary, separators=(",", ":")))
    print(_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
