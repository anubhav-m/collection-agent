# Product

<!-- impeccable:product-schema 1 -->

Answers below were taken from `CLAUDE.md` and `frontend/CLAUDE.md` rather than a live interview, as `frontend/CLAUDE.md` directs. Facts marked *(inferred)* are the agent's reading of those files.

## Platform

web

## Users

- **Primary:** a technical reviewer (hiring manager or interviewer) who opens the demo for about two minutes to judge how the agent behaves and whether the claims are backed by evidence.
- **Simulated:** a borrower discussing an overdue loan. The reviewer plays this person using sample borrowers. A real person in this situation may be stressed, so the chat must never shame, alarm or pressure them.

## Product Purpose

A portfolio simulation of a loan collections system. An LLM agent chats with borrowers, verifies identity, explains balances and policy, sets up payment plans within lender rules, and hands off to a person on disputes, hardship, stop-contact requests or failed verification. A nightly pipeline extracts promised payments and builds follow-up and escalation reports. Success for the demo means a reviewer can run a full conversation without instructions and see, next to it, what the server decided and why.

## Positioning

The server, not the model, decides what is allowed: verification, account access, plan rules and escalation are enforced in code, and the inspector makes those decisions visible turn by turn. Every number shown comes from a saved report in the repo. *(inferred)*

## Operating Context

- Opened in a desktop browser by a reviewer, sometimes on a phone. *(inferred)*
- Three jobs: chat as a sample borrower, inspect tool calls, escalation state and policy sources, and read evaluation and nightly report results.
- Backend: FastAPI serves the API and the built app from one origin.

## Capabilities and Constraints

- Two fictional lenders (LND-001 Maple Grove Example Credit, LND-002 Riverbend Sample Finance) and twelve fictional borrowers with DOBs on 1 January and ZIP codes 000xx.
- Per-IP rate limit on chat, 2,000-character message limit, and an app-wide daily cap on LLM calls with a friendly message when it is reached.
- Not deployed. Not a production or legal compliance system.
- Messages render as plain text only. No secrets in frontend code.

## Brand Commitments

- Calm, trustworthy and precise, like a financial operations tool.
- No playful styling, no alarming red, nothing that shames the borrower.
- No other company's name, logo or branding.
- A persistent notice that this is a simulation using fictional data.

## Evidence on Hand

- Evaluation: `reports/evaluation/baseline.json`, `latest.json`, `comparison.md` (38 scenarios).
- Extraction benchmark: `reports/extraction/test.json` (24 held-out transcripts).
- Nightly reports: `reports/nightly/<run>/project.json` and `simulated.json`. Simulated data must always be labelled as simulated.
- No testimonials, users, traffic or deployment exist. None may be shown or implied.

## Product Principles

1. Show the server's decisions, not just the model's words.
2. Every figure links to the report it came from.
3. Calm under stress: the borrower view stays gentle and clear even when escalating or refusing.
4. Self-explanatory in two minutes: sample borrowers and starter messages, no instructions needed.

## Accessibility & Inclusion

WCAG AA contrast, keyboard operable with visible focus, semantic HTML, usable at phone width.
