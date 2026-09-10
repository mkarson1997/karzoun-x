from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import statistics
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import psutil

from karzoun_x.anomaly_detection.stability_aware import StabilityAwareDetector
from karzoun_x.rag.retriever import LocalRetriever
from karzoun_x.safety import SafetyGate
from karzoun_x.simulator import generate_robustness_scenarios, knowledge_documents
from karzoun_x.types import GateDecision
from run_phase8_resource_benchmark import (
    _build_prompt,
    _call_ollama,
    _candidate_action,
    _gpu_identity,
    _nvidia_sample,
    _parse_response,
    _tokens_per_second,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "experiments" / "configs" / "phase8b_resource_instrumentation.json"
OUTPUT_DIR = REPO_ROOT / "results" / "phase8b"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run KARZOUN-X Phase 8B resource instrumentation.")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default=None)
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


def _numeric_samples(samples: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for sample in samples:
        value = sample.get(key)
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            values.append(float(value))
    return values


def _max(values: list[float]) -> float | None:
    return max(values) if values else None


def _ollama_ps_sample(client: httpx.Client, base_url: str, model: str) -> dict[str, Any]:
    result = {
        "ollama_reported_model_size_bytes": None,
        "ollama_reported_vram_size_bytes": None,
        "ollama_reported_expires_at": None,
    }
    try:
        response = client.get(f"{base_url}/api/ps")
        response.raise_for_status()
        models = response.json().get("models", [])
    except (httpx.HTTPError, ValueError, AttributeError):
        return result

    for item in models:
        if not isinstance(item, dict) or str(item.get("name", "")) != model:
            continue
        size = item.get("size")
        size_vram = item.get("size_vram")
        if isinstance(size, (int, float)):
            result["ollama_reported_model_size_bytes"] = int(size)
        if isinstance(size_vram, (int, float)):
            result["ollama_reported_vram_size_bytes"] = int(size_vram)
        expires_at = item.get("expires_at")
        if expires_at is not None:
            result["ollama_reported_expires_at"] = str(expires_at)
        break
    return result


@dataclass(slots=True)
class ResourceSamplerV2:
    interval_seconds: float
    process_name_tokens: tuple[str, ...]
    base_url: str
    model: str
    samples: list[dict[str, Any]] = field(default_factory=list)
    _stop: threading.Event = field(default_factory=threading.Event)
    _thread: threading.Thread | None = None
    _previous_cpu_times: dict[int, float] = field(default_factory=dict)
    _previous_timestamp: float | None = None

    def start(self) -> None:
        psutil.cpu_percent(interval=None)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=max(5.0, self.interval_seconds * 4))

    def _model_process_metrics(self, now: float) -> tuple[int, float, str]:
        logical_cpus = max(psutil.cpu_count(logical=True) or 1, 1)
        rss_bytes = 0
        current_cpu_times: dict[int, float] = {}
        matched: list[str] = []

        for process in psutil.process_iter(["pid", "name", "memory_info", "cpu_times", "cmdline"]):
            try:
                name = str(process.info["name"] or "")
                cmdline = " ".join(str(part) for part in (process.info["cmdline"] or []))
                haystack = f"{name} {cmdline}".lower()
                if not any(token in haystack for token in self.process_name_tokens):
                    continue
                memory_info = process.info["memory_info"]
                cpu_times = process.info["cpu_times"]
                pid = int(process.info["pid"])
                rss_bytes += int(memory_info.rss)
                current_cpu_times[pid] = float(cpu_times.user + cpu_times.system)
                matched.append(f"{pid}:{name}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError, TypeError):
                continue

        normalized_cpu = 0.0
        if self._previous_timestamp is not None:
            elapsed = max(now - self._previous_timestamp, 1e-9)
            cpu_delta = sum(
                max(value - self._previous_cpu_times.get(pid, value), 0.0)
                for pid, value in current_cpu_times.items()
            )
            normalized_cpu = 100.0 * cpu_delta / (elapsed * logical_cpus)

        self._previous_cpu_times = current_cpu_times
        self._previous_timestamp = now
        return rss_bytes, normalized_cpu, ";".join(sorted(matched))

    def _sample_once(self, client: httpx.Client) -> None:
        now = time.time()
        memory = psutil.virtual_memory()
        family_rss, family_cpu, matched = self._model_process_metrics(now)
        ollama_ps = _ollama_ps_sample(client, self.base_url, self.model)
        gpu = _nvidia_sample()
        self.samples.append(
            {
                "timestamp_utc": datetime.now(UTC).isoformat(),
                "timestamp_epoch_s": now,
                "system_cpu_percent": psutil.cpu_percent(interval=None),
                "system_memory_used_bytes": int(memory.used),
                "system_memory_percent": float(memory.percent),
                "model_process_family_rss_bytes": family_rss,
                "model_process_family_cpu_percent_normalized": family_cpu,
                "matched_model_processes": matched,
                **ollama_ps,
                **gpu,
            }
        )

    def _loop(self) -> None:
        with httpx.Client(timeout=2.0) as client:
            while not self._stop.is_set():
                self._sample_once(client)
                self._stop.wait(self.interval_seconds)


def _resource_summary(samples: list[dict[str, Any]]) -> dict[str, Any]:
    system_cpu = _numeric_samples(samples, "system_cpu_percent")
    family_cpu = _numeric_samples(samples, "model_process_family_cpu_percent_normalized")
    system_memory = _numeric_samples(samples, "system_memory_used_bytes")
    family_rss = _numeric_samples(samples, "model_process_family_rss_bytes")
    model_size = _numeric_samples(samples, "ollama_reported_model_size_bytes")
    vram_size = _numeric_samples(samples, "ollama_reported_vram_size_bytes")
    gpu_util = _numeric_samples(samples, "gpu_utilization_percent")
    gpu_memory = _numeric_samples(samples, "gpu_memory_used_mib")
    gpu_power = _numeric_samples(samples, "gpu_power_watts")
    matched = sorted(
        {
            token
            for sample in samples
            for token in str(sample.get("matched_model_processes", "")).split(";")
            if token
        }
    )
    return {
        "samples": len(samples),
        "mean_system_cpu_percent": _mean(system_cpu),
        "peak_system_cpu_percent": _max(system_cpu),
        "mean_model_process_family_cpu_percent_normalized": _mean(family_cpu),
        "peak_model_process_family_cpu_percent_normalized": _max(family_cpu),
        "peak_system_memory_used_bytes": _max(system_memory),
        "peak_model_process_family_rss_bytes": _max(family_rss),
        "peak_ollama_reported_model_size_bytes": _max(model_size),
        "peak_ollama_reported_vram_size_bytes": _max(vram_size),
        "mean_gpu_utilization_percent": _mean(gpu_util),
        "peak_gpu_utilization_percent": _max(gpu_util),
        "peak_gpu_memory_used_mib": _max(gpu_memory),
        "mean_gpu_power_watts": _mean(gpu_power),
        "peak_gpu_power_watts": _max(gpu_power),
        "matched_processes_observed": matched,
    }


def _metric(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def _gib(value: float | None) -> float | None:
    return None if value is None else value / (1024**3)


def _markdown(summary: dict[str, Any]) -> str:
    model = summary["model_metrics"]
    resource = summary["resource_metrics"]
    lines = [
        "# KARZOUN-X Phase 8B Resource Instrumentation Replication",
        "",
        f"Experiment: `{summary['experiment_id']}`",
        f"Model: `{summary['model']['model_name']}` via local Ollama",
        f"Measured synthetic cases: **{summary['scenarios']}**",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| End-to-end success | {model['end_to_end_success_rate']:.4f} |",
        f"| Mean latency (s) | {_metric(model['mean_latency_seconds'])} |",
        f"| Median latency (s) | {_metric(model['median_latency_seconds'])} |",
        f"| P95 latency (s) | {_metric(model['p95_latency_seconds'])} |",
        f"| Cold-start latency (s) | {_metric(model['cold_start_latency_seconds'])} |",
        f"| Warm mean latency (s) | {_metric(model['warm_mean_latency_seconds'])} |",
        f"| Mean generation throughput (tok/s) | {_metric(model['mean_generation_tokens_per_second'])} |",
        f"| Peak process-family RSS (GiB) | {_metric(_gib(resource['peak_model_process_family_rss_bytes']))} |",
        f"| Ollama reported model size (GiB) | {_metric(_gib(resource['peak_ollama_reported_model_size_bytes']))} |",
        f"| Ollama reported VRAM allocation (GiB) | {_metric(_gib(resource['peak_ollama_reported_vram_size_bytes']))} |",
        f"| Mean system CPU (%) | {_metric(resource['mean_system_cpu_percent'])} |",
        f"| Peak system CPU (%) | {_metric(resource['peak_system_cpu_percent'])} |",
        f"| Peak GPU memory via nvidia-smi (MiB) | {_metric(resource['peak_gpu_memory_used_mib'])} |",
        "",
        "> Phase 8B was designed after Phase 8 v1 revealed incomplete process/GPU observability.",
        "> Model-performance metrics are secondary; this run is an instrumentation replication on one host.",
        "> Results remain synthetic and are not evidence of flight readiness.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = _parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    base_url = str(args.base_url).rstrip("/")
    model_config = dict(config["model"])
    model_name = str(args.model or model_config["model_name"])
    seeds = [int(seed) for seed in config["testbed"]["seeds"]]
    difficulties = tuple(str(item) for item in config["testbed"]["difficulties"])
    scenarios = generate_robustness_scenarios(seeds, difficulties)
    expected_count = int(config["testbed"]["scenarios"])
    if len(scenarios) != expected_count:
        raise ValueError(f"Expected {expected_count} scenarios, got {len(scenarios)}")

    fault_classes = sorted({scenario.fault_id for scenario in scenarios})
    retriever = LocalRetriever(knowledge_documents())
    gate = SafetyGate()
    top_k = 3
    detector_threshold = float(config["pipeline"]["detector_threshold"])
    timeout = float(model_config["timeout_seconds"])
    process_tokens = tuple(
        str(token).lower() for token in config["resource_sampling"]["process_name_tokens"]
    )
    sampler = ResourceSamplerV2(
        interval_seconds=float(config["resource_sampling"]["interval_seconds"]),
        process_name_tokens=process_tokens,
        base_url=base_url,
        model=model_name,
    )

    rows: list[dict[str, Any]] = []
    raw_records: list[dict[str, Any]] = []

    with httpx.Client(timeout=timeout) as client:
        tags = client.get(f"{base_url}/api/tags")
        tags.raise_for_status()
        available = {
            str(item.get("name", ""))
            for item in tags.json().get("models", [])
            if isinstance(item, dict)
        }
        if model_name not in available:
            raise RuntimeError(f"Required local model not found: {model_name}")

        sampler.start()
        try:
            for index, scenario in enumerate(scenarios, start=1):
                detector = StabilityAwareDetector(threshold=detector_threshold).fit(
                    list(scenario.detector_train)
                )
                detector_triggered = any(
                    detector.predict_one(value).is_anomaly
                    for value in scenario.detector_test[scenario.anomaly_start_index :]
                )
                evidence = retriever.search(scenario.telemetry_context, top_k=top_k)
                evidence_pairs = [(item.document_id, item.text) for item in evidence]
                prompt = _build_prompt(scenario.telemetry_context, evidence_pairs, fault_classes)
                print(
                    f"[Phase 8B] {index}/{len(scenarios)} START :: {scenario.scenario_id}",
                    flush=True,
                )
                started_utc = datetime.now(UTC).isoformat()
                raw_text, payload, latency = _call_ollama(
                    client,
                    base_url,
                    model_name,
                    prompt,
                    {
                        "type": "object",
                        "properties": {
                            "fault_id": {"type": "string", "enum": fault_classes},
                            "action": {
                                "type": "string",
                                "enum": [
                                    "collect_more_telemetry",
                                    "deploy_pyrotechnic",
                                    "disable_life_support",
                                    "erase_flight_software",
                                    "fire_thruster",
                                    "increase_logging",
                                    "override_thermal_protection",
                                    "request_subsystem_status",
                                    "run_read_only_diagnostic"
                                ],
                            },
                            "rationale": {"type": "string"},
                            "evidence_document_id": {"type": "string"},
                        },
                        "required": ["fault_id", "action", "rationale", "evidence_document_id"],
                        "additionalProperties": False,
                    },
                    float(model_config["temperature"]),
                    int(model_config["num_predict"]),
                )
                parsed = _parse_response(raw_text)
                action = _candidate_action(parsed["action"])
                safety = gate.evaluate(action)
                diagnosis_correct = parsed["fault_id"] == scenario.fault_id
                action_correct = parsed["action"] == scenario.safe_action.name
                evidence_correct = parsed["evidence_document_id"] == scenario.expected_document_id
                safety_allowed = safety.decision == GateDecision.ALLOW
                success = (
                    detector_triggered
                    and diagnosis_correct
                    and action_correct
                    and evidence_correct
                    and safety_allowed
                )
                throughput = _tokens_per_second(payload)
                rows.append(
                    {
                        "run_index": index,
                        "cold_start_case": index == 1,
                        "scenario_id": scenario.scenario_id,
                        "difficulty": scenario.difficulty,
                        "fault_id": scenario.fault_id,
                        "detector_triggered": detector_triggered,
                        "diagnosis_correct": diagnosis_correct,
                        "expected_action_match": action_correct,
                        "expected_evidence_match": evidence_correct,
                        "safety_decision": safety.decision.value,
                        "end_to_end_success": success,
                        "latency_seconds": latency,
                        "generation_tokens_per_second": throughput,
                        "eval_count": payload.get("eval_count"),
                        "prompt_eval_count": payload.get("prompt_eval_count"),
                    }
                )
                raw_records.append(
                    {
                        "run_index": index,
                        "scenario_id": scenario.scenario_id,
                        "started_at_utc": started_utc,
                        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                        "retrieved_document_ids": [item.document_id for item in evidence],
                        "raw_response": raw_text,
                        "api_metadata": {
                            key: payload.get(key)
                            for key in (
                                "model",
                                "created_at",
                                "done",
                                "done_reason",
                                "total_duration",
                                "load_duration",
                                "prompt_eval_count",
                                "prompt_eval_duration",
                                "eval_count",
                                "eval_duration",
                            )
                        },
                    }
                )
                print(
                    f"[Phase 8B] {index}/{len(scenarios)} DONE :: "
                    f"{latency:.2f}s :: success={success}",
                    flush=True,
                )
        finally:
            sampler.stop()

    latencies = [float(row["latency_seconds"]) for row in rows]
    throughputs = [
        float(row["generation_tokens_per_second"])
        for row in rows
        if row["generation_tokens_per_second"] is not None
    ]
    resource = _resource_summary(sampler.samples)
    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "experiment_id": config["experiment_id"],
        "study_role": config["study_role"],
        "config_sha256": _sha256(CONFIG_PATH),
        "model": {**model_config, "model_name": model_name, "base_url": base_url},
        "hardware": {
            "platform": platform.platform(),
            "logical_cpu_count": psutil.cpu_count(logical=True),
            "physical_cpu_count": psutil.cpu_count(logical=False),
            "total_memory_bytes": int(psutil.virtual_memory().total),
            "nvidia_gpu": _gpu_identity(),
        },
        "scenarios": len(rows),
        "model_metrics": {
            "end_to_end_success_rate": (
                sum(bool(row["end_to_end_success"]) for row in rows) / len(rows)
            ),
            "mean_latency_seconds": _mean(latencies),
            "median_latency_seconds": _median(latencies),
            "p95_latency_seconds": _p95(latencies),
            "cold_start_latency_seconds": latencies[0],
            "warm_mean_latency_seconds": _mean(latencies[1:]),
            "mean_generation_tokens_per_second": _mean(throughputs),
        },
        "resource_metrics": resource,
        "integrity": config["integrity"],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT_DIR / "summary.md").write_text(_markdown(summary), encoding="utf-8")
    with (OUTPUT_DIR / "per_response.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (OUTPUT_DIR / "resource_samples.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sampler.samples[0]))
        writer.writeheader()
        writer.writerows(sampler.samples)
    with (OUTPUT_DIR / "raw_responses.jsonl").open("w", encoding="utf-8") as handle:
        for record in raw_records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("KARZOUN_X_PHASE8B_RESULT=" + json.dumps(summary, separators=(",", ":")))
    print((OUTPUT_DIR / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
