# Contributing

Contributions are welcome when they improve scientific clarity, reproducibility, safety, or implementation quality.

## Before opening a change

- Keep empirical claims tied to reproducible evidence.
- Add or update tests for behavior changes.
- Do not commit raw datasets unless redistribution rights are verified.
- Do not commit model weights, secrets, API keys, or private telemetry.
- Keep safety-gate changes explicit and reviewable.

## Local checks

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

## Research changes

For new experiments, document:

- hypothesis or research question
- dataset and split
- model/version
- random seed(s)
- hardware/runtime environment
- metrics
- expected failure modes

Use the research-question issue template when proposing a new study.
