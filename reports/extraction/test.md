# Extraction benchmark: test

- Split: **test** (24 transcripts), official: True
- Model: `gemini-3.5-flash-lite`, commit `b58f41cd2a`
- Pacing: 10 requests/min, 6.5 s between LLM calls
- Started 2026-11-05 04:45 UTC
- An amount or date counts only if exactly right; a wrong value is one FP and one FN.

| Extractor | Entity | Precision | Recall | F1 | TP / FP / FN |
|---|---|---|---|---|---|
| regex | promise_made | 100.0% | 94.1% | 97.0% | 16 / 0 / 1 |
| regex | amount | 100.0% | 94.1% | 97.0% | 16 / 0 / 1 |
| regex | date | 100.0% | 93.8% | 96.8% | 15 / 0 / 1 |
| llm | promise_made | 100.0% | 94.1% | 97.0% | 16 / 0 / 1 |
| llm | amount | 100.0% | 94.1% | 97.0% | 16 / 0 / 1 |
| llm | date | 100.0% | 100.0% | 100.0% | 16 / 0 / 0 |

| Extractor | Exact match | Errors | Latency avg / p95 (ms) | Tokens prompt / output |
|---|---|---|---|---|
| regex | 95.8% | 0 | 0.164 / 0.311 | 0 / 0 |
| llm | 95.8% | 0 | 4,254.008 / 7,573.1 | 10,270 / 772 |

### regex: transcripts not fully correct

- `ext-19` ("1.5k", "December 1st"): got (False, None, None), expected (True, Decimal('1500.00'), datetime.date(2026, 12, 1))

### llm: transcripts not fully correct

- `ext-40` ("payday" with no known date): got (False, None, None), expected (True, Decimal('200.00'), None)
