FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1 LEXCIVIS_HOME=/app HF_HOME=/models
WORKDIR /app

RUN pip install --index-url https://download.pytorch.org/whl/cpu torch
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install .
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; SentenceTransformer('BAAI/bge-m3'); CrossEncoder('BAAI/bge-reranker-v2-m3')"

COPY data ./data
COPY artifacts ./artifacts
COPY web ./web
COPY keys ./keys

EXPOSE 8080
CMD ["lexcivis", "serve", "--host", "0.0.0.0", "--port", "8080"]
