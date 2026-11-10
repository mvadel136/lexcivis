import hashlib
from dataclasses import dataclass

from ..catalog import Catalog, Field, Procedure, Record
from ..dialect import expand
from .dense import DenseIndex, Encoder
from .lexical import BM25
from .rerank import Reranker

RRF_K = 60


def lexical_text(r: Record) -> str:
    parts = [r.title, r.title, r.title, r.category, r.ministry, r.get(Field.DESCRIPTION)[:600],
             r.get(Field.USERS)[:200], r.get(Field.DOCUMENTS)[:400]]
    return " \n".join(p for p in parts if p)


def semantic_text(r: Record) -> str:
    description = r.get(Field.DESCRIPTION)[:400]
    return f"{r.title}. {r.category}. {description}".strip()


def rerank_text(r: Record) -> str:
    return f"{r.title} | {r.category} | {r.get(Field.DESCRIPTION)[:300]}"


def verify_text(r: Record, field: Field) -> str:
    detail = r.get(field)[:300] or r.get(Field.DESCRIPTION)[:300]
    return f"{r.title} | {r.category} | {detail}"


def corpus(catalog: Catalog) -> tuple[list[Record], list[str]]:
    records, keys = [], []
    for p in catalog:
        for r in p.records:
            records.append(r)
            keys.append(p.key)
    return records, keys


def fingerprint(records: list[Record]) -> str:
    h = hashlib.sha256()
    for r in records:
        h.update(semantic_text(r).encode("utf-8"))
    return h.hexdigest()[:16]


@dataclass
class Hit:
    procedure: Procedure
    score: float
    rerank: float | None
    lexical_rank: int | None
    dense_rank: int | None
    support: float | None = None


class HybridSearcher:
    def __init__(self, catalog: Catalog, dense: DenseIndex, encoder: Encoder, reranker: Reranker | None,
                 pool: int = 40, rerank_depth: int = 12):
        self.catalog = catalog
        self.records, self.keys = corpus(catalog)
        self.bm25 = BM25([lexical_text(r) for r in self.records])
        self.dense, self.encoder, self.reranker = dense, encoder, reranker
        self.pool, self.rerank_depth = pool, rerank_depth
        if dense.ids != self.keys:
            raise ValueError("dense index does not match the catalog; rebuild it")

    def _ranks(self, ranked: list[tuple[int, float]]) -> dict[str, int]:
        out = {}
        for i, _ in ranked:
            key = self.keys[i]
            if key not in out:
                out[key] = len(out) + 1
        return out

    def search(self, query: str, lang: str, k: int = 5, field: Field | None = None, verify_depth: int = 3) -> list[Hit]:
        expanded = expand(query)
        lexical = self._ranks(self.bm25.top(expanded, self.pool * 2))
        dense = self._ranks(self.dense.top(self.encoder.encode([expanded])[0], self.pool * 2))
        fused = {}
        for key in set(lexical) | set(dense):
            fused[key] = sum(1 / (RRF_K + r[key]) for r in (lexical, dense) if key in r)
        candidates = sorted(fused, key=lambda key: -fused[key])[: self.rerank_depth]
        reranked = {}
        if self.reranker and candidates:
            passages = [rerank_text(self.catalog.get(key).record(lang)) for key in candidates]
            reranked = dict(zip(candidates, self.reranker.score(expanded, passages)))
            candidates.sort(key=lambda key: -reranked[key])
        hits = [Hit(self.catalog.get(key), reranked.get(key, fused[key]), reranked.get(key),
                    lexical.get(key), dense.get(key)) for key in candidates[:k]]
        for hit in hits:
            hit.support = hit.rerank
        if self.reranker and field and hits:
            top = hits[:verify_depth]
            scores = self.reranker.score(expanded, [verify_text(h.procedure.record(lang), field) for h in top])
            for hit, score in zip(top, scores):
                hit.support = max(score, hit.rerank or 0.0)
        return hits
