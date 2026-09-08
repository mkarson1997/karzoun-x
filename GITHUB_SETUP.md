# GitHub Repository Settings

Use these exact values for the public repository.

## Repository name
`karzoun-x`

## Visibility
Public

## Description
`KARZOUN-X — Open research on resource-aware, safety-gated local AI for autonomous spacecraft fault diagnosis under delayed or unavailable Earth communication.`

## Website
Leave blank until a project/research page is published. Do not point to an unrelated site.

## Topics

- artificial-intelligence
- spacecraft
- spacecraft-autonomy
- fault-diagnosis
- anomaly-detection
- telemetry
- local-llm
- rag
- autonomous-systems
- safety-ai
- space-ai
- python
- research
- smap
- mars-science-laboratory

## Features
Recommended:

- Issues: ON
- Discussions: ON once community/research discussion begins
- Projects: optional
- Wiki: OFF initially; keep canonical docs versioned in the repository
- Sponsorships: OFF initially

## Pull requests

Recommended:

- Allow squash merging: ON
- Allow merge commits: OFF
- Allow rebase merging: ON
- Always suggest updating pull request branches: ON
- Automatically delete head branches: ON

## Security

Recommended when available:

- Private vulnerability reporting: ON
- Dependabot alerts: ON
- Dependabot security updates: ON
- Secret scanning: ON where available
- Push protection: ON where available

## Branch protection / ruleset for `main`

After the first commit and CI are healthy:

- Require a pull request before merging: ON for external contributions
- Require status checks: `test`
- Block force pushes: ON
- Block deletions: ON
- Require linear history: optional

For a solo research prototype, direct maintainer commits can remain allowed during the early experiment phase if that keeps iteration practical. Tighten the rule before publication freeze.

## Social preview

Add a clean KARZOUN-X research graphic later. Do not use NASA logos or imagery in a way that implies endorsement.

## Release naming

Development releases: `v0.x.y-alpha`  
First archival research snapshot: `v0.1.0` or later after reproducible benchmark completion.

## DOI workflow

When a publication-ready version exists, archive a tagged GitHub release in a DOI-minting research repository such as Zenodo, then place the DOI badge in README and update `CITATION.cff`.
