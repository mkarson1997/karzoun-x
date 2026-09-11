# KARZOUN-X preprint release metadata

This file records the metadata for the first public KARZOUN-X preprint deposit. It deliberately separates the **paper/preprint record** from the **software release record** so that the paper DOI is not confused with the software DOI.

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
- **Reserved preprint DOI:** 10.5281/zenodo.22708262

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

### Related identifiers

For the preprint deposit, add:

1. Software DOI `10.5281/zenodo.22708005` as the software associated with this preprint.
2. Repository URL `https://github.com/mkarson1997/karzoun-x` as the source-code repository.

## Software archival record

The GitHub release `v0.1.0-rc1` is archived separately as **Software** through the Zenodo-GitHub integration.

- **Software version DOI:** 10.5281/zenodo.22708005
- **Software concept DOI:** 10.5281/zenodo.22708004

The software DOI and the preprint DOI remain distinct. After the preprint is published, cross-link the two Zenodo records, update repository citation guidance, and then add the DOI-backed preprint to ORCID.

## Publication order

1. Zenodo GitHub integration enabled for `mkarson1997/karzoun-x`.
2. GitHub release `v0.1.0-rc1` published and archived by Zenodo as Software.
3. Software DOI issued: `10.5281/zenodo.22708005`.
4. Preprint DOI reserved: `10.5281/zenodo.22708262`.
5. Rebuild the preprint PDF with the reserved DOI embedded in the title-page metadata.
6. Upload that PDF to the separate Zenodo Preprint draft, complete metadata, and publish.
7. Cross-link software and preprint records, update repository citation guidance, and add the DOI-backed preprint to ORCID.

Do not invent identifiers. Record only identifiers actually issued or reserved by Zenodo.
