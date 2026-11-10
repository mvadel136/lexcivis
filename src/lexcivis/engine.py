import hashlib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from . import __version__
from .answer import Composer, Policy
from .catalog import Catalog
from .intent import IntentClassifier, training_set
from .quality import Verdicts
from .search.dense import DenseIndex, SentenceEncoder
from .search.hybrid import HybridSearcher, corpus, fingerprint, semantic_text
from .search.rerank import CrossEncoderReranker
from .settings import Settings


@dataclass
class Engine:
    settings: Settings
    catalog: Catalog
    verdicts: Verdicts
    composer: Composer
    provenance: dict = field(default_factory=dict)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ml_intent() -> dict:
    from importlib import resources

    import yaml

    return yaml.safe_load(resources.files("lexcivis.governance.resources").joinpath("ml_intent.yaml").read_text(encoding="utf-8"))


def policy(settings: Settings) -> Policy:
    p = dict(ml_intent()["pipeline"])
    if settings.refuse_below is not None:
        p["refuse_below"] = settings.refuse_below
    return Policy(**p)


def provenance(settings: Settings, dense_fingerprint: str) -> dict:
    return {"lexcivis": __version__, "data_sha256": sha256(settings.data_path),
            "verdicts_sha256": sha256(settings.verdicts_path) if settings.verdicts_path.exists() else "",
            "intent_model_sha256": sha256(settings.intent_model), "dense_fingerprint": dense_fingerprint,
            "embed_model": settings.embed_model, "rerank_model": settings.rerank_model,
            "policy": policy(settings).__dict__}


def build_artifacts(settings: Settings, encoder=None) -> dict:
    catalog = Catalog.load(settings.data_path)
    records, keys = corpus(catalog)
    encoder = encoder or SentenceEncoder(settings.embed_model, settings.device)
    DenseIndex.build(encoder, [semantic_text(r) for r in records], keys, fingerprint(records)).save(settings.dense_dir)
    texts, labels = training_set(catalog)
    IntentClassifier.train(texts, labels).save(settings.intent_model)
    return {"records": len(records), "intent_examples": len(texts)}


def load_engine(settings: Settings | None = None, encoder=None, reranker=None, use_reranker: bool = True) -> Engine:
    settings = settings or Settings()
    catalog = Catalog.load(settings.data_path)
    verdicts = Verdicts.load(settings.verdicts_path)
    dense = DenseIndex.load(settings.dense_dir)
    records, _ = corpus(catalog)
    if dense.fingerprint != fingerprint(records):
        raise RuntimeError("artifacts are out of date: run `lexcivis build`")
    encoder = encoder or SentenceEncoder(settings.embed_model, settings.device)
    if reranker is None and use_reranker:
        reranker = CrossEncoderReranker(settings.rerank_model, settings.device)
    searcher = HybridSearcher(catalog, dense, encoder, reranker)
    today = date.fromisoformat(settings.today) if settings.today else None
    composer = Composer(searcher, IntentClassifier.load(settings.intent_model), verdicts, policy(settings), today)
    return Engine(settings, catalog, verdicts, composer, provenance(settings, dense.fingerprint))
