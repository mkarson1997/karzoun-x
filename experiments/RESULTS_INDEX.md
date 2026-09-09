# KARZOUN-X Experiment Results Index

Frozen experiment configurations are treated as immutable after execution. Completion and provenance are recorded here rather than by editing the executed config.

| Experiment | Status | Source run | Results |
|---|---|---|---|
| `phase1-robust-zscore-v1` | Completed | GitHub Actions run `34337918870` | `results/phase1/summary.json`, `results/phase1/per_channel.csv` |
| `phase2-adaptive-temporal-v1` | Completed (mixed result) | GitHub Actions run `34340023894` | `results/phase2/summary.json`, `results/phase2/per_record.csv` |
| `phase3-stability-aware-v1` | Completed (best F1 so far, exploratory) | GitHub Actions run `34347057969` | `results/phase3/summary.json`, `results/phase3/per_record.csv` |
| `phase4-fault-testbed-v1` | Completed (retrieval/safety mechanics validated; no LLM yet) | GitHub Actions run `34348018741` | `results/phase4/summary.json`, `results/phase4/per_scenario.csv` |

## Phase 1 provenance

- Frozen config SHA-256: `af06f715a46a90e1efc5c0c037e805bdd28cbe36ac1f4e20565aab8bb197448a`
- Dataset archive SHA-256: `6084d3ee3906381f2c98aa3773b6b2d77c82413503faa78f962196582e873733`
- Labels SHA-256: `057ce2d6c8875982bf4e5404aefea14efdcbce413d80826d2b737c95b59b7539`
- Source commit executed: `ff07c4027214d168f7034c5abc194fdce9b117eb`
- GitHub Actions run: https://github.com/mkarson1997/karzoun-x/actions/runs/34337918870
- Artifact SHA-256: `be4db9fefe18c52de90615b731f0d8dfc2dfbda2d951b0092408159629567b38`

## Phase 2 provenance

- Frozen config SHA-256: `fe761b5f3170249e798a31a2bf9dcef1f4331570937cb607feb4d52088f173b8`
- Dataset archive SHA-256: `6084d3ee3906381f2c98aa3773b6b2d77c82413503faa78f962196582e873733`
- Labels SHA-256: `057ce2d6c8875982bf4e5404aefea14efdcbce413d80826d2b737c95b59b7539`
- Source commit executed: `8144e60765fd154bf9b1eebefe40badaf8bb951b`
- GitHub Actions run: https://github.com/mkarson1997/karzoun-x/actions/runs/34340023894
- Artifact SHA-256: `bc04b31fe386f9829ff0e8aaaf9659ac09e28dbb02f9f1494e285586fd6854b5`
- Interpretation: Phase 2 reduced false positives and improved precision, but reduced recall, event recall, and overall F1 relative to Phase 1. It is therefore retained as an auditable mixed/negative result rather than promoted as the primary detector.

## Phase 3 provenance

- Frozen config SHA-256: `934b79837c0e30ab3328590f5c1e0af488d5ccaf56f075557548f9c055685fb1`
- Dataset archive SHA-256: `6084d3ee3906381f2c98aa3773b6b2d77c82413503faa78f962196582e873733`
- Labels SHA-256: `057ce2d6c8875982bf4e5404aefea14efdcbce413d80826d2b737c95b59b7539`
- Source commit executed: `e35aa798551eaf3213a8585617da7b883d4ffa0a`
- GitHub Actions run: https://github.com/mkarson1997/karzoun-x/actions/runs/34347057969
- Artifact SHA-256: `774df8db3e8da1ac5729dac73719b69753a41e93c1da06fab8d8e6a81b0eb8cd`
- Interpretation: Phase 3 uses the Phase 1 MAD rule where training MAD is stable and switches to a training-standard-deviation fallback only when MAD collapses. It achieved the highest total F1 of the first three phases (`0.4054`) while reducing false positives by `28,606` relative to Phase 1. Because its design was informed by earlier benchmark results, it is explicitly exploratory and is not treated as an untouched confirmatory result.

## Phase 4 provenance

- Frozen config SHA-256: `fb3bd9b084be3c3a27eb714d99f9b40771cbedd2b9895b28aba35c4ae1637f20`
- Held-out seeds: `2201`, `2202`
- Fault classes: `6`
- Held-out scenarios: `12`
- Source commit executed: `a47a2ed5a23dba962ed832221ba2ec67243e424c`
- GitHub Actions run: https://github.com/mkarson1997/karzoun-x/actions/runs/34348018741
- Artifact SHA-256: `a8ce4ce8fa21d5cb1cc8824d54d9bb605b02284118369bd9f2412367dfa7fd7f`
- Interpretation: the deterministic lexical retriever returned the expected manual as the top result for all 12 held-out synthetic scenarios, all expected low-risk diagnostic actions were allowed, all synthetic high-risk distractor actions were blocked, and no unsafe distractor was falsely allowed. This validates the mechanics of the retrieval and deterministic safety layers on the deliberately small synthetic testbed. It does not validate language-model diagnosis, real spacecraft performance, or flight readiness.
