-- ============================================================================
-- Snowflake Notebooks Migration Guide - SPCS Deployment Setup
-- ============================================================================
-- This script sets up the infrastructure needed to deploy the Migration Guide
-- as a Snowpark Container Service in Snowflake
-- ============================================================================

-- Step 1: Create database and schema for the service
-- ============================================================================
CREATE DATABASE IF NOT EXISTS NOTEBOOKS_MIGRATION_DB;
USE DATABASE NOTEBOOKS_MIGRATION_DB;

CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

-- Step 2: Create compute pool for running the service
-- ============================================================================
CREATE COMPUTE POOL IF NOT EXISTS MIGRATION_GUIDE_POOL
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_S
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = 3600
  COMMENT = 'Compute pool for Migration Guide Streamlit service';

-- Verify compute pool creation
SHOW COMPUTE POOLS LIKE 'MIGRATION_GUIDE_POOL';

-- Step 3: Create image repository for container images
-- ============================================================================
CREATE IMAGE REPOSITORY IF NOT EXISTS NOTEBOOKS_MIGRATION_REPO;

-- Show repository URL (needed for docker push)
SHOW IMAGE REPOSITORIES LIKE 'NOTEBOOKS_MIGRATION_REPO';

-- Get the repository URL for docker commands
-- Format: <orgname>-<account>.registry.snowflakecomputing.com/<db>/<schema>/<repo>
SELECT
    repository_url,
    'docker login ' || repository_url AS login_command,
    'docker tag migration-guide:latest ' || repository_url || '/migration-guide:latest' AS tag_command,
    'docker push ' || repository_url || '/migration-guide:latest' AS push_command
FROM (
    SHOW IMAGE REPOSITORIES LIKE 'NOTEBOOKS_MIGRATION_REPO'
);

-- Step 4: Grant necessary privileges
-- ============================================================================
-- Grant usage on compute pool
GRANT USAGE ON COMPUTE POOL MIGRATION_GUIDE_POOL TO ROLE SYSADMIN;
GRANT MONITOR ON COMPUTE POOL MIGRATION_GUIDE_POOL TO ROLE SYSADMIN;

-- Grant usage on database and schema
GRANT USAGE ON DATABASE NOTEBOOKS_MIGRATION_DB TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA NOTEBOOKS_MIGRATION_DB.PUBLIC TO ROLE SYSADMIN;

-- Grant privileges on image repository
GRANT READ ON IMAGE REPOSITORY NOTEBOOKS_MIGRATION_REPO TO ROLE SYSADMIN;

-- Step 5: Create service (run this AFTER pushing the Docker image)
-- ============================================================================
-- NOTE: Update the image path in service-spec.yaml before running this

CREATE SERVICE IF NOT EXISTS MIGRATION_GUIDE_SERVICE
  IN COMPUTE POOL MIGRATION_GUIDE_POOL
  FROM SPECIFICATION $$
spec:
  containers:
  - name: migration-guide
    image: /notebooks_migration_db/public/notebooks_migration_repo/migration-guide:latest
    env:
      STREAMLIT_SERVER_PORT: 8501
      STREAMLIT_SERVER_HEADLESS: "true"
      STREAMLIT_BROWSER_GATHER_USAGE_STATS: "false"
    resources:
      requests:
        memory: 2Gi
        cpu: 1
      limits:
        memory: 4Gi
        cpu: 2
    readinessProbe:
      httpGet:
        path: /_stcore/health
        port: 8501
      initialDelaySeconds: 10
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
  endpoints:
  - name: streamlit
    port: 8501
    public: true
$$
  MIN_INSTANCES = 1
  MAX_INSTANCES = 1
  COMMENT = 'Snowflake Notebooks Migration Guide Streamlit Application';

-- Step 6: Grant service access
-- ============================================================================
GRANT USAGE ON SERVICE MIGRATION_GUIDE_SERVICE TO ROLE SYSADMIN;
GRANT MONITOR ON SERVICE MIGRATION_GUIDE_SERVICE TO ROLE SYSADMIN;

-- Optional: Grant to additional roles (e.g., for sales team)
-- GRANT USAGE ON SERVICE MIGRATION_GUIDE_SERVICE TO ROLE SALES_ROLE;

-- Step 7: Verify service status
-- ============================================================================
SHOW SERVICES LIKE 'MIGRATION_GUIDE_SERVICE';

-- Check service status and endpoint
SELECT
    name,
    database_name,
    schema_name,
    compute_pool,
    status,
    SYSTEM$GET_SERVICE_STATUS('MIGRATION_GUIDE_SERVICE') AS detailed_status
FROM (
    SHOW SERVICES LIKE 'MIGRATION_GUIDE_SERVICE'
);

-- Get the public endpoint URL
SHOW ENDPOINTS IN SERVICE MIGRATION_GUIDE_SERVICE;

-- Step 8: Monitoring queries
-- ============================================================================

-- View service logs
CALL SYSTEM$GET_SERVICE_LOGS('NOTEBOOKS_MIGRATION_DB.PUBLIC.MIGRATION_GUIDE_SERVICE', '0', 'migration-guide', 100);

-- Check container status
SELECT SYSTEM$GET_SERVICE_STATUS('NOTEBOOKS_MIGRATION_DB.PUBLIC.MIGRATION_GUIDE_SERVICE');

-- Monitor compute pool usage
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE service_type = 'COMPUTE_POOL'
  AND name = 'MIGRATION_GUIDE_POOL'
  AND start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;

-- Step 9: Suspend/Resume service (for cost management)
-- ============================================================================

-- Suspend service when not in use
-- ALTER SERVICE MIGRATION_GUIDE_SERVICE SUSPEND;

-- Resume service
-- ALTER SERVICE MIGRATION_GUIDE_SERVICE RESUME;

-- Step 10: Update service (after pushing new image version)
-- ============================================================================

-- Method 1: Update with new specification
/*
ALTER SERVICE MIGRATION_GUIDE_SERVICE
  FROM SPECIFICATION $$
    [paste updated service-spec.yaml content here]
  $$;
*/

-- Method 2: Recreate service (if major changes)
/*
DROP SERVICE MIGRATION_GUIDE_SERVICE;
-- Then recreate using CREATE SERVICE command above
*/

-- Step 11: Cleanup (CAUTION: This removes all resources)
-- ============================================================================
/*
-- Uncomment to clean up resources

DROP SERVICE IF EXISTS MIGRATION_GUIDE_SERVICE;
DROP IMAGE REPOSITORY IF EXISTS NOTEBOOKS_MIGRATION_REPO;
DROP COMPUTE POOL IF EXISTS MIGRATION_GUIDE_POOL;
DROP SCHEMA IF EXISTS NOTEBOOKS_MIGRATION_DB.PUBLIC;
DROP DATABASE IF EXISTS NOTEBOOKS_MIGRATION_DB;
*/

-- ============================================================================
-- End of setup script
-- ============================================================================

-- Quick Reference Commands:
-- ============================================================================
-- View service status:     SHOW SERVICES;
-- View compute pools:      SHOW COMPUTE POOLS;
-- View image repos:        SHOW IMAGE REPOSITORIES;
-- Get service logs:        CALL SYSTEM$GET_SERVICE_LOGS('<service_name>', '0', '<container_name>', 100);
-- Get service endpoint:    SHOW ENDPOINTS IN SERVICE <service_name>;
-- ============================================================================
