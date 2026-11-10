import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(os.environ.get("LEXCIVIS_HOME", Path(__file__).resolve().parents[2]))


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    data_path: Path = field(default_factory=lambda: Path(_env("LEXCIVIS_DATA", str(ROOT / "data" / "procedures.json"))))
    verdicts_path: Path = field(default_factory=lambda: Path(_env("LEXCIVIS_VERDICTS", str(ROOT / "data" / "quality" / "verdicts.json"))))
    library_path: Path = field(default_factory=lambda: Path(_env("LEXCIVIS_LIBRARY", str(ROOT / "data" / "documents"))))
    artifacts: Path = field(default_factory=lambda: Path(_env("LEXCIVIS_ARTIFACTS", str(ROOT / "artifacts"))))
    runs: Path = field(default_factory=lambda: Path(_env("LEXCIVIS_RUNS", str(ROOT / "runs"))))
    embed_model: str = field(default_factory=lambda: _env("LEXCIVIS_EMBED_MODEL", "BAAI/bge-m3"))
    rerank_model: str = field(default_factory=lambda: _env("LEXCIVIS_RERANK_MODEL", "BAAI/bge-reranker-v2-m3"))
    device: str = field(default_factory=lambda: _env("LEXCIVIS_DEVICE", "cpu"))
    refuse_below: float | None = field(default_factory=lambda: float(_env("LEXCIVIS_REFUSE_BELOW", "0")) or None)
    llm_backend: str = field(default_factory=lambda: _env("LEXCIVIS_LLM_BACKEND", "openai"))
    llm_base_url: str = field(default_factory=lambda: _env("LEXCIVIS_LLM_BASE_URL", "https://api.groq.com/openai/v1"))
    llm_api_key: str = field(default_factory=lambda: _env("LEXCIVIS_LLM_API_KEY", ""))
    llm_model: str = field(default_factory=lambda: _env("LEXCIVIS_LLM_MODEL", "openai/gpt-oss-120b"))
    today: str = field(default_factory=lambda: _env("LEXCIVIS_TODAY", ""))
    signing_key: Path = field(default_factory=lambda: Path(_env("LEXCIVIS_SIGNING_KEY", str(Path.home() / ".config" / "lexcivis" / "authority_ed25519.pem"))))
    trusted_key: Path = field(default_factory=lambda: Path(_env("LEXCIVIS_TRUSTED_KEY", str(ROOT / "keys" / "authority_ed25519.pub"))))
    signer: str = field(default_factory=lambda: _env("LEXCIVIS_SIGNER", "Data-protection authority (sandbox key)"))

    @property
    def dense_dir(self) -> Path:
        return self.artifacts / "dense"

    @property
    def intent_model(self) -> Path:
        return self.artifacts / "intent.joblib"
