-- Collection of useful queries for compute pool monitoring and cost analysis

-- Query 1: Hourly credit consumption pattern
SELECT
    DATE_TRUNC('hour', start_time) AS hour,
    name AS pool_name,
    SUM(credits_used) AS credits_per_hour,
    ROUND(SUM(credits_used) * 4, 2) AS cost_usd_per_hour
FROM
    SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE
    service_type = 'COMPUTE_POOL'
    AND start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND name = '<YOUR_COMPUTE_POOL_NAME>'
GROUP BY
    DATE_TRUNC('hour', start_time),
    name
ORDER BY
    hour DESC;


-- Query 2: Detect idle compute pools (low activity)
WITH pool_activity AS (
    SELECT
        mh.name AS pool_name,
        DATE(mh.start_time) AS activity_date,
        SUM(mh.credits_used) AS daily_credits,
        COUNT(DISTINCT qh.query_id) AS query_count
    FROM
        SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY mh
        LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY qh
            ON DATE(mh.start_time) = DATE(qh.start_time)
            AND qh.execution_status = 'SUCCESS'
    WHERE
        mh.service_type = 'COMPUTE_POOL'
        AND mh.start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    GROUP BY
        mh.name,
        DATE(mh.start_time)
)
SELECT
    pool_name,
    activity_date,
    daily_credits,
    query_count,
    CASE
        WHEN daily_credits > 0 AND query_count < 5 THEN 'Potentially Idle'
        WHEN daily_credits > 0 AND query_count >= 5 THEN 'Active'
        ELSE 'No Usage'
    END AS status
FROM
    pool_activity
WHERE
    daily_credits > 0 AND query_count < 5
ORDER BY
    activity_date DESC, daily_credits DESC;


-- Query 3: User-level cost attribution
-- Track which users are driving compute pool costs
SELECT
    qh.user_name,
    DATE(qh.start_time) AS query_date,
    COUNT(DISTINCT qh.query_id) AS query_count,
    SUM(qh.total_elapsed_time) / 1000 AS total_execution_seconds,
    -- Approximate credit attribution based on query time
    ROUND(SUM(qh.total_elapsed_time) / 3600000.0 * 2, 4) AS estimated_credits
FROM
    SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY qh
WHERE
    qh.start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    AND qh.execution_status = 'SUCCESS'
    -- Filter for queries that likely used compute pools
    AND qh.warehouse_name IS NULL
GROUP BY
    qh.user_name,
    DATE(qh.start_time)
ORDER BY
    estimated_credits DESC;


-- Query 4: Cost by workload type (requires tagging)
-- Assumes queries are tagged with workload type
SELECT
    DATE(start_time) AS query_date,
    query_tag,
    COUNT(DISTINCT query_id) AS query_count,
    ROUND(SUM(total_elapsed_time) / 3600000.0 * 2, 4) AS estimated_credits,
    ROUND(SUM(total_elapsed_time) / 3600000.0 * 2 * 4, 2) AS estimated_cost_usd
FROM
    SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE
    start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    AND execution_status = 'SUCCESS'
    AND warehouse_name IS NULL
    AND query_tag IS NOT NULL
GROUP BY
    DATE(start_time),
    query_tag
ORDER BY
    query_date DESC, estimated_credits DESC;


-- Query 5: Compare warehouse vs compute pool costs (migration analysis)
WITH warehouse_costs AS (
    SELECT
        DATE(start_time) AS cost_date,
        'Warehouse' AS service,
        SUM(credits_used) AS credits,
        ROUND(SUM(credits_used) * 4, 2) AS cost_usd
    FROM
        SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
    WHERE
        service_type = 'WAREHOUSE'
        AND name = '<YOUR_WAREHOUSE_NAME>'
        AND start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    GROUP BY DATE(start_time)
),
pool_costs AS (
    SELECT
        DATE(start_time) AS cost_date,
        'Compute Pool' AS service,
        SUM(credits_used) AS credits,
        ROUND(SUM(credits_used) * 4, 2) AS cost_usd
    FROM
        SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
    WHERE
        service_type = 'COMPUTE_POOL'
        AND name = '<YOUR_COMPUTE_POOL_NAME>'
        AND start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    GROUP BY DATE(start_time)
)
SELECT
    COALESCE(w.cost_date, p.cost_date) AS cost_date,
    COALESCE(w.credits, 0) AS warehouse_credits,
    COALESCE(p.credits, 0) AS pool_credits,
    COALESCE(w.cost_usd, 0) AS warehouse_cost_usd,
    COALESCE(p.cost_usd, 0) AS pool_cost_usd,
    COALESCE(w.cost_usd, 0) - COALESCE(p.cost_usd, 0) AS daily_savings_usd
FROM
    warehouse_costs w
    FULL OUTER JOIN pool_costs p ON w.cost_date = p.cost_date
ORDER BY
    cost_date DESC;


-- Query 6: Peak usage hours identification
SELECT
    EXTRACT(HOUR FROM start_time) AS hour_of_day,
    name AS pool_name,
    AVG(credits_used) AS avg_credits,
    MAX(credits_used) AS peak_credits,
    COUNT(*) AS measurement_count
FROM
    SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE
    service_type = 'COMPUTE_POOL'
    AND start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    AND name = '<YOUR_COMPUTE_POOL_NAME>'
GROUP BY
    EXTRACT(HOUR FROM start_time),
    name
ORDER BY
    avg_credits DESC;


-- Query 7: Weekly cost trends
SELECT
    DATE_TRUNC('week', start_time) AS week_start,
    name AS pool_name,
    SUM(credits_used) AS weekly_credits,
    ROUND(SUM(credits_used) * 4, 2) AS weekly_cost_usd,
    ROUND(AVG(credits_used), 4) AS avg_credits_per_measurement
FROM
    SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE
    service_type = 'COMPUTE_POOL'
    AND start_time >= DATEADD(day, -90, CURRENT_TIMESTAMP())
    AND name = '<YOUR_COMPUTE_POOL_NAME>'
GROUP BY
    DATE_TRUNC('week', start_time),
    name
ORDER BY
    week_start DESC;
