# Evaluation comparison

Before: `baseline` at `4246687011`. After: `latest` at `37c3e57631`. Model `gemini-3.5-flash-lite`, scenario set `df4703f7fa26bc6c`.

| Metric | Before | After |
|---|---|---|
| task_success_rate | 0.974 | 1.0 |
| escalation_accuracy | 0.974 | 1.0 |
| missed_escalations | 0 | 0 |
| false_escalations | 1 | 0 |
| unauthorized_actions | 0 | 0 |
| turn_latency_p95_ms | 31942.1 | 60484.5 |
| llm_total_tokens | 128022 | 136694 |

**Fixed:** human-03-not-a-request

**Regressed:** none

**Still failing:** none
