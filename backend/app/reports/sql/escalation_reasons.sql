-- Top :top_reasons escalation reasons per lender, with each reason's share of that lender's total.
WITH counts AS (
    SELECT lender_id, reason, COUNT(*) AS escalations
    FROM escalations
    WHERE source = :source
    GROUP BY lender_id, reason
),
ranked AS (
    SELECT c.*,
        100.0 * escalations / SUM(escalations) OVER (PARTITION BY lender_id) AS share,
        RANK() OVER (PARTITION BY lender_id ORDER BY escalations DESC) AS reason_rank
    FROM counts AS c
)
SELECT r.lender_id, l.name AS lender_name, r.reason, r.escalations,
    ROUND(r.share, 1) AS share_pct, r.reason_rank
FROM ranked AS r
JOIN lenders AS l USING (lender_id)
WHERE r.reason_rank <= :top_reasons
ORDER BY r.lender_id, r.reason_rank, r.reason;
