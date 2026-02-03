"""Page 1: Why Compute Pools?"""

import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components import (
    inject_custom_css,
    create_header,
    create_info_box,
    create_warning_box,
    create_pdf_download_button
)

st.set_page_config(
    page_title="Why Compute Pools?",
    page_icon="❓",
    layout="wide"
)

inject_custom_css()

st.title("❓ Why Migrate to Compute Pools?")

create_warning_box("""
    <strong>⚠️ Deprecation Notice:</strong> Warehouse-backed notebooks will be deprecated. 
    All customers must migrate to compute pool-backed notebooks to continue using Snowflake Notebooks.
""")

st.markdown("---")

# Key differences section
st.markdown("## Key Differences")

# Create comparison table
comparison_data = {
    "Feature": [
        "Environment Persistence",
        "Session Duration",
        "GPU Support",
        "Custom Packages",
        "Resource Isolation",
        "Scaling Model",
        "Cost Model",
        "Container Control"
    ],
    "Warehouse-Backed (Legacy)": [
        "Ephemeral - lost on disconnect",
        "Limited by warehouse timeout",
        "Not available",
        "Limited, session-scoped",
        "Shared warehouse resources",
        "Warehouse scaling (clusters)",
        "Warehouse credit consumption",
        "Limited control"
    ],
    "Compute Pool-Backed (Current)": [
        "Persistent containers",
        "Extended sessions (hours/days)",
        "Full GPU support",
        "Flexible, persistent packages",
        "Dedicated container resources",
        "Node-based scaling",
        "Compute pool credit consumption",
        "Full container lifecycle control"
    ]
}

df_comparison = pd.DataFrame(comparison_data)
st.dataframe(df_comparison, use_container_width=True, hide_index=True)

st.markdown("---")

# Benefits section
st.markdown("## Benefits of Compute Pools")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="enterprise-card">
        <h3 style="color: #29B5E8;">💎 Persistent Environments</h3>
        <p><strong>What it means:</strong> Your notebook environment (packages, data, state) 
        persists between sessions.</p>
        <p><strong>Why it matters:</strong> No need to reinstall packages or reload data every 
        time you reconnect. Faster startup, better productivity.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="enterprise-card">
        <h3 style="color: #29B5E8;">📊 Better Resource Allocation</h3>
        <p><strong>What it means:</strong> Dedicated container resources with predictable 
        performance characteristics.</p>
        <p><strong>Why it matters:</strong> No resource contention with other warehouse 
        workloads. Consistent performance for ML training and data processing.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="enterprise-card">
        <h3 style="color: #29B5E8;">🔧 Flexible Configuration</h3>
        <p><strong>What it means:</strong> Choose instance types optimized for your workload 
        (CPU, high-memory, GPU).</p>
        <p><strong>Why it matters:</strong> Right-size resources for cost efficiency. GPU 
        support enables deep learning and advanced analytics.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="enterprise-card">
        <h3 style="color: #29B5E8;">⏱️ Extended Sessions</h3>
        <p><strong>What it means:</strong> Notebook sessions can run for extended periods 
        without interruption.</p>
        <p><strong>Why it matters:</strong> Long-running ML training jobs don't get interrupted. 
        Better for iterative development and experimentation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="enterprise-card">
        <h3 style="color: #29B5E8;">🚀 GPU Acceleration</h3>
        <p><strong>What it means:</strong> Access to GPU instances for compute-intensive workloads.</p>
        <p><strong>Why it matters:</strong> Dramatically faster ML model training (10-100x speedup). 
        Enables deep learning, computer vision, and LLM fine-tuning.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="enterprise-card">
        <h3 style="color: #29B5E8;">💰 Potential Cost Savings</h3>
        <p><strong>What it means:</strong> More efficient resource utilization with auto-suspend 
        and right-sizing.</p>
        <p><strong>Why it matters:</strong> Pay only for what you use. Better cost control with 
        per-node pricing and flexible scaling.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Migration urgency guide
st.markdown("## Should You Migrate Now?")

st.markdown("""
Use this decision guide to determine your migration priority:
""")

# Interactive decision guide
workload_type = st.selectbox(
    "What type of workload do you primarily run?",
    [
        "Select...",
        "Interactive data exploration and SQL queries",
        "Machine learning model training (CPU-based)",
        "Deep learning with GPU requirements",
        "Long-running batch processing",
        "Mixed workloads"
    ]
)

