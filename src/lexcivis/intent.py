import random
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import joblib
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from .catalog import Catalog, Field
from .text import normalize

OVERVIEW = "overview"


def templates() -> dict:
    text = resources.files("lexcivis.resources").joinpath("intents.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text)


def _subjects(catalog: Catalog, lang: str, rng: random.Random, n: int) -> list[str]:
    titles = [p.title(lang) for p in catalog if p.record(lang) and p.record(lang).lang == lang]
    rng.shuffle(titles)
    return [t.lower().rstrip(" .") for t in titles[:n]]


def training_set(catalog: Catalog, per_template: int = 12, seed: int = 7) -> tuple[list[str], list[str]]:
    rng = random.Random(seed)
    subjects = {"fr": _subjects(catalog, "fr", rng, 400), "ar": _subjects(catalog, "ar", rng, 400)}
    subjects["hassaniya"] = subjects["ar"][:200] + subjects["fr"][:200]
    texts, labels = [], []
    for label, by_lang in templates().items():
        for lang, patterns in by_lang.items():
            for pattern in patterns:
                for subject in rng.sample(subjects[lang], per_template):
                    text = pattern.format(x=subject)
                    texts.append(text + rng.choice(["", " ?", "؟", " svp", " s'il vous plaît"] if lang != "ar" else ["", "؟", " من فضلك"]))
                    labels.append(label)
    return texts, labels


@dataclass
class Intent:
    label: str
    confidence: float

    @property
    def field(self) -> Field | None:
        return None if self.label == OVERVIEW else Field(self.label)


class IntentClassifier:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline

    @classmethod
    def train(cls, texts: list[str], labels: list[str]) -> "IntentClassifier":
        features = FeatureUnion([
            ("chars", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True, preprocessor=normalize)),
            ("words", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True, preprocessor=normalize)),
        ])
        model = LogisticRegression(C=6.0, max_iter=3000, class_weight="balanced")
        pipeline = Pipeline([("features", features), ("model", model)])
        pipeline.fit(texts, labels)
        return cls(pipeline)

    def predict(self, text: str) -> Intent:
        probs = self.pipeline.predict_proba([text])[0]
        best = probs.argmax()
        return Intent(str(self.pipeline.classes_[best]), float(probs[best]))

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, path)

    @classmethod
    def load(cls, path: str | Path) -> "IntentClassifier":
        return cls(joblib.load(path))
