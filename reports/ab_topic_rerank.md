# Experiment: rerank on the topic only (2026-11-10)

Variant A reranks with the full question. Variant B strips question-type cue words (267 words taken from the
intent templates, e.g. "combien", "coûte", "documents") before reranking.

| Set | A Recall@1 | B Recall@1 | A Recall@3 | B Recall@3 |
|---|---|---|---|---|
| field_questions (55) | 47 | 48 | 49 | 52 |
| procedures_50 (50) | 41 | 40 | 49 | 49 |

Decision: keep A. The difference is within one question on each set and B adds a heuristic.

# Experiment: answer when lexical and dense search agree (2026-11-10)

Rule tested: answer when the reranker score is below the threshold but the top candidate is in the top-k of both
BM25 and dense search (`reports/calibration_agreement.json`).

| k | Extra correct answers (field + procedures sets) | Off-topic questions wrongly answered (of 30) |
|---|---|---|
| 3 | 0 | 4 |
| 10 | 0 | 5 |

Decision: rejected. The reranker threshold alone stays.
