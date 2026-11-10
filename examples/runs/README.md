# Example runs

| Run | Agents | Notes |
|---|---|---|
| `20261110T144019Z-dcb553` | written playbook (offline, reproducible) | One named human decision appended at the end (seq 52: takedown approved), then re-signed |
| `20261110T144124Z-453f29` | LLM agents (`groq:openai/gpt-oss-120b`), prompt hash and raw output in each decision | Same stages and questions |

Each folder holds `ledger.jsonl` (hash chain), `ledger.head`, `ledger.sig` (Ed25519 signature of the head),
`results.json` and `case_brief.md`. Check them with `lexcivis verify examples/runs/<run>/ledger.jsonl`; the trusted
public key is `keys/authority_ed25519.pub`.
