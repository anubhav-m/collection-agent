# Build sessions

Run one session per Claude Code session. Each session must leave working, committed code. Follow the root `CLAUDE.md` for the workflow, the log, and the rules. Do not repeat those rules here or ignore them.

**The product in one line:** a simulated loan collections system in which an LLM agent handles borrower chats, then a nightly pipeline extracts promised payments and creates follow-up and escalation reports.

**Out of scope:** voice, PySpark, Databricks, MCP, user login systems, and real payments.

---

## Session 1: Foundation

**Goal:** A clean, running backend that every later session can build on.

**Build:**

1. Set up the repo: `backend/`, `frontend/` (empty for now), `docs/`, `.gitignore`, and `.env.example`. Initialize git if needed. Check that `.env` is ignored before the first commit, and check that `test_gemini.py` contains no key.
2. Create the `core/` module: typed settings, structured logging with request IDs, typed errors, and one exception handler.
3. Create the `llm/` module: an async Gemini client behind a small interface, with retries, a pacer, a switchable development cache, and token and latency logging. Provide a fake LLM for tests. Include function-calling support.
4. Create the `db/` module: an async MongoDB connection with indexes, and clean startup and shutdown through `lifespan`.
5. Add fictional seed data with one idempotent command: 2 fictional lenders, at least 10 borrowers, and accounts covering different balances and delinquency stages. Include clearly fake dates of birth and ZIP codes.
6. Add `GET /health`, which reports app and database status without exposing secrets.

**You may ask the user for:** `MONGODB_URI`, only if it's missing from `.env`. Try a local MongoDB on the default port first. Tell the user that a free MongoDB Atlas cluster also works, and will be needed for deployment.

**Done Criteria:**

- The server starts, and `/health` reports the database as connected.
- The seed command runs twice without creating duplicates.
- One live Gemini call succeeds through the `llm/` module and logs its token usage.
- Unit tests pass using the fake LLM.
- `git status` shows that `.env` isn't tracked.

---

## Session 2: Agent, rules, and handoff

**Goal:** One complete borrower conversation works from verification through a saved payment plan.

**Build:**

1. Create the `policy/` module: a lender config file per lender (allowed plan lengths, minimum payment, escalation triggers), and a rules engine that reads it. Changing a lender's rules must not require a code change.
2. Create one tool per file in `tools/`: `verify_borrower`, `get_account`, `get_payment_options`, `create_payment_plan`, and `escalate_to_human`.
3. Create the `agent/` module: the tool-calling loop, a short system prompt, and server-side conversation state.
4. Add `POST /chat` and `GET /conversations/{id}`. Store every message and tool call in MongoDB, including rejected tool calls and the reason.

**Required behavior, all enforced on the server:**

- No account detail is available before verification succeeds. Limit failed attempts to 3 per conversation, then escalate.
- A verified conversation can reach only that borrower's account.
- `create_payment_plan` accepts only plans that the rules engine allows and that add up to the correct balance.
- Saving a plan is idempotent, so a repeated tool call can't create a duplicate.
- Disputes, hardship, stop-contact requests, and requests for a person escalate. After escalation, no further collection or plan tools can run in that conversation, and the agent tells the borrower that a person will follow up.
- Each turn is capped at 5 tool iterations, and LLM failures return a safe fallback message.

Decide escalation in code as well as by LLM where it can be done reliably, and record the approach in the log.

**Done Criteria:**

- Tests with the fake LLM prove each required behavior, including an LLM that requests a forbidden action.
- A live conversation through the API completes verification, balance lookup, plan offer, and a saved plan.
- A live dispute message escalates, and collection tools are then rejected.
- The stored conversation shows the messages and tool calls.

---

## Session 3: RAG

**Goal:** Policy questions are answered only from retrieved documents, with sources.

**Build:**

1. Write 5 short fictional policy documents in `backend/data/policies/`: hardship options, payment methods, disputes, contact preferences, and fees. Attach each to a lender or mark it as shared.
2. Create the `rag/` module: chunking, local embeddings, a local vector store, and an idempotent ingestion command. Use a lightweight ONNX embedding library such as `fastembed`, not PyTorch, so the app fits on a small free host. No embedding call may use Gemini quota.
3. Add a `search_policy` tool that retrieves for the borrower's lender only and returns text, document title, and score.
4. Update the agent to use the tool for policy questions and to include sources in the API response.

**Required behavior:**

- If the top result is below a score threshold, the agent says it doesn't have that information or escalates, and doesn't guess.
- Retrieved text is treated as data, and an instruction hidden inside a document must not change the agent's behavior. Add a test for this.
- A policy can never override the server's rules engine.

**Done Criteria:**

- Retrieval tests pass for relevant, irrelevant, and wrong-lender queries, without calling Gemini.
- A live policy question returns an answer with its source.
- A live question with no matching policy doesn't invent an answer.
- Earlier tests still pass.

---

## Session 4: Evaluation and fixes

**Goal:** Real, reproducible numbers showing how the agent behaves, before and after real fixes.

**Build:**

1. Create at least 30 scenarios as data files, covering: normal plans, failed verification, wrong-borrower attempts, disputes, stop-contact requests, hardship, requests for a person, prompt injection, off-topic messages, invented-policy attempts, and policy questions. Include at least 3 per category that apply, and include hard cases. Write them before looking at agent failures.
2. Score with code checks on the tool-call trace, the database state, and the reply, such as "`create_payment_plan` wasn't called" or "reply contains no balance before verification". Do not use an LLM judge, which saves quota and keeps the results repeatable.
3. Build a runner with one command that writes JSON and Markdown reports containing: pass or fail with reasons per scenario, task success rate, escalation accuracy, unauthorized-action count, average and p95 latency, token usage, model name, git commit, and scenario count.
4. Make runs resumable by saving after every scenario, so a quota limit doesn't lose work. A resumed run must use the same model and commit. Official runs must bypass the cache and use a fresh database state per scenario.

