from __future__ import annotations

import ast
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class LabeledChannel:
    channel_id: str
    spacecraft: str
    anomaly_sequences: tuple[tuple[int, int], ...]
    num_values: int


def _parse_sequences(raw: str) -> tuple[tuple[int, int], ...]:
    parsed = ast.literal_eval(raw)
    sequences: list[tuple[int, int]] = []
    for item in parsed:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"Invalid anomaly sequence: {item!r}")
        start, end = int(item[0]), int(item[1])
        if start < 0 or end < start:
            raise ValueError(f"Invalid anomaly interval: {(start, end)!r}")
        sequences.append((start, end))
    return tuple(sequences)


def load_labeled_channels(path: str | Path) -> list[LabeledChannel]:
    """Load Telemanom-style labeled anomaly metadata.

    The loader intentionally depends only on the stable metadata columns used by the
    public SMAP/MSL benchmark and ignores optional descriptive columns.
    """
    source = Path(path)
    channels: list[LabeledChannel] = []
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"chan_id", "spacecraft", "anomaly_sequences", "num_values"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        for row in reader:
            channels.append(
                LabeledChannel(
                    channel_id=row["chan_id"].strip(),
                    spacecraft=row["spacecraft"].strip(),
                    anomaly_sequences=_parse_sequences(row["anomaly_sequences"]),
                    num_values=int(row["num_values"]),
                )
            )
    return channels
