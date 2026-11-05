-- Overall promise-kept rate per lender, using the same rule as kept_rate_weekly.sql.
WITH paid_by_due AS (
    SELECT p.promise_id, COALESCE(SUM(pay.amount_cents), 0) AS paid_cents
    FROM promises AS p
    LEFT JOIN payments AS pay
        ON pay.promise_id = p.promise_id
       AND pay.paid_on <= p.due_date AND pay.paid_on <= :as_of
    WHERE p.source = :source
    GROUP BY p.promise_id
),
per_lender AS (
    SELECT p.lender_id, COUNT(*) AS promises_due,
        SUM(CASE WHEN d.paid_cents >= p.amount_cents THEN 1 ELSE 0 END) AS promises_kept
    FROM promises AS p
    JOIN paid_by_due AS d USING (promise_id)
    WHERE p.due_date < :as_of AND p.amount_cents IS NOT NULL
    GROUP BY p.lender_id
)
SELECT
    pl.lender_id, l.name AS lender_name, pl.promises_due, pl.promises_kept,
    ROUND(100.0 * pl.promises_kept / pl.promises_due, 1) AS kept_rate_pct,
    RANK() OVER (ORDER BY 1.0 * pl.promises_kept / pl.promises_due DESC) AS lender_rank
FROM per_lender AS pl
JOIN lenders AS l USING (lender_id)
ORDER BY lender_rank, pl.lender_id;
