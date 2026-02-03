"""Page 4: Best Practices."""

import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components import (
    inject_custom_css,
    create_info_box,
    create_warning_box,
    create_pdf_download_button,
    format_sql_for_pdf
)

st.set_page_config(
    page_title="Best Practices",
    page_icon="✨",
    layout="wide"
)

inject_custom_css()

st.title("✨ Best Practices & Optimization")

st.markdown("""
Learn strategies to optimize your compute pool configuration for cost efficiency,
performance, and maintainability.
""")

st.markdown("---")

# System vs User-Managed
st.markdown("## 🏛️ System vs User-Managed Compute Pools")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### System-Managed Pools

    **Snowflake manages:** Pool creation, scaling, lifecycle

    **Pros:**
    - Zero configuration
    - Automatic optimization
    - No management overhead
    - Good for simple use cases

    **Cons:**
    - Less control over costs
    - Limited customization
    - Shared resources

    **Best for:**
    - Quick prototyping
    - Small teams
    - Simple notebook workloads
    """)

with col2:
    st.markdown("""
    ### User-Managed Pools

    **You manage:** Pool creation, sizing, policies

    **Pros:**
    - Full cost control
    - Custom configurations
    - Dedicated resources
    - GPU access

    **Cons:**
    - Requires setup
    - Ongoing management
    - Need monitoring

    **Best for:**
    - Production workloads
    - Cost-sensitive environments
    - GPU requirements
    - Enterprise deployments
    """)

create_info_box("""
    <strong>💡 Recommendation:</strong> Use system-managed pools for development and testing,
    then migrate to user-managed pools for production workloads where you need cost control
    and performance guarantees.
""")

st.markdown("---")

# Right-Sizing Guide
st.markdown("## 🎯 Right-Sizing Calculator")

st.markdown("""
Determine the optimal instance family and node count for your workload:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Input Your Requirements")

    memory_needs = st.selectbox(
        "Memory Requirements",
        ["Low (<8GB)", "Medium (8-32GB)", "High (32-64GB)", "Very High (>64GB)"]
    )

    compute_intensity = st.selectbox(
        "Compute Intensity",
        ["Light (SQL, EDA)", "Moderate (Data Processing)", "Heavy (ML Training)", "Extreme (Deep Learning)"]
    )

    session_duration = st.selectbox(
        "Typical Session Duration",
        ["Short (<1 hour)", "Medium (1-4 hours)", "Long (4-8 hours)", "Extended (>8 hours)"]
    )

with col2:
    st.markdown("### Recommendation")

    # Simple recommendation logic
    if compute_intensity == "Extreme (Deep Learning)":
        rec_family = "GPU_NV_M or GPU_NV_L"
        rec_nodes = "2-4 nodes"
        rec_suspend = "30 minutes"
    elif memory_needs in ["High (32-64GB)", "Very High (>64GB)"]:
        rec_family = "HIGHMEM_X64_M or HIGHMEM_X64_L"
        rec_nodes = "1-3 nodes"
        rec_suspend = "15 minutes"
    elif compute_intensity == "Heavy (ML Training)":
        rec_family = "CPU_X64_L"
        rec_nodes = "2-4 nodes"
        rec_suspend = "20 minutes"
    else:
        rec_family = "CPU_X64_S or CPU_X64_M"
        rec_nodes = "1-2 nodes"
        rec_suspend = "10 minutes"

    st.markdown(f"""
    **Instance Family:** `{rec_family}`

    **Node Count:** {rec_nodes}

    **Auto-Suspend:** {rec_suspend}

    **Rationale:**
    - Memory: {memory_needs}
    - Compute: {compute_intensity}
    - Duration: {session_duration}
    """)

st.markdown("---")

# Idle Timeout Recommendations
st.markdown("## ⏱️ Idle Timeout Recommendations")

st.markdown("""
Optimize auto-suspend settings based on workload patterns:
""")

