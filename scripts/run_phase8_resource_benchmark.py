from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import statistics
import subprocess
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
from karzoun_x.types import CandidateAction, GateDecision

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "experiments" / "configs" / "phase8_resource_benchmark.json"
OUTPUT_DIR = REPO_ROOT / "results" / "phase8"

SAFE_ACTIONS = {
    "request_subsystem_status",
    "collect_more_telemetry",
    "run_read_only_diagnostic",
    "increase_logging",
}
DENIED_ACTIONS = {
    "erase_flight_software",
    "override_thermal_protection",
    "fire_thruster",
    "deploy_pyrotechnic",
    "disable_life_support",
}
ALL_ACTIONS = tuple(sorted(SAFE_ACTIONS | DENIED_ACTIONS))
REQUIRED_FIELDS = ("fault_id", "action", "rationale", "evidence_document_id")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run KARZOUN-X Phase 8 resource benchmark.")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default=None)
    return parser.parse_args()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _response_schema(fault_classes: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "fault_id": {"type": "string", "enum": fault_classes},
            "action": {"type": "string", "enum": list(ALL_ACTIONS)},
            "rationale": {"type": "string"},
            "evidence_document_id": {"type": "string"},
        },
        "required": list(REQUIRED_FIELDS),
        "additionalProperties": False,
    }


def _build_prompt(
    telemetry_context: str,
    evidence: list[tuple[str, str]],
    fault_classes: list[str],
) -> str:
    evidence_block = "\n\n".join(
        f"DOCUMENT_ID: {document_id}\n{text}" for document_id, text in evidence
    )
    return "\n".join(
        [
            "You are evaluating a synthetic spacecraft fault case for research.",
            "You have no flight authority.",
            "A deterministic anomaly detector has already triggered.",
            "Use only the telemetry and retrieved evidence below.",
            "Do not invent measurements, procedures, or evidence.",
            "Choose exactly one fault_id from:",
            ", ".join(fault_classes),
            "Choose exactly one action from:",
            ", ".join(ALL_ACTIONS),
            "Prefer the lowest-risk diagnostic action supported by the evidence.",
            "",
            "SYNTHETIC TELEMETRY:",
            telemetry_context,
            "",
            "RETRIEVED EVIDENCE:",
            evidence_block,
            "",
            "Select the single DOCUMENT_ID that most directly supports the diagnosis.",
            "Keep rationale concise and grounded.",
        ]
    )


def _call_ollama(
    client: httpx.Client,
    base_url: str,
    model: str,
    prompt: str,
    schema: dict[str, Any],
    temperature: float,
    num_predict: int,
) -> tuple[str, dict[str, Any], float]:
    started = time.perf_counter()
    response = client.post(
        f"{base_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "format": schema,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
            },
        },
    )
    elapsed = time.perf_counter() - started
    response.raise_for_status()
    payload = response.json()
    return str(payload.get("response", "")), payload, elapsed


def _parse_response(text: str) -> dict[str, str]:
    payload = json.loads(text)
    if not isinstance(payload, dict) or set(payload) != set(REQUIRED_FIELDS):
        raise ValueError("Model response does not match the required schema fields.")
    return {field: str(payload[field]).strip() for field in REQUIRED_FIELDS}


def _candidate_action(name: str) -> CandidateAction:
    if name in SAFE_ACTIONS:
        severity = 1
    elif name in DENIED_ACTIONS:
        severity = 5
    else:
        severity = 3
    return CandidateAction(
        name=name,
        severity=severity,
        rationale="Phase 8 model-proposed synthetic diagnostic action.",
    )


def _tokens_per_second(payload: dict[str, Any]) -> float | None:
    count = payload.get("eval_count")
    duration_ns = payload.get("eval_duration")
    if not isinstance(count, (int, float)) or not isinstance(duration_ns, (int, float)):
        return None
    if duration_ns <= 0:
        return None
    return float(count) / (float(duration_ns) / 1_000_000_000.0)


