# Resume facts

Only what is built and committed in this repo. Every number cites the saved report it comes from. This is a portfolio simulation on fictional data. It is **not deployed** (Session 7 log), not production-ready, and has no real users or traffic.

## Suggested bullets

- Built an LLM collections-chat agent (Python, FastAPI, Gemini function calling, MongoDB) in which verification, account access, lender plan rules and human handoff are enforced in server code rather than the prompt, with a 5-iteration tool loop and structured refusals.
- Wrote a 38-scenario, 52-turn evaluation harness scored by code checks (no LLM judge). It covers prompt injection, wrong-borrower access, invented policy, paraphrased escalations and balance leaks. The agent went from 37/38 to 38/38 scenarios on the same model and scenario set, with 0 unauthorized actions in both runs. *(Source: `reports/evaluation/comparison.md`, `baseline.md`, `latest.md`.)*
- Added retrieval-augmented policy answers over a local vector store (fastembed ONNX embeddings, NumPy), filtered by lender, with a calibrated score threshold and source citations returned to the UI. *(Calibration: `docs/reports/session3_retrieval_scores.json`.)*
- Benchmarked regex and LLM promise extractors on a held-out set of 24 labelled transcripts: both reached 95.8% exact match, and the LLM reached 100% date F1 against 96.8% for regex. *(Source: `reports/extraction/test.md`.)*
- Built a nightly pipeline (PowerShell and bash) that extracts promises, loads SQLite idempotently and runs SQL reports using CTEs and window functions (`LAG`, `RANK`, running sums), with step timing, fail-fast exit codes and a `/health` status. *(Source: `reports/nightly/2026-11-05_103905/run.json`.)*
- Built a React + TypeScript demo served by FastAPI as one service. An inspector shows each tool call and the server's verdict, and a results view footnotes every figure to its report file. Added per-IP rate limiting, a message length limit and an app-wide daily LLM-call cap with a friendly limit message. *(Live checks: `docs/reports/session7_live_api.txt`.)*
- 351 backend tests with a fake LLM and no API quota spent. Strict TypeScript, type check, lint and production build pass. *(Sources: `docs/reports/session7_pytest.txt`, `docs/reports/session7_frontend_checks.txt`.)*

## Tech list

Python 3.13, FastAPI, Pydantic v2, pydantic-settings, google-genai (Gemini, async, function calling, JSON schema output), MongoDB (pymongo async), SQLite (CTEs, window functions), fastembed (ONNX) + NumPy vector search, pytest + pytest-asyncio, ruff, React 19, TypeScript (strict), Vite, oxlint, Prettier, PowerShell and bash scripting.

## Wording to avoid

- Do not say "production", "deployed", "users", "customers" or "traffic". The project is a local simulation with fictional data.
- The simulated nightly report (5,000 conversations, 2,000 promises, kept rates by lender) is generator output that exercises the SQL at volume. It is **not** a result. Do not quote its kept rates as findings.
- 38/38 is a pass on the developer's own scenario set, not a safety guarantee.

## Not built (keep off the resume)

- Voice or telephony
- PySpark, Databricks, or any distributed data processing
- Deployment, hosting, CI/CD pipelines, or a live public URL
- Authentication or user accounts
- Real payment processing, real credit-bureau reporting, or legal and regulatory compliance controls
- Multi-model comparisons (one model, `gemini-3.5-flash-lite`, for the compared runs)
