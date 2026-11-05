-- Borrowers ranked by amount overdue within each lender (top :top_n per lender).
-- Amount overdue = promised amount minus everything paid so far, for promises whose
-- due date is before :as_of. Late payments reduce it; a promise paid in full drops out.
WITH paid_to_date AS (
    SELECT p.promise_id, COALESCE(SUM(pay.amount_cents), 0) AS paid_cents
    FROM promises AS p
    LEFT JOIN payments AS pay
        ON pay.promise_id = p.promise_id AND pay.paid_on <= :as_of
    WHERE p.source = :source
    GROUP BY p.promise_id
),
per_borrower AS (
    SELECT p.lender_id, p.borrower_id, COUNT(*) AS overdue_promises,
        SUM(p.amount_cents - d.paid_cents) AS overdue_cents
    FROM promises AS p
    JOIN paid_to_date AS d USING (promise_id)
    WHERE p.due_date < :as_of AND p.amount_cents > d.paid_cents
      AND p.borrower_id IS NOT NULL
    GROUP BY p.lender_id, p.borrower_id
),
ranked AS (
    SELECT b.*,
        RANK() OVER (PARTITION BY lender_id ORDER BY overdue_cents DESC) AS rank_in_lender,
        100.0 * overdue_cents / SUM(overdue_cents) OVER (PARTITION BY lender_id) AS share
    FROM per_borrower AS b
)
SELECT lender_id, borrower_id, overdue_promises,
    ROUND(overdue_cents / 100.0, 2) AS amount_overdue, rank_in_lender,
    ROUND(share, 1) AS share_of_lender_pct
FROM ranked
WHERE rank_in_lender <= :top_n
ORDER BY lender_id, rank_in_lender, borrower_id;
