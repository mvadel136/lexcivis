import hashlib
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from lexcivis.answer import Composer, Policy
from lexcivis.catalog import Catalog
from lexcivis.dialect import expand
from lexcivis.intent import IntentClassifier, training_set
from lexcivis.quality import Verdicts
from lexcivis.search.dense import DenseIndex
from lexcivis.search.hybrid import HybridSearcher, corpus, fingerprint, semantic_text
from lexcivis.text import tokens

ROOT = Path(__file__).resolve().parents[1]
DIM = 512


class HashEncoder:
    def encode(self, texts):
        out = np.zeros((len(texts), DIM), dtype=np.float32)
        for row, text in enumerate(texts):
            for tok in tokens(expand(text)):
                out[row, int(hashlib.md5(tok.encode()).hexdigest(), 16) % DIM] += 1.0
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        return out / np.where(norms == 0, 1, norms)


def content(text):
    return {t for t in tokens(text) if len(t) > 3}


class OverlapReranker:
    def score(self, query, passages):
        q = content(expand(query))
        return [len(q & content(p)) / (len(q) or 1) for p in passages]


@pytest.fixture(scope="session")
def catalog():
    return Catalog.load(ROOT / "data" / "procedures.json")


@pytest.fixture(scope="session")
def verdicts():
    return Verdicts.load(ROOT / "data" / "quality" / "verdicts.json")


@pytest.fixture(scope="session")
def intents(catalog):
    texts, labels = training_set(catalog, per_template=4)
    return IntentClassifier.train(texts, labels)


@pytest.fixture(scope="session")
def composer(catalog, verdicts, intents):
    records, keys = corpus(catalog)
    encoder = HashEncoder()
    dense = DenseIndex.build(encoder, [semantic_text(r) for r in records], keys, fingerprint(records))
    searcher = HybridSearcher(catalog, dense, encoder, OverlapReranker())
    return Composer(searcher, intents, verdicts, Policy(refuse_below=0.2, clarify_below=0.0), today=date(2026, 11, 10))
