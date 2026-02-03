# Snowpark Container Services (SPCS) Deployment Guide

This guide walks through deploying the Snowflake Notebooks Migration Guide as a containerized service within Snowflake using Snowpark Container Services.

## Prerequisites

- Snowflake account with SPCS enabled
- Docker installed locally
- Snowflake CLI (snowsql) or web interface access
- ACCOUNTADMIN or appropriate privileges for creating compute pools and services
- Docker registry credentials for Snowflake

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│         Snowflake Account                       │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Notebooks Migration Service             │  │
│  │  (Streamlit App)                         │  │
│  │                                          │  │
│  │  ┌────────────────────────────────┐     │  │
│  │  │  Container                     │     │  │
│  │  │  - Streamlit (port 8501)       │     │  │
│  │  │  - Migration Calculator        │     │  │
│  │  │  - SQL Templates               │     │  │
│  │  │  - PDF Export                  │     │  │
│  │  └────────────────────────────────┘     │  │
│  │         ↓                                │  │
│  │  ┌────────────────────────────────┐     │  │
│  │  │  Compute Pool                  │     │  │
│  │  │  - CPU_X64_S                   │     │  │
│  │  │  - 1 node                      │     │  │
│  │  └────────────────────────────────┘     │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Image Repository                        │  │
│  │  - Container images stored here          │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Deployment Steps

### Step 1: Prepare Your Environment

```bash
# Navigate to project directory
cd /Users/mimam/spcs-test1

# Verify files are in place
ls -la
# Should see: Dockerfile, service-spec.yaml, setup.sql, app/, requirements.txt
```

### Step 2: Build Docker Image

```bash
# Build the Docker image
docker build -t migration-guide:latest .

# Verify the image was created
docker images | grep migration-guide

# Optional: Test locally first
docker run -p 8501:8501 migration-guide:latest
# Access at http://localhost:8501 to verify it works
# Press Ctrl+C to stop
```

### Step 3: Set Up Snowflake Infrastructure

```bash
# Connect to Snowflake using SnowSQL
snowsql -a <your_account> -u <your_username>

# Or use Snowflake web UI and run the SQL commands
```

Run the setup SQL:

```sql
-- Execute the setup.sql file in Snowflake
-- This creates:
-- 1. Database and schema
-- 2. Compute pool
-- 3. Image repository

-- In SnowSQL:
!source setup.sql

-- Or copy/paste sections from setup.sql in the web UI
```

### Step 4: Get Repository URL and Login

After creating the image repository, get the connection details:

```sql
-- Get repository URL
SHOW IMAGE REPOSITORIES LIKE 'NOTEBOOKS_MIGRATION_REPO';

-- Get formatted docker commands
SELECT
    repository_url,
    'docker login ' || repository_url AS login_command,
    'docker tag migration-guide:latest ' || repository_url || '/migration-guide:latest' AS tag_command,
    'docker push ' || repository_url || '/migration-guide:latest' AS push_command
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));
```

The repository URL format is:
```
<orgname>-<account>.registry.snowflakecomputing.com/notebooks_migration_db/public/notebooks_migration_repo
```

### Step 5: Push Image to Snowflake Registry

```bash
# Set variables (replace with your actual values)
REPO_URL="<orgname>-<account>.registry.snowflakecomputing.com/notebooks_migration_db/public/notebooks_migration_repo"

# Login to Snowflake registry
# Use your Snowflake username and password
docker login $REPO_URL

# Tag the image
docker tag migration-guide:latest $REPO_URL/migration-guide:latest

# Push to Snowflake
docker push $REPO_URL/migration-guide:latest

# Verify the push
# In Snowflake:
SHOW IMAGES IN IMAGE REPOSITORY NOTEBOOKS_MIGRATION_REPO;
```

### Step 6: Create the Service

After the image is pushed, create the service:

```sql
-- Create the service (this starts the container)
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
```

### Step 7: Verify Deployment

```sql
-- Check service status
SHOW SERVICES LIKE 'MIGRATION_GUIDE_SERVICE';

-- Get detailed status
SELECT SYSTEM$GET_SERVICE_STATUS('NOTEBOOKS_MIGRATION_DB.PUBLIC.MIGRATION_GUIDE_SERVICE');

-- Get the public endpoint URL
SHOW ENDPOINTS IN SERVICE MIGRATION_GUIDE_SERVICE;
```

