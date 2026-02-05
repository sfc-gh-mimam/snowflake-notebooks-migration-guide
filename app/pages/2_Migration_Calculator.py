"""Page 2: Migration Calculator - Primary Tool."""

import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components import (
    inject_custom_css,
    create_info_box,
    create_disclaimer,
    create_cost_comparison_chart,
    create_resource_comparison,
    create_pdf_download_button,
    format_table_for_pdf,
    format_sql_for_pdf
)

from models import (
    recommend_compute_pool,
    get_warehouse_by_code,
    get_migration_sql,
    compare_costs,
    load_warehouse_specs
)

st.set_page_config(
    page_title="Migration Calculator",
    page_icon="🧮",
    layout="wide"
)

inject_custom_css()

st.title("🧮 Migration Calculator")

st.markdown("""
Get instant compute pool recommendations based on your current warehouse configuration and workload characteristics.
This calculator provides cost comparisons, resource specifications, and ready-to-use SQL for migration.
""")

create_disclaimer()

create_info_box("""
    <strong>💰 Why Compute Pools Are Cheaper:</strong><br><br>
    <strong>Compute pool credits cost significantly less</strong> than warehouse credits for equivalent compute capacity.
    A typical notebook workload can see <strong>2-5x cost savings</strong> by migrating to compute pools.<br><br>
    <strong>Example:</strong> Small warehouse (2 credits/hr) vs CPU_X64_S pool (0.11 credits/hr) = ~18x cheaper per hour!<br><br>
    <em>Note: If you share a warehouse with other workloads, your marginal notebook cost may be lower,
    but dedicated notebook compute pools still offer better economics and resource isolation.</em>
""")

st.markdown("---")

# Input Section
st.markdown("## 📝 Configuration Input")

col1, col2 = st.columns(2)

with col1:
    warehouse_size = st.selectbox(
        "Current Warehouse Size",
        ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL", "6XL"],
        help="Select your current warehouse size for notebooks"
    )

    workload_type = st.selectbox(
        "Workload Type",
        ["SQL-heavy", "ML-heavy", "Balanced", "Interactive"],
        help="Primary workload characteristics"
    )

    concurrent_users = st.number_input(
        "Expected Concurrent Users",
        min_value=1,
        max_value=100,
        value=5,
        help="Number of users working simultaneously"
    )

with col2:
    gpu_required = st.checkbox(
        "GPU Required",
        value=False,
        help="Check if workload requires GPU acceleration (deep learning, etc.)"
    )

    hours_per_day = st.slider(
        "Notebook Session Hours Per Day",
        min_value=1.0,
        max_value=24.0,
        value=8.0,
        step=0.5,
        help="How long notebooks are open/active per day"
    )

    credit_rate = st.number_input(
        "Credit Rate (USD)",
        min_value=1.0,
        max_value=10.0,
        value=4.0,
        step=0.5,
        help="Your Snowflake credit rate (default: $4)"
    )

# Calculate Button
if st.button("🔍 Calculate Recommendation", type="primary", use_container_width=True):

    # Store results in session state
    try:
        warehouse = get_warehouse_by_code(warehouse_size)
        recommendation = recommend_compute_pool(
            warehouse_size=warehouse_size,
            workload_type=workload_type,
            concurrent_users=concurrent_users,
            gpu_required=gpu_required
        )

        comparison = compare_costs(
            warehouse=warehouse,
            recommendation=recommendation,
            hours_per_day=hours_per_day,
            credit_rate=credit_rate
        )

        st.session_state['calculation_done'] = True
        st.session_state['warehouse'] = warehouse
        st.session_state['recommendation'] = recommendation
        st.session_state['comparison'] = comparison
        st.session_state['inputs'] = {
            'warehouse_size': warehouse_size,
            'workload_type': workload_type,
            'concurrent_users': concurrent_users,
            'gpu_required': gpu_required,
            'hours_per_day': hours_per_day,
            'credit_rate': credit_rate
        }

    except Exception as e:
        st.error(f"Error calculating recommendation: {str(e)}")

