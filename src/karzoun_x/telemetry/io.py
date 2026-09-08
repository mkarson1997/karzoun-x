from __future__ import annotations

import csv
from pathlib import Path

from karzoun_x.types import TelemetrySample


def load_csv_channel(path: str | Path, channel_id: str) -> list[TelemetrySample]:
    """Load a simple two-column telemetry CSV with timestamp_s,value headers."""
    source = Path(path)
    samples: list[TelemetrySample] = []
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"timestamp_s", "value"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"CSV must contain columns: {sorted(required)}")
        for row in reader:
            samples.append(
                TelemetrySample(
                    channel_id=channel_id,
                    timestamp_s=float(row["timestamp_s"]),
                    value=float(row["value"]),
                )
            )
    return samples
