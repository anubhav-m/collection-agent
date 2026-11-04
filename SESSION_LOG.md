# Session log

Claude Code updates this file. See the root `CLAUDE.md` for what each finished entry must record.

Statuses: `PENDING`, `IN PROGRESS`, `BLOCKED`, `DONE`.

| Session | Name | Status |
|---|---|---|
| 1 | Foundation | DONE |
| 2 | Agent, rules, and handoff | DONE |
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

### Session 2: Agent, rules, and handoff

**Status:** DONE, 2026-11-05 01:40 IST (2026-11-04 20:10 UTC)

**What was built**

- `backend/data/lenders/LND-001.json`, `LND-002.json`: one policy file per lender (installment counts, frequencies, minimum payment, latest first-payment day, escalation trigger phrases).
- `app/policy/`: `models.py` (validated `LenderPolicy`), `loader.py` (`PolicyStore`, fails loudly on a bad file), `rules.py` (options and `plan_violations`, all money as `Decimal`), `schedule.py` (due dates), `escalation.py` (phrase matcher).
- `app/tools/`: one file per tool (`verify_borrower`, `get_account`, `get_payment_options`, `create_payment_plan`, `escalate_to_human`), plus `base.py` (context, outcome, schema), `accounts.py` (ownership check), `plan_identity.py` (idempotency key, plan view), `registry.py`.
- `app/agent/`: `state.py` (server-side state), `executor.py` (name/state/argument gates, records every result), `loop.py` (5-iteration cap, fallback), `service.py`, `starter.py`, `history.py` (last 6 turns, signatures kept), `prompts.py`, `handoff.py`, `results.py`, `turn_events.py`.
- `app/db/`: `interfaces.py` (repository protocols), Mongo repos `conversations.py`, `accounts.py`, `plans.py`, `repositories.py`, `records.py`; new indexes in `indexes.py`.
- `app/api/chat.py`: `POST /chat`, `GET /conversations/{id}`; `schemas.py`, `deps.py`.
- `scripts/live_chat.py` + `live_scenarios.py` (live API runs), `scripts/live_guard_check.py` (forced tool calls on a live conversation).

**Commands** (from `backend/`)

```
.venv\Scripts\python -m uvicorn app.main:app --port 8000
.venv\Scripts\python -m scripts.live_chat happy
.venv\Scripts\python -m scripts.live_chat dispute
.venv\Scripts\python -m scripts.live_guard_check <conversation_id>
.venv\Scripts\ruff check . ; .venv\Scripts\ruff format --check . ; .venv\Scripts\python -m pytest -q
```

**Tests and checks (actual results)**

- `pytest -q`: 129 passed in 1.42s (`docs/reports/session2_pytest.txt`). 71 are new this session (58 before). All use `FakeLLM` and in-memory repos; no quota spent.
- `ruff check`: all checks passed. `ruff format --check`: 116 files already formatted.
- Line count: largest files are `create_payment_plan.py`, `live_guard_check.py`, `test_executor.py` at 70. None over 70.
- Behaviours covered by fake-LLM tests: account tools rejected before verification (`tests/agent/test_executor.py`, `test_service_flow.py`); 3 failed attempts escalate and lock (`tests/tools/test_verify_borrower.py`, `test_service_flow.py`); another borrower's account is not reachable (`test_account_tools.py`, `test_create_payment_plan.py`); rule-breaking and wrong-sum plans rejected (`tests/policy/test_rules.py`, `test_create_payment_plan.py`); repeated save is idempotent, including a lost insert race (`test_create_payment_plan.py`, `tests/db/test_plan_repo.py`); escalation by rule, by model and by verification limit, then collection tools rejected (`test_service_escalation.py`); 5-iteration cap, LLM error, blank reply (`test_loop.py`); forbidden actions from the model: unknown tool, smuggled `verified=true` argument, tools after escalation (`test_executor.py`); client cannot send server state (`tests/api/test_chat.py`).

**Done Criteria**

- Fake-LLM tests prove each behaviour: yes, see above.
- Live conversation through the API, `gemini-3.5-flash`, Atlas: verification, balance lookup, plan offer and a saved plan (`PLAN-e8269ff33766e572`, 3 x 283.50 monthly from 2026-11-12 on ACC-1002) (`docs/reports/session2_live_happy.json`, `docs/reports/session2_db_records.json`).
- Live dispute: "I don't owe this money. It is not my debt." escalated by the code rule (reason `dispute`, source `rule`) (`docs/reports/session2_live_dispute.json`). On two follow-up messages asking for a balance and a plan, the live model did not request any tool; it said a person will follow up. So the rejection was proven on the same live, stored conversation by `scripts/live_guard_check.py`, which sends `get_account` and `create_payment_plan` as a misbehaving model would, through the real executor and Atlas state: both rejected with `conversation_escalated`, and no plan exists for ACC-2002 (`docs/reports/session2_live_guard_check.json`). Those calls are stored labelled `[forced by scripts.live_guard_check]`.
- Stored conversation shows messages and tool calls, accepted and rejected with reasons (`docs/reports/session2_live_dispute_stored.json`, and `stored_conversation` in the happy report).
- Live usage: 14 successful Gemini calls (`"llm call"` lines in `docs/reports/session2_server.log`), prompt tokens about 870-1,100 per call. Two 429s switched from key 1 to key 2 and to key 3 during the run. Logs contain no borrower names or dates of birth (grep returned 0).

**Assumptions and decisions**

- Escalation is decided in two layers. Code: every borrower message is matched (case-insensitive, word-boundary, curly apostrophes normalised) against the lender's trigger phrases before the model sees it. A match escalates at once and the reply is a fixed handoff message, with no LLM call. Model: paraphrases the phrases miss ("money has been tight since my surgery") are left to the `escalate_to_human` tool. Code also escalates after the 3rd failed verification. When several categories match, priority is stop_contact, dispute, hardship, human_request.
- Any escalation ends the turn with a fixed handoff message. Later turns still go to the model (so it can answer politely) but collection tools are rejected, and code appends "A person from our team will follow up with you." if the reply does not say it.
- A plan must cover the full account `balance` (not only the past-due amount). Only the full-balance single payment may be below the minimum payment.
- One active plan per account (unique partial index), and an idempotency key from conversation, account and terms. Same terms again returns the saved plan (`already_saved: true`); different terms are rejected as `plan_already_exists`.
- Plan money is stored as decimal strings so cents are exact.
- The 5-iteration cap means at most 5 model calls per turn; tool calls requested on the 5th are recorded as rejected (`tool_iteration_limit`), not executed.
- Arguments that fail validation do not count as a verification attempt; only real mismatches do. Failure messages never say which field was wrong.
- A new conversation needs `lender_id` from the client (which lender's chat). Verification and escalation state are never accepted from the client (`extra="forbid"` on the request).
- Thought signatures are stored with tool calls (binary in Mongo) so history replays work, and are hidden from `GET /conversations`.
- The server uses the UTC date as "today" for plan rules.

**Known issues / later**

- No authentication: anyone with a conversation ID can read it. Out of scope for this simulation.
- Event order relies on ObjectId order, which holds within one server process. Concurrent messages on one conversation are not serialised.
- The phrase matcher can over-escalate (for example "manager" in an unrelated sentence) and misses paraphrases; the model layer covers some of those. Session 4 evaluation should measure both.
- Verification arguments (name, date of birth) are stored in the event log as sent. They are fictional and are not logged.
- The live model never attempted a tool after escalation, so the live rejection proof uses forced calls, as described above.

**Commit:** recorded below after committing.
