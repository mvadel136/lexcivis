import math
from collections import Counter, defaultdict

from ..text import tokens


class BM25:
    def __init__(self, documents: list[str], k1: float = 1.4, b: float = 0.75):
        self.k1, self.b = k1, b
        self.doc_tokens = [Counter(tokens(d)) for d in documents]
        self.lengths = [sum(t.values()) for t in self.doc_tokens]
        self.avg_length = sum(self.lengths) / max(len(self.lengths), 1)
        df = Counter(term for t in self.doc_tokens for term in t)
        n = len(documents)
        self.idf = {term: math.log(1 + (n - f + 0.5) / (f + 0.5)) for term, f in df.items()}
        self.postings = defaultdict(list)
        for i, t in enumerate(self.doc_tokens):
            for term, tf in t.items():
                self.postings[term].append((i, tf))

    def scores(self, query: str) -> dict[int, float]:
        out = defaultdict(float)
        for term in set(tokens(query)):
            idf = self.idf.get(term)
            if idf is None:
                continue
            for i, tf in self.postings[term]:
                norm = tf + self.k1 * (1 - self.b + self.b * self.lengths[i] / self.avg_length)
                out[i] += idf * tf * (self.k1 + 1) / norm
        return out

    def top(self, query: str, k: int) -> list[tuple[int, float]]:
        return sorted(self.scores(query).items(), key=lambda x: -x[1])[:k]