The endpoint will be in the format:
```
<unique-id>.snowflakecomputing.app
```

### Step 8: Access the Application

Open the endpoint URL in your browser:
```
https://<unique-id>.snowflakecomputing.app
```

You should see the Snowflake Notebooks Migration Guide landing page.

## Post-Deployment

### Grant Access to Users

```sql
-- Grant usage to specific roles
GRANT USAGE ON SERVICE MIGRATION_GUIDE_SERVICE TO ROLE SALES_TEAM;
GRANT USAGE ON SERVICE MIGRATION_GUIDE_SERVICE TO ROLE DATA_ENGINEERING;

-- Users in these roles can now access the service endpoint
```

### Monitor the Service

```sql
-- View service logs (last 100 lines)
CALL SYSTEM$GET_SERVICE_LOGS(
    'NOTEBOOKS_MIGRATION_DB.PUBLIC.MIGRATION_GUIDE_SERVICE',
    '0',
    'migration-guide',
    100
);

-- Monitor compute pool credit usage
SELECT
    DATE(start_time) AS usage_date,
    SUM(credits_used) AS daily_credits,
    ROUND(SUM(credits_used) * 4, 2) AS estimated_cost_usd
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE service_type = 'COMPUTE_POOL'
  AND name = 'MIGRATION_GUIDE_POOL'
  AND start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY DATE(start_time)
ORDER BY usage_date DESC;

-- Check service health
SELECT
    name,
    status,
    owner,
    created_on
FROM TABLE(
    SHOW SERVICES LIKE 'MIGRATION_GUIDE_SERVICE'
);
```

### Update the Service

When you need to deploy updates:

```bash
# 1. Make code changes
# 2. Build new image with version tag
docker build -t migration-guide:v1.1 .

# 3. Tag and push
docker tag migration-guide:v1.1 $REPO_URL/migration-guide:v1.1
docker push $REPO_URL/migration-guide:v1.1

# 4. Also tag as latest
docker tag migration-guide:v1.1 $REPO_URL/migration-guide:latest
docker push $REPO_URL/migration-guide:latest
```

Then update the service in Snowflake:

```sql
-- Recreate service with new image
DROP SERVICE MIGRATION_GUIDE_SERVICE;

CREATE SERVICE MIGRATION_GUIDE_SERVICE
  IN COMPUTE POOL MIGRATION_GUIDE_POOL
  FROM SPECIFICATION '...'  -- Same spec as before
  MIN_INSTANCES = 1
  MAX_INSTANCES = 1;
```

### Suspend/Resume Service

To save costs when the service isn't needed:

```sql
-- Suspend the service
ALTER SERVICE MIGRATION_GUIDE_SERVICE SUSPEND;

-- Resume when needed
ALTER SERVICE MIGRATION_GUIDE_SERVICE RESUME;

-- Or suspend the entire compute pool
ALTER COMPUTE POOL MIGRATION_GUIDE_POOL SUSPEND;
ALTER COMPUTE POOL MIGRATION_GUIDE_POOL RESUME;
```

## Troubleshooting

### Service Won't Start

```sql
-- Check detailed status
SELECT SYSTEM$GET_SERVICE_STATUS('NOTEBOOKS_MIGRATION_DB.PUBLIC.MIGRATION_GUIDE_SERVICE');

-- View logs for errors
CALL SYSTEM$GET_SERVICE_LOGS(
    'NOTEBOOKS_MIGRATION_DB.PUBLIC.MIGRATION_GUIDE_SERVICE',
    '0',
    'migration-guide',
    500
);
```

Common issues:
- **Image not found**: Verify image was pushed correctly with `SHOW IMAGES`
- **Compute pool offline**: Check `SHOW COMPUTE POOLS` and resume if needed
- **Permission errors**: Verify grants with `SHOW GRANTS ON SERVICE MIGRATION_GUIDE_SERVICE`

### Can't Access Endpoint

```sql
-- Verify endpoint is public
SHOW ENDPOINTS IN SERVICE MIGRATION_GUIDE_SERVICE;

-- Ensure service is running
SELECT SYSTEM$GET_SERVICE_STATUS('NOTEBOOKS_MIGRATION_DB.PUBLIC.MIGRATION_GUIDE_SERVICE');
```

### High Costs

