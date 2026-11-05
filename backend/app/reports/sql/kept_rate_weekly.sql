-- Promise-kept rate per lender and per week of the due date, with the change from the
-- calendar week before. Only promises with an amount and a due date before :as_of count.
-- Kept means payments made on or before the due date cover the promised amount.
WITH paid_by_due AS (
    SELECT p.promise_id, COALESCE(SUM(pay.amount_cents), 0) AS paid_cents
    FROM promises AS p
    LEFT JOIN payments AS pay
        ON pay.promise_id = p.promise_id
       AND pay.paid_on <= p.due_date AND pay.paid_on <= :as_of
    WHERE p.source = :source
    GROUP BY p.promise_id
),
resolved AS (
    SELECT p.lender_id,
        date(p.due_date, '-6 days', 'weekday 1') AS week_start,  -- Monday of that week
        CASE WHEN d.paid_cents >= p.amount_cents THEN 1 ELSE 0 END AS kept
    FROM promises AS p
    JOIN paid_by_due AS d USING (promise_id)
    WHERE p.due_date < :as_of AND p.amount_cents IS NOT NULL
),
weekly AS (
    SELECT lender_id, week_start, COUNT(*) AS promises_due, SUM(kept) AS promises_kept,
        100.0 * SUM(kept) / COUNT(*) AS kept_rate
    FROM resolved
    GROUP BY lender_id, week_start
),
with_previous AS (
    SELECT w.*,
        LAG(week_start) OVER by_week AS previous_week,
        LAG(kept_rate) OVER by_week AS previous_rate
    FROM weekly AS w
    WINDOW by_week AS (PARTITION BY lender_id ORDER BY week_start)
)
SELECT
    lender_id, week_start, promises_due, promises_kept,
    ROUND(kept_rate, 1) AS kept_rate_pct,
    -- Compare only with the week directly before; a gap gives NULL, not a false change.
    CASE WHEN previous_week = date(week_start, '-7 days')
        THEN ROUND(kept_rate - previous_rate, 1) END AS wow_change_pp
FROM with_previous
ORDER BY lender_id, week_start;
