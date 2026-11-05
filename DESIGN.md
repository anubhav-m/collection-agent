---
name: Collections agent simulation
description: Annual-report figures for an AI collections demo; one ink, tabular figures, nothing stated without a footnote.
colors:
  ink: "oklch(0.34 0.058 226)"
  ink-strong: "oklch(0.27 0.05 226)"
  ink-soft: "oklch(0.9 0.025 226)"
  on-ink: "oklch(0.97 0.008 220)"
  on-ink-muted: "oklch(0.84 0.02 222)"
  paper: "oklch(0.987 0.004 226)"
  panel: "oklch(0.962 0.008 226)"
  rule: "oklch(0.88 0.012 226)"
  rule-strong: "oklch(0.74 0.02 226)"
  text: "oklch(0.24 0.02 232)"
  text-muted: "oklch(0.45 0.02 232)"
  verified: "oklch(0.46 0.085 168)"
  verified-wash: "oklch(0.95 0.03 168)"
  handoff: "oklch(0.49 0.1 70)"
  handoff-wash: "oklch(0.955 0.04 85)"
  marked: "oklch(0.93 0.045 226)"
  focus: "oklch(0.52 0.13 236)"
typography:
  heading:
    fontFamily: "Source Sans 3 Variable, Segoe UI, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 650
    lineHeight: 1.25
  body:
    fontFamily: "Source Sans 3 Variable, Segoe UI, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Source Sans 3 Variable, Segoe UI, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 650
    letterSpacing: "0.04em"
  data:
    fontFamily: "Source Code Pro, ui-monospace, Cascadia Mono, monospace"
    fontSize: "0.8125rem"
    fontWeight: 400
rounded:
  sm: "4px"
spacing:
  1: "0.25rem"
  2: "0.5rem"
  3: "0.75rem"
  4: "1rem"
  5: "1.5rem"
  6: "2.25rem"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    rounded: "{rounded.sm}"
    padding: "0 16px"
    height: "2.25rem"
  button-primary-hover:
    backgroundColor: "{colors.ink-strong}"
  button-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
  starter-chip:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
  input-composer:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
---

# Design System: Collections agent simulation

## Overview

The audited figures section of an annual report, applied to a working operations tool. One committed ink owns the shell, the ground is cool paper, structure comes from hairline rules rather than cards, and every claim carries a superscript reference to its source. It is an Operate surface: standard tabs, buttons, inputs and tables, with the world contributing type, palette, density and one signature move. The tone is calm and precise because the simulated borrower may be under stress.

## Colors

### Primary
**Ink** (`ink`) is the only brand colour: the top bar, primary buttons, links, footnote marks, selected borrower, and the 2px rule above each results section.

### Neutral
**Paper** is the content ground; **Panel** is the second layer for the borrower rail, inspector and simulation notice. **Rule** and **Rule strong** draw every division.

### Named Rules
- **One state colour per meaning.** Teal-green `verified` means the server allowed or verified something. Ochre `handoff` means handed to a person, refused, or short of target. There is no red anywhere; refusals are information, not alarms.
- **Washes only behind status lines.** `handoff-wash` and `verified-wash` sit behind a single notice line, never behind whole regions.

## Typography

One family, Source Sans 3, with tabular numerals everywhere (`font-variant-numeric: tabular-nums` on body). Source Code Pro only for IDs, tool names and tool arguments.

### Hierarchy
Three sizes only: 20px headings, 15px body, 13px labels and metadata. Rank inside a size comes from weight (400 / 600 / 650) and from uppercase tracked labels for panel headings.

## Layout

Desktop (≥1100px): fixed three-column chat (16.5rem rail, flexible conversation, 22rem inspector), each column scrolling on its own under a sticky ink header. The results view is a single 64rem column in normal page scroll. Below 1100px everything stacks; the borrower list becomes a horizontal snap row. Spacing scale 4/8/12/16/24/36px.

## Elevation & Depth

Flat. Depth comes from the panel layer and hairline rules. No drop shadows; the selected borrower uses an inset 1px ink ring.

## Shapes

4px radius on buttons, inputs, chips, tool entries and notices. Tables and sections are unboxed and ruled.

## Components

### Buttons
Primary: ink fill, on-ink text, 2.25rem tall; hover deepens to ink-strong; disabled drops to panel with muted text. Quiet: ink outline and text on transparent; hover takes the `marked` wash.

### Chips (starter messages)
Small outlined chips in ink text that send a ready-made message; disabled while a reply is pending.

### Inputs / Fields
Composer textarea with a hidden label, a live character count against the 2,000-character server limit, Enter to send.

### Navigation
Two ARIA tabs in the ink bar (Chat, Results) with a 3px on-ink underline for the selected tab and arrow-key switching.

### Footnote reference (signature)
A superscript ink number after a reply or a figure. It links to an entry in the inspector's policy sources or the results page's sources list, which washes with `marked` on arrival (`:target`).

## Do's and Don'ts

### Do:
- Footnote every figure to a saved report file, and every policy-based reply to its source passage.
- Keep refused tool calls visible in the inspector with the server's reason.
- Label simulated data as simulated in the same block as the numbers.

### Don't:
- Don't use red or alarm styling for refusals, handoffs or misses.
- Don't add cards, shadows or stat tiles; use rules and tables.
- Don't render model output as HTML or Markdown; show plain text.
