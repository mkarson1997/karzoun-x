# KARZOUN-X peer-reviewed submission plan

Verified: 11 September 2026.

## Primary target: Acta Astronautica

**Recommendation:** submit the completed v1 manuscript first to **Acta Astronautica** as a regular research article.

Rationale:

- The journal explicitly covers original contributions in space engineering and the conception, design, development, and operation of space-borne and Earth-based systems.
- Recent Acta Astronautica papers include AI-powered space systems, autonomous orbital maintenance, deep-space fault-management considerations, and machine-learning anomaly-response research, making the topic fit materially better than a generic AI journal.
- The work's strongest framing is a spacecraft-autonomy systems paper with explicit engineering safety and resource boundaries, not a general-purpose LLM benchmark.

Official journal scope:
https://shop.elsevier.com/journals/acta-astronautica/0094-5765

Elsevier preprint policy:
https://www.elsevier.com/about/policies-and-standards/sharing

Elsevier states that author preprints may be shared anywhere at any time and that preprint sharing does not count as prior publication under its general author guidance. The Zenodo preprint should therefore be disclosed transparently in the cover letter and submission metadata rather than hidden.

## Backup targets

1. **Advances in Space Research** — broad COSPAR space-research journal. Suitable if the editor views KARZOUN-X primarily as space-research methodology rather than spacecraft engineering.
2. A suitable aerospace/autonomous-systems journal can be evaluated after any editorial feedback from Acta Astronautica; do not submit concurrently.

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
- `cover_letter_v1.md` (paste into submission system or convert to PDF if requested)
- `highlights_v1.txt`
- `graphical_abstract.svg` / rendered PNG if the journal requests or accepts one
- `data_code_availability.md`
- `author_declarations.md`

## Preprint disclosure

Prior public preprint:
https://doi.org/10.5281/zenodo.22708262

Archived research software:
https://doi.org/10.5281/zenodo.22708005

Both should be disclosed in submission metadata/cover letter. The software and preprint are distinct DOI-backed research outputs.