timeout_data = {
    "Workload Type": [
        "Interactive SQL Queries",
        "Data Exploration (EDA)",
        "Batch Data Processing",
        "ML Model Training",
        "Deep Learning (GPU)",
        "Development/Testing"
    ],
    "Recommended Timeout": [
        "5-10 minutes",
        "10-15 minutes",
        "15-20 minutes",
        "20-30 minutes",
        "30-60 minutes",
        "5 minutes"
    ],
    "Reasoning": [
        "Short pauses between queries, quick restart acceptable",
        "Medium pauses for analysis, balance cost vs UX",
        "Jobs run continuously, longer timeout prevents interruption",
        "Long training sessions, minimize restarts",
        "Expensive GPUs, but training jobs are long-running",
        "Frequent stops, optimize for cost over convenience"
    ],
    "Monthly Savings vs 60min": [
        "60-70%",
        "40-50%",
        "25-35%",
        "15-25%",
        "0-10%",
        "70-80%"
    ]
}

df_timeouts = pd.DataFrame(timeout_data)
st.dataframe(df_timeouts, use_container_width=True, hide_index=True)

create_warning_box("""
    <strong>⚠️ Warning:</strong> Setting timeout too short causes frequent restarts and poor UX.
    Setting it too long wastes credits on idle pools. Monitor actual usage patterns and adjust.
""")

st.markdown("---")

# Configuration Templates
st.markdown("## 📜 Configuration Templates")

st.markdown("""
Ready-to-use SQL templates for common scenarios:
""")

template_tabs = st.tabs([
    "Interactive Notebooks",
    "ML Training",
    "Batch Processing",
    "GPU Workloads"
])

with template_tabs[0]:
    st.markdown("### Interactive Data Analysis")
    sql_interactive = """
-- Optimal for: SQL queries, data exploration, ad-hoc analysis
CREATE COMPUTE POOL INTERACTIVE_NOTEBOOKS
  MIN_NODES = 1
  MAX_NODES = 3
  INSTANCE_FAMILY = CPU_X64_S
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = 600  -- 10 minutes
  COMMENT = 'Interactive notebook workloads with quick auto-suspend';

GRANT USAGE ON COMPUTE POOL INTERACTIVE_NOTEBOOKS TO ROLE DATA_ANALYST;
GRANT OPERATE ON COMPUTE POOL INTERACTIVE_NOTEBOOKS TO ROLE DATA_ANALYST;
"""
    st.code(sql_interactive, language="sql")
    st.download_button(
        "Download Template",
        sql_interactive,
        "interactive_notebooks.sql",
        use_container_width=True
    )

with template_tabs[1]:
    st.markdown("### Machine Learning Training")
    sql_ml = """
-- Optimal for: ML model training, feature engineering, CPU-based ML
CREATE COMPUTE POOL ML_TRAINING_POOL
  MIN_NODES = 2
  MAX_NODES = 5
  INSTANCE_FAMILY = CPU_X64_L
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = 1800  -- 30 minutes
  COMMENT = 'ML training workloads with extended sessions';

GRANT USAGE ON COMPUTE POOL ML_TRAINING_POOL TO ROLE ML_ENGINEER;
GRANT OPERATE ON COMPUTE POOL ML_TRAINING_POOL TO ROLE ML_ENGINEER;
"""
    st.code(sql_ml, language="sql")
    st.download_button(
        "Download Template",
        sql_ml,
        "ml_training.sql",
        use_container_width=True
    )

with template_tabs[2]:
    st.markdown("### Batch Data Processing")
    sql_batch = """
-- Optimal for: ETL pipelines, data transformations, scheduled jobs
CREATE COMPUTE POOL BATCH_PROCESSING
  MIN_NODES = 1
  MAX_NODES = 4
  INSTANCE_FAMILY = HIGHMEM_X64_M
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = 900  -- 15 minutes
  COMMENT = 'Batch processing with high memory for large datasets';

GRANT USAGE ON COMPUTE POOL BATCH_PROCESSING TO ROLE DATA_ENGINEER;
GRANT OPERATE ON COMPUTE POOL BATCH_PROCESSING TO ROLE DATA_ENGINEER;
"""
    st.code(sql_batch, language="sql")
    st.download_button(
        "Download Template",
        sql_batch,
        "batch_processing.sql",
        use_container_width=True
    )

