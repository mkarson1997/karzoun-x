from __future__ import annotations

import httpx


class OllamaReasoner:
    """Minimal Ollama-compatible local reasoner adapter."""

    def __init__(self, base_url: str, model: str, timeout_seconds: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def health(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False

    def diagnose(self, telemetry_context: str, evidence: list[str]) -> str:
        evidence_block = "\n\n".join(f"- {item}" for item in evidence) or "- No evidence retrieved"
        prompt = f"""You are a research diagnostic assistant operating on historical or simulated spacecraft telemetry.
Do not claim flight authority. Use only the supplied telemetry context and evidence. If evidence is insufficient, say so explicitly.

Telemetry context:
{telemetry_context}

Retrieved evidence:
{evidence_block}

Return a concise diagnosis with: suspected issue, supporting evidence, uncertainty, and a low-risk recommended next diagnostic step.
"""
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload.get("response", "")).strip()
