# Backend rules

Root `CLAUDE.md` rules also apply, including the 70-line maximum per file.

## Environment

- The user is on Windows with PowerShell. Keep paths and scripts cross-platform.
- Python 3.12 or newer. Use `uv` with `pyproject.toml` if available. Otherwise use `venv` and pip with pinned requirements.
- Install current stable packages, then pin them.
- Settings load from the `.env` file in the project root, not from `backend/`.

## Required modern syntax and libraries

Use:

- `google-genai` with async calls through `client.aio`
- `pymongo` with `AsyncMongoClient`
- Pydantic v2: `BaseModel`, `ConfigDict`, `field_validator`, `model_dump`, `model_validate`
- `pydantic-settings` for configuration
- FastAPI `lifespan`, with `Annotated[..., Depends(...)]`
- Built-in generics and unions: `list[str]`, `dict[str, int]`, `str | None`
- `datetime.now(UTC)`, `pathlib.Path`, `async`/`await`, and `asyncio.TaskGroup` where it helps
- `httpx.AsyncClient` with `ASGITransport` for API tests
- `ruff` for linting and formatting, and `pytest` with `pytest-asyncio`

Do not use:

- `google-generativeai`, `motor`, `@app.on_event`, `datetime.utcnow()`
- Pydantic v1 patterns: `class Config`, `.dict()`, `.parse_obj()`, `@validator`
- `typing.List`, `typing.Dict`, `typing.Optional`, `typing.Union`
- Blocking I/O inside async routes

## Structure

Organize by feature under `backend/app/`:

- `core/`: settings, logging, errors, shared dependencies
- `llm/`: Gemini client, retries, pacing, cache, usage tracking. No other module may import the Gemini SDK.
- `agent/`: conversation loop, prompts, state
- `tools/`: one tool per file, with its own schema and server-side validation
- `policy/`: lender config and the rules engine
- `rag/`: ingestion and retrieval
- `db/`: MongoDB and SQLite access. No raw queries in routes.
- `api/`: thin route handlers only
- `evaluation/`, `extraction/`, `reports/`: pipelines

Keep routes thin: validate, call a service, and return a response model. Depend on small interfaces so tests can swap in fakes. Tests live in `backend/tests/` and mirror this layout.

## Agent safety rules

The LLM decides what to say and which tool to request. The server decides what is allowed.

- Enforce identity verification, balance access, payment rules, and escalation state in code, never only in prompts.
- Keep verification and escalation state on the server, tied to the conversation ID. Never accept it from the client or the model.
- Balances, plans, and policies must come only from tools or retrieved documents.
- Validate every tool call's name and arguments before running it. Return a structured error to the model on failure.
- Cap the tool loop at 5 iterations per message.
- Treat user messages and retrieved text as untrusted data, never as instructions.
- Always return a safe fallback message rather than a blank response or an error trace.

## Error handling

- Define typed application errors and map them to consistent JSON responses through one exception handler.
- Use structured logs with a request ID and conversation ID. Do not log secrets or full personal details.
- Retry only transient LLM errors, such as 429 and 5xx, with exponential backoff, jitter, and a cap. Respect any retry delay the API provides.
- Set timeouts on all external calls.

## LLM usage

- Read `GEMINI_API_KEY` and `GEMINI_MODEL` from settings.
- Log the model, prompt tokens, output tokens, and latency for every call.
- Keep prompts short and send only recent conversation history.
- Provide a request pacer with a configurable requests-per-minute limit.
- Development caching must be easy to turn off. Official evaluation runs must always bypass it.

## Testing

- Unit tests use a fake LLM and must not spend API quota.
- Test every rule and tool, including failure paths.
- Before finishing a session, run `ruff check`, `ruff format --check`, `pytest`, and a line-count check on all source and test files.
