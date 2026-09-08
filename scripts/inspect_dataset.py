from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from karzoun_x.datasets import load_labeled_channels


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Telemanom label metadata.")
    parser.add_argument(
        "labels",
        nargs="?",
        default="data/raw/telemanom/labeled_anomalies.csv",
        help="Path to labeled_anomalies.csv",
    )
    args = parser.parse_args()

    channels = load_labeled_channels(Path(args.labels))
    spacecraft = Counter(channel.spacecraft for channel in channels)
    anomaly_count = sum(len(channel.anomaly_sequences) for channel in channels)
    value_count = sum(channel.num_values for channel in channels)

    print(f"channels={len(channels)}")
    print(f"anomaly_sequences={anomaly_count}")
    print(f"metadata_num_values_total={value_count}")
    for name, count in sorted(spacecraft.items()):
        print(f"spacecraft[{name}]={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
