# Extraction benchmark: dev-2

- Split: **dev** (20 transcripts), official: False
- Model: `gemini-3.5-flash-lite`, commit `e30bcd152b`
- Pacing: 10 requests/min, 6.5 s between LLM calls
- Started 2026-11-05 04:37 UTC
- An amount or date counts only if exactly right; a wrong value is one FP and one FN.

| Extractor | Entity | Precision | Recall | F1 | TP / FP / FN |
|---|---|---|---|---|---|
| regex | promise_made | 100.0% | 100.0% | 100.0% | 14 / 0 / 0 |
| regex | amount | 100.0% | 100.0% | 100.0% | 13 / 0 / 0 |
| regex | date | 100.0% | 100.0% | 100.0% | 13 / 0 / 0 |
| llm | promise_made | 100.0% | 100.0% | 100.0% | 14 / 0 / 0 |
| llm | amount | 100.0% | 100.0% | 100.0% | 13 / 0 / 0 |
| llm | date | 100.0% | 100.0% | 100.0% | 13 / 0 / 0 |

| Extractor | Exact match | Errors | Latency avg / p95 (ms) | Tokens prompt / output |
|---|---|---|---|---|
| regex | 100.0% | 0 | 0.136 / 0.268 | 0 / 0 |
| llm | 100.0% | 0 | 9,155.495 / 16,493.7 | 8,568 / 642 |

### regex: transcripts not fully correct

- none

### llm: transcripts not fully correct

- none