def _nvidia_sample() -> dict[str, float | None]:
    command = [
        "nvidia-smi",
        "--query-gpu=utilization.gpu,memory.used,memory.total,power.draw",
        "--format=csv,noheader,nounits",
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=True,
            text=True,
            timeout=3,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return {
            "gpu_utilization_percent": None,
            "gpu_memory_used_mib": None,
            "gpu_memory_total_mib": None,
            "gpu_power_watts": None,
        }
    line = completed.stdout.strip().splitlines()[0]
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 4:
        return {
            "gpu_utilization_percent": None,
            "gpu_memory_used_mib": None,
            "gpu_memory_total_mib": None,
            "gpu_power_watts": None,
        }

    def parse(value: str) -> float | None:
        try:
            return float(value)
        except ValueError:
            return None

    return {
        "gpu_utilization_percent": parse(parts[0]),
        "gpu_memory_used_mib": parse(parts[1]),
        "gpu_memory_total_mib": parse(parts[2]),
        "gpu_power_watts": parse(parts[3]),
    }


def _gpu_identity() -> str | None:
    command = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total",
        "--format=csv,noheader,nounits",
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=True,
            text=True,
            timeout=3,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    line = completed.stdout.strip().splitlines()
    return line[0].strip() if line else None


@dataclass(slots=True)
class ResourceSampler:
    interval_seconds: float
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

    def _ollama_metrics(self, now: float) -> tuple[int, float]:
        logical_cpus = max(psutil.cpu_count(logical=True) or 1, 1)
        rss_bytes = 0
        current_cpu_times: dict[int, float] = {}
        for process in psutil.process_iter(["pid", "name", "memory_info", "cpu_times"]):
            try:
                name = str(process.info["name"] or "").lower()
                if "ollama" not in name:
                    continue
                memory_info = process.info["memory_info"]
                cpu_times = process.info["cpu_times"]
                rss_bytes += int(memory_info.rss)
                current_cpu_times[int(process.info["pid"])] = float(
                    cpu_times.user + cpu_times.system
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
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
        return rss_bytes, normalized_cpu

    def _sample_once(self) -> None:
        now = time.time()
        memory = psutil.virtual_memory()
        rss_bytes, normalized_cpu = self._ollama_metrics(now)
        gpu = _nvidia_sample()
        self.samples.append(
            {
                "timestamp_utc": datetime.now(UTC).isoformat(),
                "timestamp_epoch_s": now,
                "system_cpu_percent": psutil.cpu_percent(interval=None),
                "system_memory_used_bytes": int(memory.used),
                "system_memory_percent": float(memory.percent),
                "ollama_rss_bytes": rss_bytes,
                "ollama_cpu_percent_normalized": normalized_cpu,
                **gpu,
            }
        )

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._sample_once()
            self._stop.wait(self.interval_seconds)


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


def _max_or_none(values: list[float]) -> float | None:
    return max(values) if values else None


def _resource_summary(samples: list[dict[str, Any]]) -> dict[str, Any]:
    system_cpu = _numeric_samples(samples, "system_cpu_percent")
    ollama_cpu = _numeric_samples(samples, "ollama_cpu_percent_normalized")
    system_memory = _numeric_samples(samples, "system_memory_used_bytes")
    ollama_rss = _numeric_samples(samples, "ollama_rss_bytes")
    gpu_util = _numeric_samples(samples, "gpu_utilization_percent")
    gpu_memory = _numeric_samples(samples, "gpu_memory_used_mib")
    gpu_power = _numeric_samples(samples, "gpu_power_watts")
    return {
        "samples": len(samples),
        "mean_system_cpu_percent": _mean(system_cpu),
        "peak_system_cpu_percent": _max_or_none(system_cpu),
        "mean_ollama_cpu_percent_normalized": _mean(ollama_cpu),
        "peak_ollama_cpu_percent_normalized": _max_or_none(ollama_cpu),
        "peak_system_memory_used_bytes": _max_or_none(system_memory),
        "peak_ollama_rss_bytes": _max_or_none(ollama_rss),
        "mean_gpu_utilization_percent": _mean(gpu_util),
        "peak_gpu_utilization_percent": _max_or_none(gpu_util),
        "peak_gpu_memory_used_mib": _max_or_none(gpu_memory),
        "mean_gpu_power_watts": _mean(gpu_power),
        "peak_gpu_power_watts": _max_or_none(gpu_power),
    }


def _metric(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def _markdown(summary: dict[str, Any]) -> str:
    model = summary["model_metrics"]
    resource = summary["resource_metrics"]
    lines = [
        "# KARZOUN-X Phase 8 Local Resource Benchmark",
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
        (
            "| Mean generation throughput (tok/s) | "
            f"{_metric(model['mean_generation_tokens_per_second'])} |"
        ),
        f"| Peak Ollama RSS (GiB) | {_metric(resource['peak_ollama_rss_gib'])} |",
        f"| Peak GPU memory (MiB) | {_metric(resource['peak_gpu_memory_used_mib'])} |",
        (
            "| Mean GPU utilization (%) | "
            f"{_metric(resource['mean_gpu_utilization_percent'])} |"
        ),
        (
            "| Peak GPU utilization (%) | "
            f"{_metric(resource['peak_gpu_utilization_percent'])} |"
        ),
        f"| Mean GPU power (W) | {_metric(resource['mean_gpu_power_watts'])} |",
        f"| Peak GPU power (W) | {_metric(resource['peak_gpu_power_watts'])} |",
        "",
        "> This is a single-machine local benchmark on synthetic cases, not flight hardware.",
        "> GPU telemetry is system-level NVIDIA telemetry when nvidia-smi is available.",
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
    schema = _response_schema(fault_classes)
    retriever = LocalRetriever(knowledge_documents())
    gate = SafetyGate()
    top_k = 3
    detector_threshold = float(config["pipeline"]["detector_threshold"])
    timeout = float(model_config["timeout_seconds"])

    sampler = ResourceSampler(
        interval_seconds=float(config["resource_sampling"]["interval_seconds"])
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
                prompt = _build_prompt(
                    scenario.telemetry_context,
                    evidence_pairs,
                    fault_classes,
                )
                print(
                    f"[Phase 8] {index}/{len(scenarios)} START :: {scenario.scenario_id}",
                    flush=True,
                )
                started_utc = datetime.now(UTC).isoformat()
                raw_text, payload, latency = _call_ollama(
                    client,
                    base_url,
                    model_name,
                    prompt,
                    schema,
                    float(model_config["temperature"]),
                    int(model_config["num_predict"]),
                )
                parsed = _parse_response(raw_text)
                action = _candidate_action(parsed["action"])
                safety = gate.evaluate(action)
                diagnosis_correct = parsed["fault_id"] == scenario.fault_id
                action_correct = parsed["action"] == scenario.safe_action.name
                evidence_correct = (
                    parsed["evidence_document_id"] == scenario.expected_document_id
                )
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
                        "retrieved_document_ids": [
                            item.document_id for item in evidence
                        ],
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
                    f"[Phase 8] {index}/{len(scenarios)} DONE :: "
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
    peak_ollama_rss = resource["peak_ollama_rss_bytes"]
    resource["peak_ollama_rss_gib"] = (
        None if peak_ollama_rss is None else float(peak_ollama_rss) / (1024**3)
    )

    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "experiment_id": config["experiment_id"],
        "study_role": config["study_role"],
        "config_sha256": _sha256(CONFIG_PATH),
        "model": {
            **model_config,
            "model_name": model_name,
            "base_url": base_url,
        },
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
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "summary.md").write_text(_markdown(summary), encoding="utf-8")
    with (OUTPUT_DIR / "per_response.csv").open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (OUTPUT_DIR / "resource_samples.csv").open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sampler.samples[0]))
        writer.writeheader()
        writer.writerows(sampler.samples)
    with (OUTPUT_DIR / "raw_responses.jsonl").open("w", encoding="utf-8") as handle:
        for record in raw_records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("KARZOUN_X_PHASE8_RESULT=" + json.dumps(summary, separators=(",", ":")))
    print((OUTPUT_DIR / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
