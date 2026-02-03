"""Page 3: Cost Monitoring - SQL Library."""

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
    page_title="Cost Monitoring",
    page_icon="📋",
    layout="wide"
)

inject_custom_css()

st.title("📋 Cost Monitoring & Budget Management")

st.markdown("""
Access production-ready SQL queries for tracking compute pool costs, setting up budgets,
and monitoring usage patterns. All queries are copy-paste ready for immediate use.
""")

create_info_box("""
    <strong>💡 Pro Tip:</strong> Start with the Budget Setup queries to establish monitoring,
    then use daily tracking queries to maintain visibility into your compute pool costs.
""")

st.markdown("---")

# Load SQL templates
def load_sql_template(filename):
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "sql_templates", filename
    )
    with open(path, "r") as f:
        return f.read()

# Budget Setup Guide
st.markdown("## 🎯 Budget Setup & Tracking")

create_warning_box("""
    <strong>⚠️ Important:</strong> Resource Monitors do NOT work with compute pools.
    You must use custom queries and tables to track budgets.
""")

budget_sql = load_sql_template("budget_setup.sql")

st.markdown("""
### Step-by-Step Budget Setup

1. **Create Budget Tracking Table** - Store monthly budget thresholds
2. **Insert Budget Configuration** - Define credit and USD limits
3. **Monitor Current Usage** - Query month-to-date consumption
4. **Track Burn Rate** - Calculate daily spending and projections
""")

tab1, tab2 = st.tabs(["View SQL", "Setup Guide"])

with tab1:
    st.code(budget_sql, language="sql")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download Budget Setup SQL",
            data=budget_sql,
            file_name="budget_setup.sql",
            mime="text/sql",
            use_container_width=True
        )

with tab2:
    st.markdown("""
    #### Setup Instructions

    **Step 1: Create the tracking table**
    ```sql
    CREATE TABLE compute_pool_budgets (...)
    ```
    This creates a centralized table to store budget configurations for all compute pools.

    **Step 2: Configure your budget**
    - Set `monthly_budget_credits` based on expected usage
    - Calculate `monthly_budget_usd` using your credit rate
    - Set `alert_threshold_percent` (recommended: 80%)

    **Step 3: Run monitoring queries**
    - Execute the "current month usage" query daily
    - Review the status column for threshold alerts
    - Use burn rate query to project month-end costs

    **Step 4: Set up automated alerts**
    - Schedule queries using Snowflake Tasks
    - Send alerts via email or Slack when thresholds exceeded
    - Review and adjust budgets monthly
    """)

st.markdown("---")

# Daily Cost Monitoring
st.markdown("## 📈 Daily Credit Consumption")

cost_monitoring_sql = load_sql_template("cost_monitoring.sql")

st.markdown("""
Track daily credit usage for your compute pools using the `METERING_HISTORY` view.
This query provides daily aggregations with cost estimates.
""")

st.code(cost_monitoring_sql, language="sql")

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        label="📥 Download Cost Monitoring SQL",
        data=cost_monitoring_sql,
        file_name="cost_monitoring.sql",
        mime="text/sql",
        use_container_width=True
    )

with col2:
    pool_name = st.text_input(
        "Customize Pool Name",
        value="<YOUR_COMPUTE_POOL_NAME>",
        help="Replace placeholder with your actual pool name"
    )
    if pool_name != "<YOUR_COMPUTE_POOL_NAME>":
        customized_sql = cost_monitoring_sql.replace("<YOUR_COMPUTE_POOL_NAME>", pool_name)
        st.download_button(
            label="📥 Download Customized SQL",
            data=customized_sql,
            file_name=f"cost_monitoring_{pool_name}.sql",
            mime="text/sql",
            use_container_width=True
        )

st.markdown("---")

# Usage Query Library
st.markdown("## 📚 Advanced Monitoring Queries")

usage_queries_sql = load_sql_template("usage_queries.sql")

st.markdown("""
Comprehensive collection of queries for detailed cost analysis and optimization:
""")

query_tabs = st.tabs([
    "Hourly Patterns",
    "Idle Detection",
    "User Attribution",
    "Workload Costs",
    "Migration Analysis",
    "Peak Hours",
    "Weekly Trends"
])

# Split the usage queries by section
query_sections = usage_queries_sql.split("-- Query ")

with query_tabs[0]:
    st.markdown("### Hourly Credit Consumption Pattern")
    st.markdown("Identify usage patterns throughout the day to optimize auto-suspend settings.")
    if len(query_sections) > 1:
        st.code("-- Query " + query_sections[1], language="sql")

with query_tabs[1]:
    st.markdown("### Detect Idle Compute Pools")
    st.markdown("Find pools consuming credits with minimal query activity.")
    if len(query_sections) > 2:
        st.code("-- Query " + query_sections[2], language="sql")

