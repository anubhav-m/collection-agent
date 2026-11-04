# Session log

Claude Code updates this file. See the root `CLAUDE.md` for what each finished entry must record.

Statuses: `PENDING`, `IN PROGRESS`, `BLOCKED`, `DONE`.

| Session | Name | Status |
|---|---|---|
| 1 | Foundation | DONE |
| 2 | Agent, rules, and handoff | PENDING |
| 3 | RAG | PENDING |
| 4 | Evaluation and fixes | PENDING |
| 5 | Entity extraction | PENDING |
| 6 | Reports and automation | PENDING |
| 7 | Frontend, deployment, and resume facts | PENDING |

## Entries

### Session 1: Foundation

**Status:** DONE, 2026-11-05 01:21 IST (2026-11-04 19:51 UTC)

**What was built**

- Repo layout: `backend/`, `frontend/` (only its CLAUDE.md), `docs/`, `.gitignore`, `.gitattributes`, `.env.example` (placeholders only).
- `backend/app/core/`: typed settings (`settings.py`), JSON logging with request and conversation IDs (`logging.py`, `context.py`, `request_id.py`), typed errors (`errors.py`), one exception handler for app, HTTP, validation and unexpected errors (`handlers.py`), shared deps (`deps.py`).
- `backend/app/llm/`: neutral types (`types.py`), `LLMClient` protocol (`interface.py`), async Gemini client with key fallback (`gemini_client.py`), SDK mapping with function calling and thought signatures (`gemini_mapping.py`), retries (`retry.py`), RPM pacer (`pacer.py`), switchable file cache (`cache.py`), `FakeLLM` (`fake.py`), `build_llm` (`factory.py`).
- `backend/app/db/`: `AsyncMongoClient` wrapper (`mongo.py`), indexes (`indexes.py`), validated record models (`models.py`), fictional seed data (`seed_data/`), idempotent seed command (`seed.py`).
- `backend/app/api/health.py` and `backend/app/main.py` (lifespan startup and shutdown).
- `backend/scripts/llm_smoke.py`: one live text call and one function-calling call.

**Commands** (from `backend/`, venv at `backend/.venv`)

```
python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m app.db.seed
.venv\Scripts\python -m uvicorn app.main:app --port 8000
.venv\Scripts\python -m scripts.llm_smoke
.venv\Scripts\ruff check . ; .venv\Scripts\ruff format --check . ; .venv\Scripts\python -m pytest -q
```

**Tests and checks (actual results)**

- `pytest -q`: 57 passed in 1.06s (`docs/reports/session1_pytest.txt`). All use `FakeLLM` or a fake SDK client; no quota spent.
- `ruff check`: all checks passed. `ruff format --check`: 55 files already formatted.
- Line count: largest files are `gemini_client.py` (70), `retry.py` (68), `gemini_mapping.py` (68). None over 70.

**Done Criteria**

- Server starts and `/health` returns 200 with `"database":"connected"` (`docs/reports/session1_health.txt`, `docs/reports/session1_server.log`).
- Seed run twice: first run inserted 2 lenders, 12 borrowers, 14 accounts; second run inserted 0 and totals stayed 2/12/14 (`docs/reports/session1_seed_rerun.json` is the rerun output).
- Live Gemini calls succeeded through `app.llm` with `gemini-3.5-flash`: text call 6 prompt / 1 output / 65 thinking tokens, 3738 ms; tool call returned `get_fictional_balance(account_id="ACC-1001")`, 69 / 27 / 99 tokens, 1484 ms (`docs/reports/session1_llm_smoke.json`, `.log`). 4 live requests were used in total this session (2 smoke runs).
- Unit tests pass with the fake LLM (57 passed).
- `git check-ignore -v .env` matches `.gitignore:2`; `.env` is not tracked.

**Assumptions and decisions**

- `.env` holds `GEMINI_API_KEY_1..3`, not `GEMINI_API_KEY` as `backend/CLAUDE.md` says. Settings read the three slots and use them in order; a 429 switches to the next key at once. The switch is sticky for the process lifetime.
- `test_gemini.py` does not exist anywhere in the repo, so there was nothing to scrub. A scan for Gemini key prefixes outside `.env` found nothing.
- `MONGODB_URI` in `.env` points to MongoDB Atlas, and all runs used Atlas (verified: 3 nodes, all `*.mongodb.net`, 14 accounts). Local MongoDB is not used. After the user said they do not want local, the `localhost` default was removed: `MONGODB_URI` is now required, and the app fails at startup if it is missing.
- No `uv` installed, so venv + pip with a frozen `requirements.txt`.
- SDK-level retries are disabled (`HttpRetryOptions(attempts=1)`) so our retry layer is the only one. Retry delay from the API's `RetryInfo` is respected, capped at 60s.
- `/health` returns 503 when the database is down so probes can detect it. The app still starts without a database.
- Thinking tokens are logged separately because Gemini counts them in the total.
- Seed records upsert by natural key (`lender_id`, `borrower_id`, `account_id`) with `$setOnInsert` for `created_at`.
- Fake personal data: every date of birth is 1 January; ZIP codes are `00001`-`00012` (unassigned range). Lender names are invented.
- Remote `main` already had a GitHub "Initial commit" with a one-line README; work was committed on top of it, not force-pushed.

**Known issues / later**

- Uvicorn's own access logs are plain text, not JSON.
- The dev cache key includes the whole request; it is off by default (`LLM_CACHE_ENABLED=false`).
- `frontend/` is empty until Session 7.

**Commit:** `7f3356b` (feat), followed by a docs commit that records this hash. Pushed to `origin/main`.