with template_tabs[3]:
    st.markdown("### Deep Learning with GPU")
    sql_gpu = """
-- Optimal for: Deep learning, neural networks, GPU-accelerated workloads
CREATE COMPUTE POOL DL_GPU_POOL
  MIN_NODES = 1
  MAX_NODES = 2
  INSTANCE_FAMILY = GPU_NV_M
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = 3600  -- 60 minutes
  COMMENT = 'GPU pool for deep learning workloads';

GRANT USAGE ON COMPUTE POOL DL_GPU_POOL TO ROLE ML_ENGINEER;
GRANT OPERATE ON COMPUTE POOL DL_GPU_POOL TO ROLE ML_ENGINEER;
"""
    st.code(sql_gpu, language="sql")
    st.download_button(
        "Download Template",
        sql_gpu,
        "gpu_workloads.sql",
        use_container_width=True
    )

st.markdown("---")

# Optimization Strategies
st.markdown("## 🚀 Cost Optimization Strategies")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 1. Right-Size Instance Families
    - Start small (CPU_X64_S) and scale up
    - Use high-memory only when needed
    - Reserve GPUs for confirmed use cases

    ### 2. Optimize Auto-Suspend
    - Monitor idle time patterns
    - Adjust timeouts per workload
    - Balance UX vs cost

    ### 3. Node Count Management
    - Set MIN_NODES = 1 for most workloads
    - Increase MAX_NODES for burst capacity
    - Scale based on concurrent users

    ### 4. Consolidate Where Possible
    - Share pools across similar workloads
    - Avoid over-segmentation
    - Use naming conventions
    """)

with col2:
    st.markdown("""
    ### 5. Implement Monitoring
    - Track daily credit consumption
    - Set budget alerts
    - Review idle pools weekly

    ### 6. User Education
    - Train users on cost awareness
    - Encourage proper session cleanup
    - Share optimization tips

    ### 7. Leverage Tagging
    - Tag queries by project/user
    - Enable chargeback models
    - Track cost attribution

    ### 8. Regular Reviews
    - Monthly cost analysis
    - Quarterly configuration audits
    - Continuous optimization
    """)

st.markdown("---")

# PDF Export
st.markdown("## 📄 Export Best Practices Guide")

if st.button("📄 Generate PDF"):
    pdf_content = f"""
    <h2>Best Practices & Optimization</h2>

    <h3>System vs User-Managed Pools</h3>
    <p><strong>System-Managed:</strong> Zero config, automatic optimization, good for prototyping</p>
    <p><strong>User-Managed:</strong> Full control, custom configs, production workloads</p>

    <h3>Idle Timeout Recommendations</h3>
    {df_timeouts.to_html(index=False, border=0)}

    <h3>Configuration Templates</h3>

    <h4>Interactive Notebooks</h4>
    {format_sql_for_pdf(sql_interactive)}

    <h4>ML Training</h4>
    {format_sql_for_pdf(sql_ml)}

    <h4>Batch Processing</h4>
    {format_sql_for_pdf(sql_batch)}

    <h4>GPU Workloads</h4>
    {format_sql_for_pdf(sql_gpu)}

    <h3>Cost Optimization Checklist</h3>
    <ul>
        <li>Right-size instance families (start small)</li>
        <li>Optimize auto-suspend timeouts</li>
        <li>Manage node counts efficiently</li>
        <li>Consolidate similar workloads</li>
        <li>Implement comprehensive monitoring</li>
        <li>Educate users on cost awareness</li>
        <li>Use query tagging for attribution</li>
        <li>Conduct regular configuration reviews</li>
    </ul>
    """

    create_pdf_download_button(
        pdf_content,
        title="Best Practices Guide",
        filename="best_practices_guide.pdf"
    )

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Previous: Cost Monitoring"):
        st.switch_page("pages/3_Cost_Monitoring.py")

with col3:
    if st.button("Next: Getting Started ➡️"):
        st.switch_page("pages/5_Getting_Started.py")
