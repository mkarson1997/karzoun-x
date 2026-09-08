from __future__ import annotations

import math
import re
from dataclasses import dataclass

from karzoun_x.types import RetrievedEvidence

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_\-]+")


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in _TOKEN_RE.findall(text)}


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    document_id: str
    text: str


class LocalRetriever:
    """Small deterministic lexical retriever for early experiments.

    It is dependency-light on purpose. Future benchmark tracks can add embedding retrieval.
    """

    def __init__(self, documents: list[KnowledgeDocument]) -> None:
        self.documents = documents

    def search(self, query: str, top_k: int = 3) -> list[RetrievedEvidence]:
        q = _tokens(query)
        if not q:
            return []
        scored: list[RetrievedEvidence] = []
        for doc in self.documents:
            d = _tokens(doc.text)
            if not d:
                continue
            overlap = len(q & d)
            score = overlap / math.sqrt(len(q) * len(d))
            if score > 0:
                scored.append(
                    RetrievedEvidence(
                        document_id=doc.document_id,
                        text=doc.text,
                        score=float(score),
                    )
                )
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]
