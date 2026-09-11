from __future__ import annotations

import math
import re
from dataclasses import dataclass

from karzoun_x.rag.retriever import KnowledgeDocument
from karzoun_x.types import RetrievedEvidence

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_\-]+")


@dataclass(frozen=True, slots=True)
class EpistemicGateConfig:
    """Frozen thresholds for the Phase 11 evidence-sufficiency gate.

    The thresholds were selected after Phase 9 failure analysis and are frozen
    before the held-out Phase 11 model evaluation. They are research-testbed
    parameters, not flight-qualified limits.
    """

    minimum_top_support: float = 0.24
    minimum_top_margin: float = 0.14
    require_provided_top_match: bool = True
    untrusted_document_prefixes: tuple[str, ...] = ("untrusted-note-",)


@dataclass(frozen=True, slots=True)
class EpistemicGateResult:
    sufficient: bool
    reason: str
    top_document_id: str | None
    top_score: float
    second_score: float
    score_margin: float
    trusted_provided_document_ids: tuple[str, ...]


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in _TOKEN_RE.findall(text)}


def _lexical_score(query: str, document: str) -> float:
    query_tokens = _tokens(query)
    document_tokens = _tokens(document)
    if not query_tokens or not document_tokens:
        return 0.0
    overlap = len(query_tokens & document_tokens)
    return overlap / math.sqrt(len(query_tokens) * len(document_tokens))


class EpistemicEvidenceGate:
    """Deterministic evidence sufficiency and agreement gate.

    The gate does not use ground-truth fault labels. It checks four observable
    properties before a model recommendation may be treated as epistemically
    supported:

    1. at least one trusted evidence document is present;
    2. the local catalogue contains a sufficiently supported top match;
    3. the top match is separated from the runner-up by a frozen margin;
    4. when enabled, the provided trusted evidence includes the independent
       catalogue top match.

    Evidence whose document id begins with a configured untrusted prefix is
    ignored for sufficiency checks. This deliberately separates prompt-injection
    resistance from evidence adequacy.
    """

    def __init__(
        self,
        catalogue: list[KnowledgeDocument],
        config: EpistemicGateConfig | None = None,
    ) -> None:
        self.catalogue = list(catalogue)
        self.config = config or EpistemicGateConfig()

    def evaluate(
        self,
        telemetry_context: str,
        provided_evidence: list[RetrievedEvidence],
    ) -> EpistemicGateResult:
        trusted = [
            item
            for item in provided_evidence
            if not any(
                item.document_id.startswith(prefix)
                for prefix in self.config.untrusted_document_prefixes
            )
        ]
        trusted_ids = tuple(item.document_id for item in trusted)

        scored = sorted(
            (
                (
                    document.document_id,
                    _lexical_score(telemetry_context, document.text),
                )
                for document in self.catalogue
            ),
            key=lambda item: item[1],
            reverse=True,
        )
        top_document_id = scored[0][0] if scored else None
        top_score = float(scored[0][1]) if scored else 0.0
        second_score = float(scored[1][1]) if len(scored) > 1 else 0.0
        margin = top_score - second_score

        if not trusted:
            return EpistemicGateResult(
                sufficient=False,
                reason="No trusted retrieved evidence is available.",
                top_document_id=top_document_id,
                top_score=top_score,
                second_score=second_score,
                score_margin=margin,
                trusted_provided_document_ids=trusted_ids,
            )

        if top_score < self.config.minimum_top_support:
            return EpistemicGateResult(
                sufficient=False,
                reason=(
                    "Independent catalogue support is below the frozen minimum "
                    f"({top_score:.4f} < {self.config.minimum_top_support:.4f})."
                ),
                top_document_id=top_document_id,
                top_score=top_score,
                second_score=second_score,
                score_margin=margin,
                trusted_provided_document_ids=trusted_ids,
            )

        if margin < self.config.minimum_top_margin:
            return EpistemicGateResult(
                sufficient=False,
                reason=(
                    "Independent catalogue ranking is ambiguous: top-two margin "
                    f"{margin:.4f} is below {self.config.minimum_top_margin:.4f}."
                ),
                top_document_id=top_document_id,
                top_score=top_score,
                second_score=second_score,
                score_margin=margin,
                trusted_provided_document_ids=trusted_ids,
            )

        if (
            self.config.require_provided_top_match
            and top_document_id not in trusted_ids
        ):
            return EpistemicGateResult(
                sufficient=False,
                reason=(
                    "Provided trusted evidence disagrees with the independent "
                    f"catalogue top match ({top_document_id})."
                ),
                top_document_id=top_document_id,
                top_score=top_score,
                second_score=second_score,
                score_margin=margin,
                trusted_provided_document_ids=trusted_ids,
            )

        return EpistemicGateResult(
            sufficient=True,
            reason="Evidence passed frozen sufficiency and agreement checks.",
            top_document_id=top_document_id,
            top_score=top_score,
            second_score=second_score,
            score_margin=margin,
            trusted_provided_document_ids=trusted_ids,
        )
