# Extraction benchmark: dev-1

- Split: **dev** (20 transcripts), official: False
- Model: `gemini-3.5-flash-lite`, commit `e30bcd152b`
- Pacing: 10 requests/min, 6.5 s between LLM calls
- Started 2026-11-05 04:32 UTC
- An amount or date counts only if exactly right; a wrong value is one FP and one FN.

| Extractor | Entity | Precision | Recall | F1 | TP / FP / FN |
|---|---|---|---|---|---|
| regex | promise_made | 100.0% | 100.0% | 100.0% | 14 / 0 / 0 |
| regex | amount | 100.0% | 100.0% | 100.0% | 13 / 0 / 0 |
| regex | date | 100.0% | 100.0% | 100.0% | 13 / 0 / 0 |
| llm | promise_made | 100.0% | 85.7% | 92.3% | 12 / 0 / 2 |
| llm | amount | 100.0% | 92.3% | 96.0% | 12 / 0 / 1 |
| llm | date | 100.0% | 92.3% | 96.0% | 12 / 0 / 1 |

| Extractor | Exact match | Errors | Latency avg / p95 (ms) | Tokens prompt / output |
|---|---|---|---|---|
| regex | 100.0% | 0 | 0.136 / 0.263 | 0 / 0 |
| llm | 90.0% | 0 | 7,223.18 / 11,946.0 | 8,188 / 618 |

### regex: transcripts not fully correct

- none

### llm: transcripts not fully correct

- `ext-11` (vague date ("sometime next week")): got (False, None, None), expected (True, Decimal('100.00'), None)
- `ext-29` (promise with no amount): got (False, None, None), expected (True, None, datetime.date(2026, 11, 6))