if workload_type != "Select...":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if workload_type == "Deep learning with GPU requirements":
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Migration Priority</div>
                <div class="metric-value">🔴 HIGH</div>
            </div>
            """, unsafe_allow_html=True)
        elif workload_type in ["Machine learning model training (CPU-based)", "Long-running batch processing"]:
            st.markdown("""
            <div class="metric-card" style="background: linear-gradient(135deg, #FFA500 0%, #FF8C00 100%);">
                <div class="metric-label">Migration Priority</div>
                <div class="metric-value">🟠 MEDIUM</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card" style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);">
                <div class="metric-label">Migration Priority</div>
                <div class="metric-value">🟢 STANDARD</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        recommendations = {
            "Interactive data exploration and SQL queries": """
                <strong>Recommendation:</strong> Plan migration within normal upgrade cycle.
                <br><br>
                <strong>Why:</strong> Warehouses work well for SQL queries, but compute pools offer better 
                session persistence and cost control. Migrate before deprecation deadline.
                <br><br>
                <strong>Action:</strong> Use the Migration Calculator to size appropriately and compare costs.
            """,
            "Machine learning model training (CPU-based)": """
                <strong>Recommendation:</strong> Migrate soon to take advantage of persistent environments.
                <br><br>
                <strong>Why:</strong> CPU-based ML benefits significantly from persistent package installations 
                and extended sessions. Cost savings from better resource allocation.
                <br><br>
                <strong>Action:</strong> Start with a pilot migration of one ML workload, then expand.
            """,
            "Deep learning with GPU requirements": """
                <strong>Recommendation:</strong> Migrate immediately - this workload cannot run on warehouses.
                <br><br>
                <strong>Why:</strong> Warehouses don't support GPUs. Compute pools are the only option for 
                GPU-accelerated workloads. 10-100x speedup for deep learning.
                <br><br>
                <strong>Action:</strong> Use Migration Calculator with GPU option enabled to get started today.
            """,
            "Long-running batch processing": """
                <strong>Recommendation:</strong> Migrate soon for extended session support.
                <br><br>
                <strong>Why:</strong> Warehouse timeouts can interrupt long-running jobs. Compute pools 
                support extended sessions and better handle batch workloads.
                <br><br>
                <strong>Action:</strong> Test migration with longest-running job first to validate reliability.
            """,
            "Mixed workloads": """
                <strong>Recommendation:</strong> Plan phased migration starting with most complex workloads.
                <br><br>
                <strong>Why:</strong> Different workloads benefit differently from compute pools. Prioritize 
                ML/GPU workloads first, then migrate remaining notebooks.
                <br><br>
                <strong>Action:</strong> Categorize your notebooks and create a migration roadmap.
            """
        }
        
        create_info_box(recommendations[workload_type])

st.markdown("---")

# Architecture overview
st.markdown("## Architecture Overview")

st.markdown("""
Compute pool-backed notebooks run in dedicated container environments managed by Snowflake:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Warehouse-Backed (Legacy)")
    st.markdown("""
    ```
    [Snowflake Notebook]
           |
           v
    [Warehouse: XL]
           |
           v
    [Shared Compute Resources]
           |
           v
    [SQL Engine + Python Runtime]
    ```
    
    **Limitations:**
    - Ephemeral Python environment
    - No GPU support
    - Resource contention
    - Limited session duration
    """)

with col2:
    st.markdown("### Compute Pool-Backed (Current)")
    st.markdown("""
    ```
    [Snowflake Notebook]
           |
           v
    [Compute Pool]
           |
           v
    [Container Node 1] [Container Node 2]
           |                    |
           v                    v
    [Persistent Runtime] [Persistent Runtime]
    [Custom Packages]    [Custom Packages]
    [Optional GPU]       [Optional GPU]
    ```
    
    **Advantages:**
    - Persistent containers
    - GPU support
    - Dedicated resources
    - Extended sessions
    """)

st.markdown("---")

# PDF export section
st.markdown("## Export This Guide")

if st.button("💾 Generate PDF Version"):
    pdf_content = f"""
    <h2>Why Migrate to Compute Pools?</h2>
    
    <div class="warning-box">
        <strong>Deprecation Notice:</strong> Warehouse-backed notebooks will be deprecated. 
        All customers must migrate to compute pool-backed notebooks.
    </div>
    
    <h3>Key Differences</h3>
    {df_comparison.to_html(index=False, border=0)}
    
    <h3>Primary Benefits</h3>
    <ul>
        <li><strong>Persistent Environments:</strong> Packages and state preserved between sessions</li>
        <li><strong>Extended Sessions:</strong> Long-running workloads without interruption</li>
        <li><strong>GPU Support:</strong> Hardware acceleration for ML workloads</li>
        <li><strong>Better Resource Allocation:</strong> Dedicated containers with predictable performance</li>
        <li><strong>Flexible Configuration:</strong> Choose optimal instance types (CPU/GPU/high-memory)</li>
        <li><strong>Cost Efficiency:</strong> Right-sized resources with auto-suspend</li>
    </ul>
    
    <h3>Migration Priority Guidelines</h3>
    <table>
        <tr>
            <th>Workload Type</th>
            <th>Priority</th>
            <th>Reasoning</th>
        </tr>
        <tr>
            <td>Deep Learning (GPU)</td>
            <td>HIGH</td>
            <td>Requires GPU support - must use compute pools</td>
        </tr>
        <tr>
            <td>ML Training (CPU)</td>
            <td>MEDIUM</td>
            <td>Benefits from persistent environments and extended sessions</td>
        </tr>
        <tr>
            <td>Long-Running Batch</td>
            <td>MEDIUM</td>
            <td>Needs extended session duration</td>
        </tr>
        <tr>
            <td>Interactive SQL</td>
            <td>STANDARD</td>
            <td>Works on both, migrate before deadline</td>
        </tr>
    </table>
    
    <h3>Next Steps</h3>
    <ol>
        <li>Use the <strong>Migration Calculator</strong> to get compute pool recommendations</li>
        <li>Review <strong>Cost Monitoring</strong> SQL templates for budget setup</li>
        <li>Check <strong>Best Practices</strong> for optimization strategies</li>
        <li>Follow the <strong>Getting Started</strong> guide for step-by-step migration</li>
    </ol>
    """
    
    create_pdf_download_button(
        pdf_content,
        title="Why Migrate to Compute Pools?",
        filename="snowflake_compute_pools_overview.pdf",
        button_text="Download PDF"
    )

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Back to Home"):
        st.switch_page("main.py")

with col3:
    if st.button("Next: Migration Calculator ➡️"):
        st.switch_page("pages/2_Migration_Calculator.py")
