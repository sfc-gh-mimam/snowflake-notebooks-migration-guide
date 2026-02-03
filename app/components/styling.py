"""Styling utilities for enterprise appearance."""

import streamlit as st


def inject_custom_css():
    """Inject custom CSS for enterprise styling."""
    st.markdown("""
        <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        /* Card styling */
        .enterprise-card {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .enterprise-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: box-shadow 0.3s ease;
        }

        /* Header styling */
        .enterprise-header {
            color: #29B5E8;
            font-weight: 600;
            margin-bottom: 1rem;
            border-bottom: 2px solid #29B5E8;
            padding-bottom: 0.5rem;
        }

        /* Button customization */
        .stButton>button {
            border-radius: 6px;
            font-weight: 500;
            border: 1px solid #29B5E8;
            background-color: #29B5E8;
            color: white;
        }

        .stButton>button:hover {
            background-color: #1a8fc9;
            border-color: #1a8fc9;
        }

        /* Info box styling */
        .info-box {
            background-color: #F0F8FF;
            border-left: 4px solid #29B5E8;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }

        .warning-box {
            background-color: #FFF4E6;
            border-left: 4px solid #FFA500;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }

        /* Metric card styling */
        .metric-card {
            background: linear-gradient(135deg, #29B5E8 0%, #1a8fc9 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 1rem;
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }

        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Table styling */
        .dataframe {
            border: none !important;
        }

        .dataframe th {
            background-color: #29B5E8 !important;
            color: white !important;
            font-weight: 600 !important;
            text-align: left !important;
        }

        .dataframe td {
            text-align: left !important;
        }

        /* Code block styling */
        code {
            background-color: #F5F5F5;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }

        pre {
            background-color: #F5F5F5;
            padding: 1rem;
            border-radius: 6px;
            border-left: 3px solid #29B5E8;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: #F8F9FA;
        }

        /* Navigation */
        .nav-card {
            background-color: white;
            border: 2px solid #E0E0E0;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            cursor: pointer;
            text-decoration: none;
            display: block;
            transition: all 0.3s ease;
        }

        .nav-card:hover {
            border-color: #29B5E8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(41, 181, 232, 0.2);
        }

        .nav-title {
            color: #29B5E8;
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .nav-description {
            color: #666;
            font-size: 0.9rem;
        }

        /* Disclaimer styling */
        .disclaimer {
            background-color: #FFF9E6;
            border: 1px solid #FFD700;
            border-radius: 6px;
            padding: 1rem;
            margin: 1.5rem 0;
            font-size: 0.85rem;
            color: #666;
        }

        /* Success/Error messages */
        .success-message {
            background-color: #E8F5E9;
            border-left: 4px solid #4CAF50;
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }

        .error-message {
            background-color: #FFEBEE;
            border-left: 4px solid #F44336;
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)


def create_card(content: str, card_class: str = "enterprise-card"):
    """Create a styled card with content."""
    st.markdown(f'<div class="{card_class}">{content}</div>', unsafe_allow_html=True)


def create_header(text: str, level: int = 1):
    """Create a styled header."""
    tag = f"h{level}"
    st.markdown(f'<{tag} class="enterprise-header">{text}</{tag}>', unsafe_allow_html=True)


def create_info_box(content: str):
    """Create an info box."""
    st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)


def create_warning_box(content: str):
    """Create a warning box."""
    st.markdown(f'<div class="warning-box">{content}</div>', unsafe_allow_html=True)


def create_disclaimer():
    """Create a standard disclaimer box."""
    st.markdown("""
        <div class="disclaimer">
            <strong>⚠️ Pricing Disclaimer:</strong> The cost estimates shown are based on 
            placeholder credit rates and may not reflect your actual Snowflake pricing. 
            Please consult with your Snowflake account team for accurate pricing specific 
            to your contract and region.
        </div>
    """, unsafe_allow_html=True)


def create_metric_card(value: str, label: str):
    """Create a metric display card."""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)
