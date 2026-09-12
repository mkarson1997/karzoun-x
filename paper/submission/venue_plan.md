# KARZOUN-X peer-reviewed submission plan

Updated: 12 September 2026.

## Primary target: Acta Astronautica

**Recommendation:** submit the completed v1 manuscript first to **Acta Astronautica** as a regular research article.

Rationale:

- The journal covers original contributions in space engineering and the conception, design, development, and operation of space-borne and Earth-based systems.
- KARZOUN-X is best positioned as a spacecraft-autonomy systems paper with explicit engineering safety, uncertainty, communication, and resource boundaries rather than as a generic LLM benchmark.
- The manuscript preserves negative and mixed results and clearly separates real telemetry anomaly detection from synthetic diagnosis/action evidence.

Official journal scope:
https://www.sciencedirect.com/journal/acta-astronautica

The public Zenodo preprint must be disclosed transparently in the cover letter and submission metadata. Do not submit the manuscript concurrently to another peer-reviewed journal.

## Backup target

**Advances in Space Research** is the first backup if Acta Astronautica declines the paper or judges it outside scope. A different aerospace/autonomous-systems venue can be evaluated after editorial feedback.

## Submission positioning

The manuscript should be submitted as a research article centered on these claims:

1. Local RAG changed evidence-grounded next-action selection on paired synthetic cases without changing already-saturated fault classification.
2. Communication-delay analysis quantifies why a local diagnostic path can remain available when a ground-dependent path is delayed or unavailable.
3. Phase 9 exposes a concrete epistemic-safety failure mode that action-hazard gating alone cannot solve.
4. Phase 11 evaluates a deterministic evidence-sufficiency mitigation on newly held-out cases, with the post-Phase-9 design chronology disclosed.
5. Phase 12 quantifies the quality/resource trade-off across three frozen local model sizes on the same host and scenarios.

Do **not** position the work as flight-ready, NASA-endorsed, the first LLM in spacecraft autonomy, or proof of operational spacecraft safety.

## Expected submission files

- `KARZOUN-X-journal-submission-v1.0.0.pdf`
- `KARZOUN-X-journal-submission-v1.0.0.docx`
- `cover_letter_v1.md`
- `highlights_v1.txt`
- `graphical_abstract.svg` / rendered PNG if the journal requests or accepts one
- `data_code_availability.md`
- `author_declarations.md`
- `submission_metadata_v1.json`
- `submission_checklist.md`

## Preprint disclosure

Canonical public preprint v1.0.0:
https://doi.org/10.5281/zenodo.22712634

Preprint concept DOI for all versions:
https://doi.org/10.5281/zenodo.22708261

Stable software DOI family:
https://doi.org/10.5281/zenodo.22708004

Stable GitHub release:
https://github.com/mkarson1997/karzoun-x/releases/tag/v1.0.0

The software and preprint are distinct DOI-backed research outputs.
