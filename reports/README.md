# Reports

| File | What it shows | Produced by |
|---|---|---|
| `evaluation.json` | Results on the 50 SANAD procedure questions, the 55 hand-written field questions and the two must-refuse sets, with every failure listed | `lexcivis evaluate` |
| `benchmark_v1_dev_before_tuning.json` | First run of a 200-question benchmark generated from the records (`data/eval/benchmark_v1_dev_*`), before any tuning. It was then used as a development set to improve the training patterns | `lexcivis benchmark` |
| `benchmark_v2.json` | Locked test: 200 questions with new wording, generated and hashed (`benchmark_v2_lock.sha256`) before the tuning, run once at the end, with 95% bootstrap intervals | `lexcivis benchmark` |
| `benchmark_v2_lock.sha256` | SHA-256 of the v2 questions and wording, recorded before tuning | `sha256sum` |
| `calibration_refusal_threshold.json` | First calibration of the refusal threshold (reranker scores of answerable and off-topic questions) | experiment |
| `calibration_support.json` | Calibration after adding field verification (threshold 0.002) | experiment |
| `calibration_agreement.json` | Rejected experiment: answering when lexical and dense search agree | experiment |
| `ab_topic_rerank.md` | Two retrieval ideas tested and rejected, with numbers | experiment |