```sql
-- Check if service is idle
SELECT
    DATEDIFF(hour, MAX(start_time), CURRENT_TIMESTAMP()) AS hours_since_last_activity
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE service_type = 'COMPUTE_POOL'
  AND name = 'MIGRATION_GUIDE_POOL';

-- Suspend if idle
ALTER SERVICE MIGRATION_GUIDE_SERVICE SUSPEND;
```

## Cost Optimization

### Right-Size Compute Pool

The default configuration uses `CPU_X64_S` which is appropriate for this Streamlit app. If you experience performance issues:

```sql
-- Create a larger compute pool
CREATE COMPUTE POOL MIGRATION_GUIDE_POOL_M
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_M  -- Upgrade to Medium
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = 1800;

-- Recreate service on new pool
ALTER SERVICE MIGRATION_GUIDE_SERVICE SET COMPUTE_POOL = MIGRATION_GUIDE_POOL_M;
```

### Auto-Suspend Configuration

Adjust auto-suspend to match usage patterns:

```sql
-- Shorter timeout for development (15 min)
ALTER COMPUTE POOL MIGRATION_GUIDE_POOL SET AUTO_SUSPEND_SECS = 900;

-- Longer timeout for active use (1 hour)
ALTER COMPUTE POOL MIGRATION_GUIDE_POOL SET AUTO_SUSPEND_SECS = 3600;
```

## Security Considerations

### Network Access

The service endpoint is public by default. To restrict access:

```sql
-- Create service with private endpoint
-- Modify service-spec.yaml:
endpoints:
- name: streamlit
  port: 8501
  public: false  -- Change to false
```

Then access via Snowflake's network infrastructure.

### Authentication

SPCS endpoints inherit Snowflake authentication. Users must:
1. Have a valid Snowflake account
2. Have USAGE privilege on the service
3. Be authenticated in their browser

### Data Access

The service runs with the privileges of the role that created it. Grant minimal necessary privileges:

```sql
-- Service only needs to read metadata tables
GRANT USAGE ON DATABASE NOTEBOOKS_MIGRATION_DB TO ROLE MIGRATION_SERVICE_ROLE;
GRANT USAGE ON SCHEMA NOTEBOOKS_MIGRATION_DB.PUBLIC TO ROLE MIGRATION_SERVICE_ROLE;
```

## Cleanup

To completely remove the deployment:

```sql
-- Stop and remove service
DROP SERVICE IF EXISTS MIGRATION_GUIDE_SERVICE;

-- Remove images
DROP IMAGE REPOSITORY IF EXISTS NOTEBOOKS_MIGRATION_REPO;

-- Remove compute pool
DROP COMPUTE POOL IF EXISTS MIGRATION_GUIDE_POOL;

-- Remove database
DROP DATABASE IF EXISTS NOTEBOOKS_MIGRATION_DB;
```

## Support

For SPCS-specific issues:
- Snowflake Documentation: https://docs.snowflake.com/en/developer-guide/snowpark-container-services
- Snowflake Support Portal
- Your Snowflake account team

For application issues:
- Review logs: `SYSTEM$GET_SERVICE_LOGS`
- Check service status: `SYSTEM$GET_SERVICE_STATUS`
- Verify image: `SHOW IMAGES IN IMAGE REPOSITORY`

## Best Practices

1. **Version Your Images**: Tag with version numbers (`v1.0`, `v1.1`) not just `latest`
2. **Monitor Costs**: Set up alerts for compute pool credit consumption
3. **Use Auto-Suspend**: Configure appropriate timeouts to avoid idle costs
4. **Test Locally First**: Always test Docker image locally before pushing to Snowflake
5. **Gradual Rollout**: Deploy to dev/test environments before production
6. **Document Changes**: Keep track of service specification changes
7. **Regular Updates**: Update base images and dependencies for security patches
8. **Backup Configuration**: Store service-spec.yaml and setup.sql in version control

## Next Steps

After successful deployment:

1. Share the endpoint URL with your sales team
2. Set up cost monitoring alerts
3. Customize pricing data in the JSON files for your organization
4. Add your company branding to the Streamlit theme
5. Train users on how to use the Migration Calculator
6. Gather feedback and iterate on features

---

**Deployed Version**: 1.0.0
**Last Updated**: 2024
**Deployment Target**: Snowpark Container Services
