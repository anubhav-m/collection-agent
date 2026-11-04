# Frontend rules

Root `CLAUDE.md` rules also apply, including the 70-line maximum per file.

## Stack

- React with TypeScript in strict mode, built with Vite. Use current stable versions.
- Function components and hooks only. Use `createRoot`.
- Use native `fetch` in one API module, and keep state in hooks. Add a state library only if a real need appears.
- Do not use class components, `defaultProps`, Create React App, or `any`.
- Types for API responses live in one file and must match the backend's response models.

## Design with Impeccable

Use the Impeccable skill for all visual and interface work.

- Check that it is available before starting the UI. If it isn't, stop and ask the user to run `npx impeccable install` from the project root and reload Claude Code.
- Run `/impeccable init` once to create `PRODUCT.md`, answering its questions yourself from this file and the root `CLAUDE.md`. Ask the user only if it requires them.
- Run `/impeccable polish` on the finished UI and `/impeccable audit` before the session ends, then fix what they find.

Product context for Impeccable: this is an internal-looking demo that a reviewer opens for two minutes. It should feel calm, trustworthy, and precise, like a financial operations tool. A person discussing debt may be stressed, so avoid playful styling, alarming red, and anything that shames the borrower. Do not use another company's name, logo, or branding.

## Structure

- `src/api/`: API client and types
- `src/features/chat/`: chat components and hooks
- `src/features/inspector/`: the tool-call and policy-source panel
- `src/features/reports/`: evaluation and report views
- `src/components/`: shared UI only

One component per file. Split a component before it passes 70 lines. Keep logic in hooks and rendering in components.

## Behavior

- Show a persistent notice that this is a simulation using fictional data.
- Offer sample borrowers and starter messages so a reviewer can try it without instructions.
- Handle loading, empty, error, retrying, and rate-limited states for every request.
- Show a friendly message for API failures, never raw errors.
- Render messages as plain text, never as raw HTML.
- Never put API keys or secrets in frontend code. All LLM calls go through the backend.

## Quality

- Keep it responsive to phone width and keyboard accessible, with visible focus states and semantic HTML.
- Before finishing a session, run the type check, lint, and production build, and check it in a browser if one is available.
