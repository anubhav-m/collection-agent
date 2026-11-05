-- Reporting schema. Every row carries `source`: 'project' rows come from MongoDB and the
-- extraction results; 'simulated' rows come from the seeded generator. Reports filter on it,
-- so simulated history never mixes with real project numbers.
-- Money is stored in integer cents; dates are ISO 'YYYY-MM-DD' text.

CREATE TABLE IF NOT EXISTS lenders (
    lender_id   TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    source      TEXT NOT NULL CHECK (source IN ('project', 'simulated'))
);

CREATE TABLE IF NOT EXISTS borrowers (
    borrower_id TEXT PRIMARY KEY,
    lender_id   TEXT NOT NULL REFERENCES lenders (lender_id),
    source      TEXT NOT NULL CHECK (source IN ('project', 'simulated'))
);

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id   TEXT PRIMARY KEY,
    lender_id         TEXT NOT NULL REFERENCES lenders (lender_id),
    borrower_id       TEXT REFERENCES borrowers (borrower_id),
    status            TEXT NOT NULL,
    started_on        TEXT NOT NULL,
    source            TEXT NOT NULL CHECK (source IN ('project', 'simulated'))
);

CREATE TABLE IF NOT EXISTS promises (
    promise_id      TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL UNIQUE REFERENCES conversations (conversation_id),
    lender_id       TEXT NOT NULL REFERENCES lenders (lender_id),
    borrower_id     TEXT REFERENCES borrowers (borrower_id),
    amount_cents    INTEGER CHECK (amount_cents IS NULL OR amount_cents > 0),
    promised_on     TEXT NOT NULL,
    due_date        TEXT,
    extractor       TEXT NOT NULL,
    source          TEXT NOT NULL CHECK (source IN ('project', 'simulated'))
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id   TEXT PRIMARY KEY,
    promise_id   TEXT REFERENCES promises (promise_id),
    lender_id    TEXT NOT NULL REFERENCES lenders (lender_id),
    borrower_id  TEXT REFERENCES borrowers (borrower_id),
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    paid_on      TEXT NOT NULL,
    source       TEXT NOT NULL CHECK (source IN ('project', 'simulated'))
);

CREATE TABLE IF NOT EXISTS escalations (
    conversation_id TEXT PRIMARY KEY REFERENCES conversations (conversation_id),
    lender_id       TEXT NOT NULL REFERENCES lenders (lender_id),
    borrower_id     TEXT REFERENCES borrowers (borrower_id),
    reason          TEXT NOT NULL,
    trigger_kind    TEXT NOT NULL,
    escalated_on    TEXT NOT NULL,
    source          TEXT NOT NULL CHECK (source IN ('project', 'simulated'))
);

CREATE INDEX IF NOT EXISTS ix_promises_lender_due ON promises (lender_id, due_date);
CREATE INDEX IF NOT EXISTS ix_payments_promise ON payments (promise_id, paid_on);
CREATE INDEX IF NOT EXISTS ix_escalations_lender ON escalations (lender_id, reason);
