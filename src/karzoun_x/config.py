from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    ollama_url: str = os.getenv("KARZOUN_X_OLLAMA_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("KARZOUN_X_OLLAMA_MODEL", "qwen3:14b-q4_K_M")
    request_timeout_seconds: float = float(
        os.getenv("KARZOUN_X_REQUEST_TIMEOUT_SECONDS", "120")
    )
    max_authorized_severity: int = int(
        os.getenv("KARZOUN_X_MAX_AUTHORIZED_SEVERITY", "2")
    )
