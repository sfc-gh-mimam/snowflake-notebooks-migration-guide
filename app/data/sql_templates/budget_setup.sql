-- Budget Setup and Tracking for Compute Pools
-- Note: Resource Monitors do NOT work with compute pools
-- This provides a manual monitoring approach

-- Step 1: Create a table to track budget thresholds
CREATE TABLE IF NOT EXISTS compute_pool_budgets (
    pool_name VARCHAR,
    monthly_budget_credits FLOAT,
    monthly_budget_usd FLOAT,
    alert_threshold_percent FLOAT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Step 2: Insert budget for your compute pool
INSERT INTO compute_pool_budgets (
    pool_name,
    monthly_budget_credits,
    monthly_budget_usd,
    alert_threshold_percent
)
VALUES (
    '<YOUR_COMPUTE_POOL_NAME>',
    1000,  -- Monthly credit budget
    4000,  -- Monthly USD budget (at $4/credit)
    80     -- Alert when 80% consumed
);

-- Step 3: Query current month usage vs budget
WITH current_month_usage AS (
    SELECT
        name AS pool_name,
        SUM(credits_used) AS credits_used_mtd,
        ROUND(SUM(credits_used) * 4, 2) AS cost_usd_mtd
    FROM
        SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
    WHERE
        service_type = 'COMPUTE_POOL'
        AND start_time >= DATE_TRUNC('month', CURRENT_DATE())
        AND name = '<YOUR_COMPUTE_POOL_NAME>'
    GROUP BY name
)
SELECT
    b.pool_name,
    b.monthly_budget_credits,
    b.monthly_budget_usd,
    COALESCE(u.credits_used_mtd, 0) AS credits_used_mtd,
    COALESCE(u.cost_usd_mtd, 0) AS cost_usd_mtd,
    ROUND((COALESCE(u.credits_used_mtd, 0) / b.monthly_budget_credits) * 100, 2) AS budget_used_percent,
    b.monthly_budget_credits - COALESCE(u.credits_used_mtd, 0) AS credits_remaining,
    CASE
        WHEN (COALESCE(u.credits_used_mtd, 0) / b.monthly_budget_credits) * 100 >= b.alert_threshold_percent
        THEN 'ALERT: Threshold exceeded'
        ELSE 'OK'
    END AS status
FROM
    compute_pool_budgets b
    LEFT JOIN current_month_usage u ON b.pool_name = u.pool_name;

-- Step 4: Daily budget burn rate calculation
WITH daily_usage AS (
    SELECT
        DATE(start_time) AS usage_date,
        name AS pool_name,
        SUM(credits_used) AS daily_credits
    FROM
        SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
    WHERE
        service_type = 'COMPUTE_POOL'
        AND start_time >= DATE_TRUNC('month', CURRENT_DATE())
        AND name = '<YOUR_COMPUTE_POOL_NAME>'
    GROUP BY DATE(start_time), name
)
SELECT
    pool_name,
    usage_date,
    daily_credits,
    SUM(daily_credits) OVER (PARTITION BY pool_name ORDER BY usage_date) AS cumulative_credits,
    ROUND(AVG(daily_credits) OVER (PARTITION BY pool_name), 2) AS avg_daily_credits,
    ROUND(AVG(daily_credits) OVER (PARTITION BY pool_name) * 22, 2) AS projected_monthly_credits
FROM
    daily_usage
ORDER BY
    pool_name, usage_date DESC;
