# Extraction dataset

44 fictional borrower chats, hand-labelled for one promised payment each. All names, amounts and dates are invented.

- `transcripts/`: the chats. Each has a fixed `reference_date` (the day of the chat) so relative dates such as "tomorrow" have one right answer.
- `labels/`: the answers, kept apart from the transcripts. `case` says what makes the transcript hard; extractors never see it.
- `split.json`: the development and held-out test ids, made by `scripts/make_extraction_split.py` before any extractor was written. Only the development set is used for tuning.

## Labelling rules

**promise_made** is `true` only when the borrower clearly commits to pay.

- Conditional ("if my refund comes in"), hedged ("maybe", "I'll try", "I don't know yet") and retracted promises are `false`.
- Past payments, refusals, disputes, questions and third parties are `false`.
- Saying yes to an agent's proposal ("Yes, that works", "Deal") is a promise of the agent's proposed amount and date.

**amount** is the final committed amount of the first promised payment, in dollars. If the borrower changes it, the last value counts. Amounts said by the agent (balances, minimums) or about income do not count unless the borrower accepts them as the payment. `null` when no amount is given.

**date** is the date of that payment, from the reference date:

- "today", "tonight": the reference date. "tomorrow": the next day.
- A weekday alone or "this <weekday>": the next such day after the reference date.
- "next <weekday>": that weekday in the following calendar week (weeks start on Monday).
- "the 15th", "the first": the next such day of the month on or after the reference date.
- "in two weeks", "a week from today": add the days.
- "end of the month": the last day of the current month.
- Vague times ("sometime next week", "payday" with no known date) are `null`.

When `promise_made` is `false`, both `amount` and `date` are `null`.
