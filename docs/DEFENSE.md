# Interview defense notes

Plain-language notes for explaining design choices. One section per build session.

## Session 1: Foundation

### Request flow

1. A request hits `RequestIdMiddleware`. It reuses a safe incoming `x-request-id` or makes a new one, stores it in a context variable, and echoes it back in the response header.
2. FastAPI routes it. `/health` gets the Mongo wrapper and settings through `Annotated[..., Depends(...)]`, pings the database and returns a small typed response.
3. If anything raises, one handler turns it into `{"error": {"code", "message", "request_id"}}`. Unexpected errors become a generic 500; the real message is never shown or logged.
4. Every log line is JSON with the request ID and conversation ID attached automatically.

LLM call flow: caller builds a provider-neutral `LLMRequest` -> `GeminiClient` checks the dev cache (if on) -> pacer waits for an RPM slot -> SDK call with a timeout -> on 429 switch to the next API key, on other 429/5xx back off with jitter (or the delay the API asks for) -> map the reply back to neutral types -> log model, tokens, thinking tokens and latency.

### Key decisions and why

- **Provider-neutral types plus a `Protocol` interface.** Only `app/llm/` imports the Gemini SDK. The agent in later sessions depends on `LLMClient`, so tests swap in `FakeLLM` and spend no quota.
- **Our own retry layer, SDK retries off.** Two retry layers multiply attempts and hide what happened. One layer means one place to log and cap.
- **Key fallback on 429.** The free tier has small per-key limits; switching keys is quicker than waiting.
- **Pacer before every call.** Prevents 429s instead of only reacting to them.
- **File cache, off by default, bypassable per call.** Saves quota while debugging; evaluation runs pass `use_cache=False` so scores are always real.
- **Pure ASGI middleware, not `BaseHTTPMiddleware`.** Simpler, keeps context variables working, and avoids known streaming issues.
- **Upsert by natural key for seeding.** Running it twice changes nothing; `created_at` is only set on insert.
- **Pydantic models for seed data.** The delinquency stage is derived from days past due, and a mismatch fails validation, so bad fixtures cannot be seeded.
- **`/health` returns 503 when the DB is down**, and the app still starts, so the outage is visible instead of a crash loop.

### Alternatives rejected

- `motor` (deprecated in favour of PyMongo's native async client).
- `google-generativeai` (old SDK; `google-genai` is current).
- LangChain or similar wrappers: too much hidden behaviour for a small, explainable system.
- Redis for caching: extra infrastructure for a dev-only feature.

### Limitations

- The pacer and key index live in memory, so they are per process, not shared across workers.
- Key fallback is sticky until restart.
- No auth on any endpoint yet (out of scope for this project).
- All data is fictional and this is not a compliance system.

### Likely questions

- **How do you test LLM code without calling the API?** `FakeLLM` returns scripted replies, and a fake SDK client tests the real `GeminiClient` paths (retry, key switch, cache, errors).
- **What counts as a retryable error?** 429, 5xx, network and timeout errors. A 400 is a bug in our request, so retrying would only waste quota.
- **How do you avoid leaking secrets?** `SecretStr` in settings, logs record exception types not messages, health shows only booleans, and a test checks the response body for the key and password.
- **Why is the seed idempotent?** So anyone can rerun setup safely; a test runs it twice and checks counts and `created_at`.
- **How would you scale the pacer?** Move the counter to a shared store (for example Redis) or a token-bucket service.
