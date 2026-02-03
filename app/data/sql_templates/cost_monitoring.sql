-- Daily Credit Consumption for Compute Pools
-- Query METERING_HISTORY to track daily credit usage

SELECT
    DATE(start_time) AS usage_date,
    service_type,
    name AS compute_pool_name,
    SUM(credits_used) AS total_credits,
    COUNT(DISTINCT start_time) AS num_measurements,
    ROUND(SUM(credits_used) * 4, 2) AS estimated_cost_usd
FROM
    SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE
    service_type = 'COMPUTE_POOL'
    AND start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    AND name = '<YOUR_COMPUTE_POOL_NAME>'
GROUP BY
    DATE(start_time),
    service_type,
    name
ORDER BY
    usage_date DESC;
