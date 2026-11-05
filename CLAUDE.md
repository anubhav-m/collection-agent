# Collections AI Agent

A portfolio simulation of a loan collections system. An LLM agent handles borrower chats. A nightly pipeline extracts promised payments and creates follow-up and escalation reports. All data is fictional. This is not a production or legal compliance system.

## Session workflow

The project is built in sessions defined in `PROMPTS.md`, with progress tracked in `SESSION_LOG.md`.

When the user says "run the next session" or similar:

1. Read `SESSION_LOG.md` and find the first session marked `PENDING`.
2. Read only that session in `PROMPTS.md`, plus the CLAUDE.md for each area it touches.
3. Mark it `IN PROGRESS` in the log, then build it.
4. Verify every item in its Done Criteria by running the code.
5. Update the log, append to `docs/DEFENSE.md`, and commit.
6. Stop. Run only one session per Claude Code session, then tell the user to start a fresh session.

If the log shows a session `IN PROGRESS` or `BLOCKED`, resume it instead of starting a new one. Inspect the code and git history first, and do not redo finished work.

## SESSION_LOG.md rules

Each finished session entry must record:

- Status, and date and time
- What was built, and the key files
- Commands to run it
- Tests run, with actual results
- Real metrics, with the path of the report they came from
- Assumptions and decisions made
- Known issues, and anything left for later

- The commit hash

Mark a session `DONE` only if all its Done Criteria pass. Otherwise use `BLOCKED` and state exactly why and what is needed.

## docs/DEFENSE.md rules

After each session, append simple-language notes the user can use in an interview: the request flow, why each main decision was made, the alternatives rejected, the limitations, and likely interview questions with short answers.

## Working style

- Move fast. Make reasonable assumptions, record them in the log, and keep going.
- Ask the user only when you need a secret or connection string, access to an external account, or a decision that is hard to undo or changes the project's direction.
- Do not ask for approval of folder structure, libraries, naming, or routine design choices.
- Do not add features outside the current session.
- Fix the root cause of a failure. Do not hide errors or work around tests.

## Code standards

- Aim for 50-70 lines or fewer in every source and test file, with 70 as a hard maximum. If a file grows past that, split it by responsibility. Shorter files are fine, so never pad one.
- This limit does not apply to generated files, lockfiles, Markdown, or fixture and data files. Split large fixtures into several files anyway.
- One responsibility per file. Work component by component, with clear interfaces between modules.
- Use descriptive names and only comment on non-obvious reasoning.
- Handle errors deliberately. Never swallow an exception, and never show a stack trace or secret to a user.
- Use the current stable versions and current syntax. Check the installed version or official docs when unsure. Do not use deprecated APIs.

## Honesty rules

- Use clearly fictional data only.
- Never fake data, metrics, passing tests, or deployment status.
- Every metric in the README, log, or `RESUME_FACTS.md` must come from a saved report in the repo.
- Never weaken, delete, or special-case tests or evaluation scenarios to raise a score. If a scenario is genuinely wrong, record the change and the reason in the log.
- Do not imply the project is production-ready or affiliated with any company. Do not use another company's name, branding, or product names.

## Security and git

- Never print, log, or commit secrets. `.env` must stay in `.gitignore`, and `.env.example` must contain placeholders only.
- Keep the existing `.env` in the project root. If a required value is missing, tell the user the exact variable name.
- Make 1-2 commits per session, using Conventional Commits with clear messages.
- Never add a `Co-Authored-By` trailer or any Claude/AI attribution to commit messages.
- Do not create branches. Commit directly to `main` and push to `origin` (`git@github.com:anubhav-m/collection-agent.git`) at the end of each session.
- Do not deploy until a session calls for it and the user has supplied what's needed.

## API quota

- The project uses one Gemini model on a free tier, set by `GEMINI_MODEL` in `.env`. Since Session 4 it is `gemini-3.5-flash-lite`: 15 requests per minute, 250K tokens per minute and 500 requests per day per project (AI Studio dashboard, 2026-11-05). `gemini-3.5-flash` allows only 20 requests per day, too few for an evaluation run. Limits are per project and per model, and the daily quota resets at midnight Pacific time. Treat the user's AI Studio dashboard as authoritative.
- Keep the same model for runs that will be compared. Session 4's reports are on `gemini-3.5-flash-lite`.
- A full evaluation run (38 scenarios) uses about 100 calls. Estimate calls before any live run.
- Use mocked LLM responses in unit tests. Run only a few live scenarios while debugging.
- `.env` holds `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2` and `GEMINI_API_KEY_3`. The client (`app/llm/key_pool.py`) moves to the next key on a 429. A per-day 429 retires that key for the day. A per-minute 429 rests the key for up to 60 s, then it is used again.

## Stack

Python, FastAPI, Gemini, MongoDB, SQLite, a local vector store, and React with TypeScript. See `backend/CLAUDE.md` and `frontend/CLAUDE.md`.
