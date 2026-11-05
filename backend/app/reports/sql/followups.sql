-- Promises a collector should act on as of :as_of.
--   overdue          due date has passed and the promise is not fully paid
--   due              unpaid and due within the next :window_days days
--   missing_details  a promise with no amount or no date; confirm the details
-- Escalated conversations are left out: a human agent owns them now.
WITH paid AS (
    SELECT p.promise_id, COALESCE(SUM(pay.amount_cents), 0) AS paid_cents
    FROM promises AS p
    LEFT JOIN payments AS pay
        ON pay.promise_id = p.promise_id AND pay.paid_on <= :as_of
    WHERE p.source = :source
    GROUP BY p.promise_id
),
open_promises AS (
    SELECT p.*, paid.paid_cents,
        CASE
            WHEN p.amount_cents IS NULL OR p.due_date IS NULL THEN 'missing_details'
            WHEN p.due_date < :as_of THEN 'overdue'
            ELSE 'due'
        END AS followup_status
    FROM promises AS p
    JOIN paid USING (promise_id)
    LEFT JOIN escalations AS e USING (conversation_id)
    WHERE e.conversation_id IS NULL
      AND (p.amount_cents IS NULL OR paid.paid_cents < p.amount_cents)
)
SELECT
    o.promise_id, o.lender_id, l.name AS lender_name, o.borrower_id, o.conversation_id,
    o.followup_status, o.due_date,
    ROUND(o.amount_cents / 100.0, 2) AS promised_amount,
    ROUND(o.paid_cents / 100.0, 2) AS paid_amount,
    ROUND((o.amount_cents - o.paid_cents) / 100.0, 2) AS outstanding_amount,
    CASE WHEN o.followup_status = 'overdue'
        THEN CAST(julianday(:as_of) - julianday(o.due_date) AS INTEGER) END AS days_overdue
FROM open_promises AS o
JOIN lenders AS l USING (lender_id)
WHERE o.followup_status <> 'due'
   OR o.due_date <= date(:as_of, '+' || :window_days || ' days')
ORDER BY
    CASE o.followup_status WHEN 'overdue' THEN 0 WHEN 'due' THEN 1 ELSE 2 END,
    o.due_date, o.promise_id;
