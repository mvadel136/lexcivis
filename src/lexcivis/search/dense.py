import json
from pathlib import Path
from typing import Protocol

import numpy as np


class Encoder(Protocol):
    def encode(self, texts: list[str]) -> np.ndarray: ...


class SentenceEncoder:
    def __init__(self, model_name: str, device: str = "cpu", batch_size: int = 16):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name, device=device)
        self.batch_size = batch_size

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = self.model.encode(texts, batch_size=self.batch_size, normalize_embeddings=True,
                                    convert_to_numpy=True, show_progress_bar=len(texts) > 64)
        return vectors.astype(np.float32)


class DenseIndex:
    def __init__(self, vectors: np.ndarray, ids: list[str], fingerprint: str = ""):
        self.vectors = vectors.astype(np.float32)
        self.ids = ids
        self.fingerprint = fingerprint

    @classmethod
    def build(cls, encoder: Encoder, texts: list[str], ids: list[str], fingerprint: str) -> "DenseIndex":
        return cls(encoder.encode(texts), ids, fingerprint)

    def save(self, directory: str | Path) -> None:
        d = Path(directory)
        d.mkdir(parents=True, exist_ok=True)
        np.save(d / "vectors.npy", self.vectors.astype(np.float16))
        (d / "ids.json").write_text(json.dumps({"fingerprint": self.fingerprint, "ids": self.ids}), encoding="utf-8")

    @classmethod
    def load(cls, directory: str | Path) -> "DenseIndex":
        d = Path(directory)
        meta = json.loads((d / "ids.json").read_text(encoding="utf-8"))
        return cls(np.load(d / "vectors.npy").astype(np.float32), meta["ids"], meta.get("fingerprint", ""))

    def top(self, query_vector: np.ndarray, k: int) -> list[tuple[int, float]]:
        sims = self.vectors @ query_vector.astype(np.float32)
        k = min(k, len(sims))
        idx = np.argpartition(-sims, k - 1)[:k]
        return sorted(((int(i), float(sims[i])) for i in idx), key=lambda x: -x[1])
