# Baseline: SANAD v1 in the same staged exercise (10 Nov 2026, 01:22 UTC)

SANAD v1 is the team's earlier French/Arabic legal assistant (generic RAG: hybrid retrieval over field chunks, LLM answer, cite-or-refuse).
It was run through a first version of this sandbox with the same nine citizen questions as `src/lexcivis/governance/resources/events.yaml`.
`answers.json` holds its nine answers as delivered, with the retrieved records. Web links in SANAD's answers are replaced by
`[link removed]`. The full hash-chained log (45 records) is kept outside the repository and is available on request; its
head hash and file SHA-256 are recorded in `answers.json`.

| Stage | Language | SANAD v1 raw outcome |
|---|---|---|
| S1 | fr | answered |
| S1 | ar | refused |
| S2 | fr | refused |
| S2 | ar | answered |
| S3 | fr | refused |
| S4 | ar | refused |
| S4 | fr | refused |
| S5 | fr | answered |
| S6 | fr | refused |

SANAD v1 answered 3 of 9 questions itself; one of them (S2, Arabic) gave a single value although the French and Arabic records disagree.
The twin-check hold shown in the log was added by the sandbox around SANAD, not by SANAD.
