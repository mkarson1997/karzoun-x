# Data and code availability

All KARZOUN-X source code, frozen experiment configurations, machine-generated result summaries, raw local-model responses, resource samples, provenance hashes, and experiment-index metadata used for the reported research are maintained in the public repository:

https://github.com/mkarson1997/karzoun-x

The stable software family is archived through Zenodo under concept DOI:

https://doi.org/10.5281/zenodo.22708004

The stable GitHub software release is:

https://github.com/mkarson1997/karzoun-x/releases/tag/v1.0.0

The canonical public preprint version is available through Zenodo:

https://doi.org/10.5281/zenodo.22712634

The preprint concept DOI for all versions is:

https://doi.org/10.5281/zenodo.22708261

The real-data anomaly-detection track uses the public SMAP/MSL benchmark associated with Telemanom. KARZOUN-X does not redistribute the upstream benchmark by default. Acquisition instructions, upstream provenance, and cryptographic hashes are documented in `data/README.md` and `experiments/RESULTS_INDEX.md`.

SMAP/MSL is used only for anomaly-detection evaluation. Diagnosis, retrieval, action-policy, communication, hard-stress, and epistemic-gate experiments use separately labeled synthetic research scenarios. This separation is intentional because the public SMAP/MSL anomaly intervals do not provide detailed root-cause and recovery-action labels for each anomaly.
