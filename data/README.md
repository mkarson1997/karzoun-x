# Data

Raw spacecraft telemetry is **not committed** to this repository.

The first benchmark target is the public telemetry anomaly dataset distributed with the Telemanom project, containing anonymized, normalized telemetry from NASA's SMAP mission and the Mars Science Laboratory (Curiosity) mission.

Upstream project:
- https://github.com/khundman/telemanom

The upstream repository documents 82 unique telemetry channels and 105 labeled anomaly sequences across SMAP and MSL.

## Expected local layout

```text
data/
├── raw/
│   └── telemanom/
├── processed/
└── README.md
```

Use:

```bash
python scripts/download_telemanom.py
```

The script clones only the upstream research repository into `data/raw/telemanom`. Review the upstream license and citation requirements before redistributing any dataset files.
