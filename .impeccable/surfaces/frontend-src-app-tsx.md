---
version: 1
slug: "frontend-src-app-tsx"
primary_target: "frontend/src/App.tsx"
related_targets: []
---

## Scope

The whole demo app (`frontend/src`): chat view with sample borrowers, inspector panel, results view. Mode: Operate.

## Audience and job

A technical reviewer, about two minutes, plays a fictional borrower and checks that the server, not the model, decides what is allowed, and that every figure is backed by a saved report.

## Constraints

Calm, precise, financial-operations feel. No alarming red, nothing playful or shaming. Persistent simulation notice. Plain-text messages. Phone width and keyboard accessible.

## Direction contract

THESIS: The demo reads like the audited figures section of an annual report: one committed ink, tabular figures, and nothing stated without a footnote. It refuses the category default of a grey chat bubble app with a stat-card dashboard.

OWN-WORLD: Deep petrol-ink shell (top bar and active tab) over a cool, faintly blue paper ground; a second, slightly darker blue-grey layer for the side rail and inspector. Hairline rules instead of cards. Ochre is the only state colour for handoff and blocked actions, teal-green for verified. Source Sans 3 with tabular numerals, three sizes only (13, 15, 20 px); rank by weight, case and rule. Source Code Pro only for IDs and tool arguments.

STORY: The reviewer picks a sample borrower, sends a starter message, watches the inspector fill with numbered server decisions, then opens Results and sees each number footnoted to its report file.

FIRST VIEWPORT: Ink top bar with product name, Chat/Results tabs and the simulation notice. Below, three columns: sample borrowers rail (left, 260px), conversation (centre, flexible, composer pinned at bottom), inspector (right, 340px): state ledger, numbered tool calls, policy sources. Primary action: the starter message buttons and the composer.

FORM: Swiss annual-report figures section, candidate 3 of 7 on the ordered list; seed:a655f9014763d0b8. Signature move: footnote markers. Every assistant reply that used policy, every inspector entry and every metric carries a superscript reference that resolves to its source (tool call, policy section, report path); selecting one highlights the matching entry. Raises: blocked tool calls stay visible with a "blocked by server" mark and are never hidden (from the ticket wallet's "nothing disappears, it cancels"); a strict hairline module system with dense inspector rows (from high-density web); rank carried by weight and case within the three sizes (from the timetable rack).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
