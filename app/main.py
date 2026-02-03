"""Main landing page for Snowflake Notebooks Migration Guide."""

import streamlit as st
import sys
import os

# Add app directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components import inject_custom_css, create_info_box, create_warning_box

# Page configuration
st.set_page_config(
    page_title="Snowflake Notebooks Migration Guide",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
inject_custom_css()

# Hero section
st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #29B5E8 0%, #1a8fc9 100%); color: white; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="margin: 0; font-size: 3rem; color: white;">❄️ Snowflake Notebooks Migration Guide</h1>
        <p style="font-size: 1.3rem; margin-top: 1rem; color: white;">Migrate from Warehouse-Backed to Compute Pool-Backed Notebooks</p>
    </div>
""", unsafe_allow_html=True)

# Deprecation notice
create_warning_box("""
    <strong>⚠️ Important Notice:</strong> Warehouse-backed Snowflake Notebooks are being deprecated. 
    All notebook workloads must migrate to compute pool-backed notebooks. This tool helps you plan 
    and execute your migration with cost optimization and best practices.
""")

# Overview section
st.markdown("## What This Tool Does")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="enterprise-card" style="min-height: 200px;">
        <h3 style="color: #29B5E8;">📊 Calculate Migration</h3>
        <p>Get recommendations for compute pool configurations based on your current warehouse setup, 
        workload type, and usage patterns.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="enterprise-card" style="min-height: 200px;">
        <h3 style="color: #29B5E8;">💰 Compare Costs</h3>
        <p>Understand the cost implications of migrating to compute pools with side-by-side 
        comparisons and savings projections.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="enterprise-card" style="min-height: 200px;">
        <h3 style="color: #29B5E8;">🔍 Monitor Usage</h3>
        <p>Access SQL templates and best practices for tracking credit consumption, 
        setting budgets, and optimizing costs.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Navigation cards
st.markdown("## Get Started")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-title">1️⃣ Why Compute Pools?</div>
        <div class="nav-description">
            Understand the benefits and differences between warehouse-backed and 
            compute pool-backed notebooks. Learn why migration is necessary and 
            what advantages you'll gain.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="nav-card">
        <div class="nav-title">2️⃣ Migration Calculator</div>
        <div class="nav-description">
            <strong>PRIMARY TOOL:</strong> Input your warehouse size, workload type, 
            and user count to get instant compute pool recommendations with cost 
            comparisons and configuration SQL.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="nav-card">
        <div class="nav-title">3️⃣ Cost Monitoring</div>
        <div class="nav-description">
            <strong>SQL LIBRARY:</strong> Access ready-to-use SQL queries for tracking 
            credit consumption, user attribution, idle pool detection, and budget management.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-title">4️⃣ Best Practices</div>
        <div class="nav-description">
            Learn optimization strategies, right-sizing guidance, idle timeout 
            recommendations, and configuration templates for different workload types.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="nav-card">
        <div class="nav-title">5️⃣ Getting Started</div>
        <div class="nav-description">
            Step-by-step setup wizard with prerequisite checklist, permission grants, 
            pool creation SQL, and validation tests to ensure successful migration.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Quick links
st.markdown("## Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧮 Open Migration Calculator", use_container_width=True):
        st.switch_page("pages/2_Migration_Calculator.py")

with col2:
    if st.button("📋 View SQL Templates", use_container_width=True):
        st.switch_page("pages/3_Cost_Monitoring.py")

with col3:
    if st.button("🚀 Setup Guide", use_container_width=True):
        st.switch_page("pages/5_Getting_Started.py")

st.markdown("---")

# Information box
create_info_box("""
    <strong>💡 Pro Tip:</strong> Start with the <strong>Migration Calculator</strong> to get 
    personalized recommendations, then use the <strong>Cost Monitoring</strong> page to set up 
    tracking before you migrate. Don't forget to review <strong>Best Practices</strong> for 
    optimization strategies.
""")

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #E0E0E0; color: #666;">
        <p><strong>Snowflake Notebooks Migration Tool</strong></p>
        <p style="font-size: 0.9rem;">For questions or support, contact your Snowflake account team</p>
        <p style="font-size: 0.85rem; margin-top: 1rem;">This tool provides planning guidance and cost estimates based on placeholder data. 
        Always validate with your Snowflake account team.</p>
    </div>
""", unsafe_allow_html=True)
