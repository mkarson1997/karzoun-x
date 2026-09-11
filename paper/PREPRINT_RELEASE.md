# KARZOUN-X preprint release metadata

This file records the intended metadata for the first public KARZOUN-X preprint deposit. It deliberately separates the **paper/preprint record** from the **software release record** so that the paper DOI is not confused with the software DOI.

## Preprint deposit

- **Resource type:** Publication / Preprint
- **Title:** KARZOUN-X: A Resource-Aware, Safety-Gated Local LLM and RAG Architecture for Autonomous Spacecraft Fault Diagnosis Under Communication Delay
- **Creator:** Mahmoud Karzoun
- **ORCID:** 0009-0006-2752-7744
- **Publication date:** 2026-09-11
- **Language:** English
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Version:** v0.1.0-rc1
- **Repository:** https://github.com/mkarson1997/karzoun-x

### Description

KARZOUN-X studies a local-first spacecraft fault-diagnosis and low-risk decision-support architecture combining telemetry anomaly detection, local retrieval-augmented generation, a locally deployed language model, deterministic action gating, communication-delay analysis, hard-stress evaluation, and auditable resource measurement. The study separates real SMAP/MSL anomaly-detection evaluation from synthetic diagnosis/action experiments. On separable synthetic cases, retrieved evidence strongly improved expected next-action selection, while a precommitted hard-stress suite exposed substantial failures of epistemic abstention under ambiguous, conflicting, or missing evidence. The work is a research prototype and is not flight-qualified or certified for autonomous spacecraft control.

### Keywords

- spacecraft autonomy
- spacecraft fault diagnosis
- local LLM
- retrieval-augmented generation
- telemetry anomaly detection
- deterministic safety gate
- deep-space communication delay
- resource-aware AI
- uncertainty
- autonomous systems

### Recommended related identifier

Add the GitHub repository as a related identifier with a relation indicating that the repository is the software/source associated with the preprint.

## Software archival record

The GitHub release `v0.1.0-rc1` is intended to be archived separately as **Software** through the Zenodo-GitHub integration. Zenodo should read `.zenodo.json` for that software record. Because `.zenodo.json` is present, Zenodo will use it instead of `CITATION.cff` for GitHub-release metadata.

The software DOI and the preprint DOI should remain distinct. After both are public, cross-link them as related identifiers and add the DOI-backed preprint to ORCID.

## Publication order

1. Enable the public `mkarson1997/karzoun-x` repository in Zenodo's GitHub integration before creating the GitHub release.
2. Run the repository workflow **Publish v0.1.0-rc1** to create the tagged GitHub release with PDF/DOCX assets.
3. Confirm that Zenodo has ingested the GitHub release and issued the software DOI.
4. Create a separate Zenodo upload for the preprint PDF using the metadata above and publish it to mint the preprint DOI.
5. Cross-link the two Zenodo records, update repository citation guidance, and then add the preprint work to ORCID.

Do not invent or pre-fill a DOI. Record only identifiers actually issued by the archive.
