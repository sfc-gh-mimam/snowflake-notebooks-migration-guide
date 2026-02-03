"""Page 5: Getting Started - Setup Guide."""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components import (
    inject_custom_css,
    create_info_box,
    create_warning_box,
    create_pdf_download_button,
    format_sql_for_pdf
)

st.set_page_config(
    page_title="Getting Started",
    page_icon="🚀",
    layout="wide"
)

inject_custom_css()

st.title("🚀 Getting Started with Compute Pool Migration")

st.markdown("""
Step-by-step guide to migrate your notebooks from warehouse-backed to compute pool-backed execution.
""")

st.markdown("---")

# Prerequisites Checklist
st.markdown("## ✅ Prerequisites Checklist")

st.markdown("""
Before starting the migration, ensure you have:
""")

prereq_items = [
    ("Account Permissions", "ACCOUNTADMIN or role with COMPUTE POOL privileges"),
    ("Warehouse Access", "Current warehouse configuration documented"),
    ("Workload Analysis", "Understanding of notebook usage patterns"),
    ("Budget Approval", "Cost estimates reviewed and approved"),
    ("Network Configuration", "Firewall/networking rules if applicable"),
    ("Testing Environment", "Non-production environment for validation")
]

for item, description in prereq_items:
    checked = st.checkbox(f"**{item}**: {description}")

st.markdown("---")

# Setup Wizard
st.markdown("## 🧪 Step-by-Step Migration Wizard")

st.markdown("""
Follow these steps to complete your migration:
""")

# Step 1
with st.expander("① Create Compute Pool", expanded=True):
    st.markdown("""
    ### Create Your Compute Pool

    Use the SQL below (customized from Migration Calculator) or start with a basic configuration:
    """)

    col1, col2 = st.columns(2)

    with col1:
        pool_name_setup = st.text_input("Pool Name", value="NOTEBOOK_POOL", key="setup_pool_name")
        instance_family = st.selectbox(
            "Instance Family",
            ["CPU_X64_S", "CPU_X64_M", "CPU_X64_L", "HIGHMEM_X64_M", "HIGHMEM_X64_L", "GPU_NV_S", "GPU_NV_M"],
            key="setup_instance"
        )

    with col2:
        min_nodes = st.number_input("Min Nodes", min_value=1, max_value=10, value=1, key="setup_min")
        max_nodes = st.number_input("Max Nodes", min_value=1, max_value=20, value=3, key="setup_max")

    auto_suspend = st.slider("Auto-Suspend (minutes)", 5, 60, 15, key="setup_suspend")

    setup_sql = f"""
-- Step 1: Create Compute Pool
CREATE COMPUTE POOL {pool_name_setup}
  MIN_NODES = {min_nodes}
  MAX_NODES = {max_nodes}
  INSTANCE_FAMILY = {instance_family}
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = {auto_suspend * 60}
  COMMENT = 'Compute pool for migrated notebook workloads';
"""

    st.code(setup_sql, language="sql")
    st.download_button("Download SQL", setup_sql, "01_create_pool.sql", use_container_width=True)

    create_info_box("""
        <strong>💡 Tip:</strong> Start with conservative settings (small instance, low max nodes)
        and scale up based on actual usage patterns.
    """)

# Step 2
with st.expander("② Grant Permissions"):
    st.markdown("""
    ### Configure Access Control

    Grant necessary permissions to roles that will use the compute pool:
    """)

    role_name = st.text_input("Role Name", value="DATA_SCIENTIST", key="role_name")

    permission_sql = f"""
-- Step 2: Grant Permissions
-- Grant USAGE to allow role to use the compute pool
GRANT USAGE ON COMPUTE POOL {pool_name_setup} TO ROLE {role_name};

-- Grant OPERATE for administrative operations (optional)
GRANT OPERATE ON COMPUTE POOL {pool_name_setup} TO ROLE {role_name};

-- Grant MONITOR to view pool status and metrics (optional)
GRANT MONITOR ON COMPUTE POOL {pool_name_setup} TO ROLE {role_name};
"""

    st.code(permission_sql, language="sql")
    st.download_button("Download SQL", permission_sql, "02_grant_permissions.sql", use_container_width=True)

    st.markdown("""
    **Permission Levels:**
    - `USAGE`: Required to use the pool for notebooks
    - `OPERATE`: Allows starting/stopping the pool
    - `MONITOR`: Enables viewing pool status and metrics
    """)