with query_tabs[2]:
    st.markdown("### User-Level Cost Attribution")
    st.markdown("Track which users are driving compute pool costs for chargeback.")
    if len(query_sections) > 3:
        st.code("-- Query " + query_sections[3], language="sql")

with query_tabs[3]:
    st.markdown("### Cost by Workload Type")
    st.markdown("Analyze costs by workload category (requires query tagging).")
    if len(query_sections) > 4:
        st.code("-- Query " + query_sections[4], language="sql")

with query_tabs[4]:
    st.markdown("### Compare Warehouse vs Pool Costs")
    st.markdown("Track actual cost differences after migration.")
    if len(query_sections) > 5:
        st.code("-- Query " + query_sections[5], language="sql")

with query_tabs[5]:
    st.markdown("### Peak Usage Hours Identification")
    st.markdown("Understand when your compute pools are most active.")
    if len(query_sections) > 6:
        st.code("-- Query " + query_sections[6], language="sql")

with query_tabs[6]:
    st.markdown("### Weekly Cost Trends")
    st.markdown("Track spending patterns over weeks for budget forecasting.")
    if len(query_sections) > 7:
        st.code("-- Query " + query_sections[7], language="sql")

st.download_button(
    label="📥 Download All Usage Queries",
    data=usage_queries_sql,
    file_name="usage_queries.sql",
    mime="text/sql",
    use_container_width=True
)

st.markdown("---")

# Alert Threshold Calculator
st.markdown("## 🚨 Alert Threshold Calculator")

st.markdown("""
Calculate appropriate alert thresholds based on your monthly budget.
""")

col1, col2 = st.columns(2)

with col1:
    monthly_budget = st.number_input(
        "Monthly Budget (USD)",
        min_value=100.0,
        max_value=100000.0,
        value=5000.0,
        step=100.0
    )

    working_days = st.number_input(
        "Working Days per Month",
        min_value=1,
        max_value=31,
        value=22
    )

    alert_percent = st.slider(
        "Alert Threshold (%)",
        min_value=50,
        max_value=100,
        value=80,
        step=5
    )

with col2:
    daily_budget = monthly_budget / working_days
    weekly_budget = daily_budget * 5
    alert_threshold = monthly_budget * (alert_percent / 100)

    st.markdown("### Calculated Thresholds")
    st.metric("Daily Budget", f"${daily_budget:,.2f}")
    st.metric("Weekly Budget", f"${weekly_budget:,.2f}")
    st.metric("Alert Threshold", f"${alert_threshold:,.2f}")
    st.metric("Remaining After Alert", f"${monthly_budget - alert_threshold:,.2f}")

create_info_box(f"""
    <strong>Recommendation:</strong> Set up daily monitoring to track against
    ${daily_budget:,.2f}/day budget. Alert triggers at ${alert_threshold:,.2f}
    total monthly spend ({alert_percent}% of budget).
""")

st.markdown("---")

# PDF Export
st.markdown("## 📄 Export Monitoring Guide")

if st.button("📄 Generate PDF with All Queries"):
    pdf_content = f"""
    <h2>Cost Monitoring & Budget Management</h2>

    <h3>Budget Setup</h3>
    <p>Resource Monitors do not work with compute pools. Use custom tracking tables.</p>
    {format_sql_for_pdf(budget_sql)}

    <h3>Daily Cost Monitoring</h3>
    {format_sql_for_pdf(cost_monitoring_sql)}

    <h3>Advanced Usage Queries</h3>
    {format_sql_for_pdf(usage_queries_sql)}

    <h3>Alert Thresholds</h3>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Monthly Budget</td><td>${monthly_budget:,.2f}</td></tr>
        <tr><td>Daily Budget</td><td>${daily_budget:,.2f}</td></tr>
        <tr><td>Alert Threshold ({alert_percent}%)</td><td>${alert_threshold:,.2f}</td></tr>
    </table>

    <h3>Implementation Checklist</h3>
    <ul>
        <li>Create budget tracking table</li>
        <li>Insert budget configurations</li>
        <li>Schedule daily monitoring queries</li>
        <li>Set up alert notifications</li>
        <li>Implement user attribution strategy</li>
        <li>Configure query tagging</li>
        <li>Review and optimize monthly</li>
    </ul>
    """

    create_pdf_download_button(
        pdf_content,
        title="Cost Monitoring Guide",
        filename="cost_monitoring_guide.pdf"
    )

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Previous: Migration Calculator"):
        st.switch_page("pages/2_Migration_Calculator.py")

with col3:
    if st.button("Next: Best Practices ➡️"):
        st.switch_page("pages/4_Best_Practices.py")