# Results Section
if st.session_state.get('calculation_done', False):
    st.markdown("---")
    st.markdown("## 📊 Recommendation Results")

    recommendation = st.session_state['recommendation']
    comparison = st.session_state['comparison']
    warehouse = st.session_state['warehouse']
    inputs = st.session_state['inputs']

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Instance Family",
            recommendation['instance_family'],
            delta=recommendation['instance_type']
        )

    with col2:
        st.metric(
            "Recommended Nodes",
            f"{recommendation['recommended_min_nodes']}-{recommendation['recommended_max_nodes']}",
            delta="Min-Max"
        )

    with col3:
        savings = comparison['monthly_savings']
        savings_pct = comparison['savings_percent']
        st.metric(
            "Monthly Savings",
            f"${abs(savings):,.2f}",
            delta=f"{abs(savings_pct):.1f}% {'saved' if savings > 0 else 'more'}",
            delta_color="normal" if savings > 0 else "inverse"
        )

    with col4:
        st.metric(
            "Auto-Suspend",
            f"{recommendation['auto_suspend_minutes']} min",
            delta="Recommended"
        )

    st.markdown("---")

    # Resource Comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Resource Specifications")

        specs_data = {
            "Specification": ["Memory (GB)", "vCPU", "Credits/Hour"],
            "Warehouse": [
                warehouse['memory_gb'],
                warehouse['vcpu'],
                f"{warehouse['credits_per_hour']:.2f}"
            ],
            "Compute Pool (per node)": [
                recommendation['memory_gb'],
                recommendation['vcpu'],
                f"{recommendation['credits_per_hour']:.2f}"
            ]
        }

        if inputs['gpu_required']:
            specs_data["Specification"].extend(["GPU Memory (GB)", "GPU Count"])
            specs_data["Warehouse"].extend(["N/A", "N/A"])
            specs_data["Compute Pool (per node)"].extend([
                recommendation['gpu_details']['gpu_memory_gb'],
                recommendation['gpu_details']['gpu_count']
            ])

        df_specs = pd.DataFrame(specs_data)
        st.dataframe(df_specs, use_container_width=True, hide_index=True)

        # Show savings message
        if savings > 0:
            create_info_box(f"""
                <strong>✅ Compute Pool is {abs(savings_pct):.0f}% cheaper!</strong><br><br>
                Migrating to <strong>{recommendation['instance_family']}</strong> saves
                <strong>${abs(savings):,.2f}/month</strong> compared to the {warehouse_size} warehouse.<br><br>
                <strong>Recommendation:</strong> {recommendation['description']}
            """)
        else:
            create_info_box(f"""
                <strong>💡 Recommendation:</strong> {recommendation['description']}
                <br><br>
                <strong>Workload Multiplier:</strong> {recommendation['workload_multiplier']}x
                applied for {inputs['workload_type']} workload type.
            """)

    with col2:
        st.markdown("### Cost Comparison")

        # Cost comparison chart
        fig = create_cost_comparison_chart(comparison)
        st.plotly_chart(fig, use_container_width=True)

        # Detailed cost breakdown
        wh_cost = comparison['warehouse_cost']['monthly_cost']
        pool_cost = comparison['compute_pool_cost']['monthly_cost']

        cost_details = {
            "Metric": [
                "Monthly Cost",
                "Credits/Hour",
                "Total Hours/Month",
                "Total Credits/Month"
            ],
            "Warehouse": [
                f"${wh_cost:,.2f}",
                f"{comparison['warehouse_cost']['credits_per_hour']:.2f}",
                f"{comparison['warehouse_cost']['total_hours']:.1f}",
                f"{comparison['warehouse_cost']['total_credits']:.2f}"
            ],
            "Compute Pool": [
                f"${pool_cost:,.2f}",
                f"{comparison['compute_pool_cost']['credits_per_hour']:.2f}",
                f"{comparison['compute_pool_cost']['total_hours']:.1f}",
                f"{comparison['compute_pool_cost']['total_credits']:.2f}"
            ]
        }

        df_costs = pd.DataFrame(cost_details)
        st.dataframe(df_costs, use_container_width=True, hide_index=True)

    st.markdown("---")

    # SQL Generation
    st.markdown("### 📜 Migration SQL")

    pool_name = st.text_input(
        "Compute Pool Name",
        value="NOTEBOOK_COMPUTE_POOL",
        help="Name for your new compute pool"
    )

    migration_sql = get_migration_sql(recommendation, pool_name)

    st.code(migration_sql, language="sql")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download SQL",
            data=migration_sql,
            file_name=f"{pool_name}_migration.sql",
            mime="text/sql",
            use_container_width=True
        )

    with col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.code(migration_sql, language="sql")
            st.success("SQL displayed above - copy manually")

    st.markdown("---")

    # Scenario Comparison
    st.markdown("### 📊 Save & Compare Scenarios")

    if 'scenarios' not in st.session_state:
        st.session_state['scenarios'] = []

    scenario_name = st.text_input(
        "Scenario Name",
        value=f"{warehouse_size}_{workload_type}",
        help="Give this configuration a name"
    )

    if st.button("💾 Save Scenario") and len(st.session_state['scenarios']) < 3:
        st.session_state['scenarios'].append({
            'name': scenario_name,
            'inputs': inputs,
            'recommendation': recommendation,
            'comparison': comparison
        })
        st.success(f"Scenario '{scenario_name}' saved!")

    if st.session_state['scenarios']:
        st.markdown("#### Saved Scenarios")

        scenario_data = {
            "Scenario": [],
            "Warehouse Size": [],
            "Instance Family": [],
            "Nodes": [],
            "Monthly Cost": [],
            "Savings": []
        }

        for scenario in st.session_state['scenarios']:
            scenario_data["Scenario"].append(scenario['name'])
            scenario_data["Warehouse Size"].append(scenario['inputs']['warehouse_size'])
            scenario_data["Instance Family"].append(scenario['recommendation']['instance_family'])
            scenario_data["Nodes"].append(
                f"{scenario['recommendation']['recommended_min_nodes']}-"
                f"{scenario['recommendation']['recommended_max_nodes']}"
            )
            scenario_data["Monthly Cost"].append(
                f"${scenario['comparison']['compute_pool_cost']['monthly_cost']:,.2f}"
            )
            scenario_data["Savings"].append(
                f"${scenario['comparison']['monthly_savings']:,.2f}"
            )

        df_scenarios = pd.DataFrame(scenario_data)
        st.dataframe(df_scenarios, use_container_width=True, hide_index=True)

        if st.button("🗑️ Clear All Scenarios"):
            st.session_state['scenarios'] = []
            st.rerun()

    # PDF Export
    st.markdown("---")
    st.markdown("### 📄 Export Report")

    if st.button("📄 Generate PDF Report"):
        pdf_content = f"""
        <h2>Migration Calculator Results</h2>

        <h3>Input Configuration</h3>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            <tr><td>Warehouse Size</td><td>{inputs['warehouse_size']}</td></tr>
            <tr><td>Workload Type</td><td>{inputs['workload_type']}</td></tr>
            <tr><td>Concurrent Users</td><td>{inputs['concurrent_users']}</td></tr>
            <tr><td>GPU Required</td><td>{'Yes' if inputs['gpu_required'] else 'No'}</td></tr>
            <tr><td>Hours/Day</td><td>{inputs['hours_per_day']}</td></tr>
            <tr><td>Credit Rate</td><td>${inputs['credit_rate']}</td></tr>
        </table>

        <h3>Recommendation</h3>
        <p><strong>Instance Family:</strong> {recommendation['instance_family']}</p>
        <p><strong>Nodes:</strong> {recommendation['recommended_min_nodes']} - {recommendation['recommended_max_nodes']}</p>
        <p><strong>Auto-Suspend:</strong> {recommendation['auto_suspend_minutes']} minutes</p>
        <p><strong>Description:</strong> {recommendation['description']}</p>

        <h3>Resource Specifications</h3>
        {format_table_for_pdf(df_specs)}

        <h3>Cost Comparison</h3>
        {format_table_for_pdf(df_costs)}

        <p><strong>Monthly Savings:</strong> ${comparison['monthly_savings']:,.2f}
        ({comparison['savings_percent']:.1f}%)</p>

        <h3>Migration SQL</h3>
        {format_sql_for_pdf(migration_sql)}
        """

        create_pdf_download_button(
            pdf_content,
            title="Migration Calculator Results",
            filename=f"migration_recommendation_{warehouse_size}.pdf"
        )

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Previous: Why Compute Pools?"):
        st.switch_page("pages/1_Why_Compute_Pools.py")

with col3:
    if st.button("Next: Cost Monitoring ➡️"):
        st.switch_page("pages/3_Cost_Monitoring.py")