**Then:**

5. Before the first full run, estimate its calls against the quota, and tell the user the estimate. Run all scenarios and save the report to `reports/evaluation/baseline.json` and `.md`. Never overwrite the baseline, even if it scores low.
6. Fix real failures in the agent's logic, tools, or prompts, using only the failing scenarios while debugging. Don't add logic that detects specific scenario text.
7. Run all scenarios again as a final official run on the same model, and save it to `reports/evaluation/latest.json` and `.md`, plus a before-and-after comparison.

If the daily quota runs out, save progress and mark the session `BLOCKED`, stating that it resumes after the daily reset. Only full runs on the same model and scenario set can be compared. The user may decide to continue with Session 5 meanwhile, and the before-and-after numbers can follow later.

**Done Criteria:**

- The baseline report exists, and every scenario has a result.
- The comparison comes from two complete runs on the same model and scenarios, or the log clearly says the second run is pending.
- Any remaining failures are listed honestly with their reasons.
- Any change to a scenario is recorded in the log with its reason.

---

## Session 5: Entity extraction

**Goal:** After each call, structured data is pulled from the conversation, with measured accuracy.

**Build:**

1. Create at least 40 fictional transcripts with hand-written labels for promised payment dates, amounts, and whether a payment promise was made. Include hard cases: "next Friday", "two hundred bucks", changed amounts, and no promise at all. Labels are stored separately from transcripts.
2. Split them into a development set and a held-out test set before writing any extractor. Tune only on the development set.
3. Create the `extraction/` module with two extractors behind one interface: regex with date and number normalization, and LLM with structured output validated by Pydantic. Each transcript needs a fixed reference date for relative dates.
4. Build a benchmark that reports precision, recall, and F1 for each entity type and extractor on the test set, plus latency and tokens. Write it to `reports/extraction/` as JSON and Markdown.
5. Add a command that runs the chosen extractor on stored conversations and saves results to MongoDB. Record which extractor you chose and why, based on the results.

**Done Criteria:**

- Metric calculations have unit tests with known answers.
- The benchmark report comes from a real run on the held-out test set.
- Extraction runs on stored conversations and saves results.
- Quota use is paced and logged.

---

## Session 6: Reports and automation

**Goal:** A nightly job turns conversations into reports that a collections team would use.

**Build:**

1. Create the `reports/` module: a SQLite schema with `lenders`, `borrowers`, `conversations`, `promises`, `payments`, and `escalations`, and a loader that moves data from MongoDB and extraction results into it. Make the load idempotent.
2. Add a fictional data generator for a larger history, such as 5,000 conversations and 2,000 promises, with a fixed random seed. Mark generated rows clearly as simulated, and keep them separate from real project evaluation numbers.
3. Write SQL reports as `.sql` files using joins, CTEs, and window functions, answering:
   - Which promises are due or overdue and need follow-up?
   - What is the promise-kept rate by lender and by week, with a week-over-week change?
   - What are the top escalation reasons per lender?
   - How do borrowers rank by amount overdue within each lender?
4. Add a nightly job in two thin versions, `scripts/nightly.sh` and `scripts/nightly.ps1`, that runs extraction, load, and reports. It should stop on failure, log each step with timing, return a non-zero exit code on failure, and write dated output to `reports/nightly/`.
5. Add a `/reports` API that returns the latest report data, and extend `/health` with the last nightly run status.

**Done Criteria:**

- SQL reports have tests on a small fixture with known answers.
- The PowerShell job runs end to end here, and a failed step is reported correctly.
- The bash script passes a syntax check, and is run if bash is available.
- Reports are generated from a real run.

---

## Session 7: Frontend and resume facts

**Goal:** A working demo link, a clear README, and resume claims backed by evidence.

Read `frontend/CLAUDE.md` first.

**Build:**

1. Build the React app using Impeccable: a chat view with sample borrowers, an inspector panel showing tool calls, escalation state, and policy sources, and a results view showing real evaluation and report data.
2. Have FastAPI serve the built frontend, so the app deploys as one service with no CORS setup.
3. Add production safeguards: per-IP rate limits and a message length limit on `/chat`, a daily app-wide cap on LLM calls so a public demo can't use up the quota, and a friendly message when the cap is reached.
4. Write the README: the problem, an architecture diagram in Mermaid, setup, how to run the evaluation and the nightly job, real results with links to reports, limitations, and a clear statement that this is a simulation using fictional data and isn't a production or legal compliance system.
5. Write `RESUME_FACTS.md`: suggested resume bullets and a tech list, using only what's built, and citing the report behind each number. List separately anything not built, so it stays off the resume, including voice, PySpark, and Databricks. Do not call the project production-ready or describe simulated data as real traffic.


**Before pushing, verify:** the git history contains no secrets, `.env` isn't tracked, and no file contains a real key.

**Done Criteria:**

- Type check, lint, build, and all backend tests pass.
- A full demo conversation works in the browser locally.
- Every number in the README and `RESUME_FACTS.md` matches a saved report.
- If deployed, the live URL is tested with a full conversation and `/health`. If not, the log says "not deployed" and `RESUME_FACTS.md` doesn't claim it.