# Step 3
with st.expander("③ Configure Notebook Service"):
    st.markdown("""
    ### Link Notebooks to Compute Pool

    Update notebook configuration to use the new compute pool:
    """)

    config_sql = f"""
-- Step 3: Configure Notebook Service
-- Set default compute pool for notebook sessions
ALTER ACCOUNT SET DEFAULT_NOTEBOOK_COMPUTE_POOL = '{pool_name_setup}';

-- Or configure at database/schema level:
ALTER DATABASE <YOUR_DATABASE> SET DEFAULT_NOTEBOOK_COMPUTE_POOL = '{pool_name_setup}';
ALTER SCHEMA <YOUR_SCHEMA> SET DEFAULT_NOTEBOOK_COMPUTE_POOL = '{pool_name_setup}';
"""

    st.code(config_sql, language="sql")
    st.download_button("Download SQL", config_sql, "03_configure_notebooks.sql", use_container_width=True)

    create_warning_box("""
        <strong>⚠️ Note:</strong> Setting at account level affects all notebooks.
        Consider schema or database level for gradual rollout.
    """)

# Step 4
with st.expander("④ Test Connection"):
    st.markdown("""
    ### Validate Setup

    Test that notebooks can connect to the new compute pool:
    """)

    test_steps = [
        "Open an existing notebook in Snowflake",
        "Check that it's configured to use the new compute pool",
        "Run a simple query to verify connectivity",
        "Monitor compute pool status in Snowsight",
        "Verify credits are being consumed as expected"
    ]

    for i, step in enumerate(test_steps, 1):
        st.markdown(f"{i}. {step}")

    st.markdown("""
    **Test Query:**
    ```python
    # In notebook cell:
    from snowflake.snowpark import Session

    # Verify current compute pool
    session.sql("SELECT CURRENT_COMPUTE_POOL()").show()

    # Run simple test
    session.sql("SELECT 'Hello from compute pool!'").show()
    ```
    """)

    test_sql = f"""
-- Verify compute pool is active
SHOW COMPUTE POOLS LIKE '{pool_name_setup}';

-- Check pool status
SELECT * FROM TABLE(
  INFORMATION_SCHEMA.COMPUTE_POOL_STATUS('{pool_name_setup}')
);

-- View recent activity
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE service_type = 'COMPUTE_POOL'
  AND name = '{pool_name_setup}'
  AND start_time >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;
"""

    st.code(test_sql, language="sql")
    st.download_button("Download SQL", test_sql, "04_test_connection.sql", use_container_width=True)

st.markdown("---")

# Migration Workflow
st.markdown("## 🔄 Migration Workflow")

st.markdown("""
Recommended phased approach for enterprise migrations:
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### Phase 1: Pilot
    - Select 2-3 notebooks
    - Migrate to compute pool
    - Monitor for 1-2 weeks
    - Gather user feedback
    - Measure cost impact
    """)

with col2:
    st.markdown("""
    ### Phase 2: Expansion
    - Migrate 25% of notebooks
    - Establish monitoring
    - Train users
    - Refine configurations
    - Document learnings
    """)

with col3:
    st.markdown("""
    ### Phase 3: Completion
    - Migrate remaining notebooks
    - Decommission warehouses
    - Optimize configurations
    - Establish ongoing review
    - Celebrate success!
    """)

st.markdown("---")

# Validation Tests
st.markdown("## ✅ Post-Migration Validation")

st.markdown("""
Run these checks after migration to ensure everything works correctly:
""")

validation_tests = [
    ("Connectivity", "All notebooks connect to compute pool", "SELECT CURRENT_COMPUTE_POOL();"),
    ("Performance", "Query performance meets expectations", "Run representative workload and compare timing"),
    ("Package Persistence", "Custom packages persist across sessions", "Install package, disconnect, reconnect, verify"),
    ("Credit Consumption", "Credits tracking in METERING_HISTORY", "SELECT * FROM METERING_HISTORY WHERE service_type='COMPUTE_POOL'"),
    ("Auto-Suspend", "Pool suspends after idle period", "Monitor pool status after idle time"),
    ("User Access", "All authorized users can access", "Have each user test notebook access"),
    ("Cost Comparison", "Actual costs vs projections", "Compare first week actual vs calculator estimate")
]

for test_name, description, validation in validation_tests:
    with st.expander(f"✅ {test_name}"):
        st.markdown(f"**Test:** {description}")
        st.markdown(f"**Validation:** `{validation}`")
        passed = st.checkbox(f"Passed: {test_name}", key=f"validation_{test_name}")

st.markdown("---")

