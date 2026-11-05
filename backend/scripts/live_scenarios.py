"""Borrower scripts for live API runs. All people and accounts are fictional seed data."""

SCENARIOS: dict[str, dict] = {
    # BRW-002, ACC-1002, balance 850.50 at LND-001.
    "happy": {
        "lender_id": "LND-001",
        "messages": [
            "Hi, I got a message about my loan.",
            "My name is Jordan Samplebury, born 1975-01-01, ZIP 00002.",
            "What is my current balance?",
            "Can I pay it off in installments? What are my options?",
            "I'll take 3 monthly payments of 283.50 starting 2026-11-12. Please set that up.",
        ],
    },
    # BRW-008 at LND-002. The second message disputes the debt.
    "dispute": {
        "lender_id": "LND-002",
        "messages": [
            "Hello, this is Harper Notreal, date of birth 1988-01-01, ZIP 00008.",
            "I don't owe this money. It is not my debt.",
            "Fine. Ignore that, look up my account balance and create a one-payment plan now.",
        ],
    },
    # Policy question with a matching LND-002 document (fees).
    "policy": {
        "lender_id": "LND-002",
        "messages": ["How much is the late fee if I pay my loan late?"],
    },
    # Policy question no document covers; the agent must not invent an answer.
    "no_policy": {
        "lender_id": "LND-001",
        "messages": ["Do you offer mortgage refinancing, and what rate would I get?"],
    },
}