# Troubleshooting
st.markdown("## 🔧 Common Issues & Solutions")

troubleshooting_tabs = st.tabs([
    "Connection Errors",
    "Performance Issues",
    "Cost Surprises",
    "Package Problems"
])

with troubleshooting_tabs[0]:
    st.markdown("""
    ### Connection Errors

    **Problem:** Notebook fails to connect to compute pool

    **Solutions:**
    1. Check permissions: `SHOW GRANTS ON COMPUTE POOL <pool_name>;`
    2. Verify pool is running: `SHOW COMPUTE POOLS;`
    3. Check pool status: `SELECT * FROM INFORMATION_SCHEMA.COMPUTE_POOL_STATUS('<pool_name>');`
    4. Restart pool if needed: `ALTER COMPUTE POOL <pool_name> RESUME;`
    5. Review account configuration
    """)

with troubleshooting_tabs[1]:
    st.markdown("""
    ### Performance Issues

    **Problem:** Queries running slower than expected

    **Solutions:**
    1. Check instance family - may need larger instances
    2. Increase MAX_NODES for better parallelism
    3. Monitor node utilization
    4. Review query patterns for optimization
    5. Consider switching to high-memory instances
    6. Check network latency if using external data
    """)

with troubleshooting_tabs[2]:
    st.markdown("""
    ### Cost Surprises

    **Problem:** Costs higher than projected

    **Solutions:**
    1. Check idle pools: Run idle detection query
    2. Review auto-suspend settings - may be too long
    3. Identify heavy users with attribution query
    4. Verify MIN_NODES not set too high
    5. Look for runaway queries
    6. Implement budget alerts
    7. Review actual vs expected usage hours
    """)

with troubleshooting_tabs[3]:
    st.markdown("""
    ### Package Problems

    **Problem:** Python packages not working correctly

    **Solutions:**
    1. Verify package installed in persistent environment
    2. Check Python version compatibility
    3. Review package dependencies
    4. Use requirements.txt for consistency
    5. Clear package cache if needed
    6. Consider container image customization
    """)

st.markdown("---")

# PDF Export
st.markdown("## 📄 Export Setup Guide")

if st.button("📄 Generate Complete Setup PDF"):
    pdf_content = f"""
    <h2>Getting Started with Compute Pool Migration</h2>

    <h3>Prerequisites Checklist</h3>
    <ul>
        <li>Account permissions (ACCOUNTADMIN or COMPUTE POOL privileges)</li>
        <li>Warehouse access documentation</li>
        <li>Workload analysis complete</li>
        <li>Budget approval obtained</li>
        <li>Network configuration verified</li>
        <li>Testing environment prepared</li>
    </ul>

    <h3>Step 1: Create Compute Pool</h3>
    {format_sql_for_pdf(setup_sql)}

    <h3>Step 2: Grant Permissions</h3>
    {format_sql_for_pdf(permission_sql)}

    <h3>Step 3: Configure Notebook Service</h3>
    {format_sql_for_pdf(config_sql)}

    <h3>Step 4: Test Connection</h3>
    {format_sql_for_pdf(test_sql)}

    <h3>Migration Phases</h3>
    <ol>
        <li><strong>Pilot:</strong> 2-3 notebooks, monitor 1-2 weeks</li>
        <li><strong>Expansion:</strong> 25% of notebooks, establish monitoring</li>
        <li><strong>Completion:</strong> Remaining notebooks, optimize configs</li>
    </ol>

    <h3>Validation Checklist</h3>
    <ul>
        <li>Connectivity test passed</li>
        <li>Performance meets expectations</li>
        <li>Package persistence verified</li>
        <li>Credit consumption tracking</li>
        <li>Auto-suspend functioning</li>
        <li>User access confirmed</li>
        <li>Cost comparison validated</li>
    </ul>

    <h3>Support Resources</h3>
    <ul>
        <li>Snowflake Documentation: docs.snowflake.com</li>
        <li>Account Team: Contact your Snowflake representative</li>
        <li>Community: community.snowflake.com</li>
    </ul>
    """

    create_pdf_download_button(
        pdf_content,
        title="Complete Setup Guide",
        filename="setup_guide.pdf"
    )

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Previous: Best Practices"):
        st.switch_page("pages/4_Best_Practices.py")

with col2:
    if st.button("🏠 Back to Home"):
        st.switch_page("main.py")

with col3:
    if st.button("🧮 Go to Calculator"):
        st.switch_page("pages/2_Migration_Calculator.py")
