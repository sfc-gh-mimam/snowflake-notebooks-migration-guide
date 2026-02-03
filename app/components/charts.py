"""Chart generation utilities using Plotly."""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List


def create_cost_comparison_chart(comparison: Dict) -> go.Figure:
    """Create a cost comparison bar chart."""
    warehouse_cost = comparison["warehouse_cost"]["monthly_cost"]
    pool_cost = comparison["compute_pool_cost"]["monthly_cost"]

    fig = go.Figure(data=[
        go.Bar(
            name="Current (Warehouse)",
            x=["Monthly Cost"],
            y=[warehouse_cost],
            marker_color="#FF6B6B",
            text=[f"${warehouse_cost:,.2f}"],
            textposition="auto",
        ),
        go.Bar(
            name="Proposed (Compute Pool)",
            x=["Monthly Cost"],
            y=[pool_cost],
            marker_color="#29B5E8",
            text=[f"${pool_cost:,.2f}"],
            textposition="auto",
        )
    ])

    fig.update_layout(
        title="Monthly Cost Comparison",
        yaxis_title="Cost (USD)",
        barmode="group",
        showlegend=True,
        height=400,
        template="plotly_white",
        font=dict(family="sans-serif", size=12)
    )

    return fig


def create_savings_chart(comparison: Dict) -> go.Figure:
    """Create a savings visualization."""
    savings = comparison["monthly_savings"]
    savings_percent = comparison["savings_percent"]

    color = "#4CAF50" if savings > 0 else "#F44336"
    label = "Savings" if savings > 0 else "Additional Cost"

    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=abs(savings),
        title={"text": f"Monthly {label}"},
        delta={"reference": 0, "valueformat": ".2f"},
        number={"prefix": "$", "valueformat": ",.2f"},
        domain={"x": [0, 1], "y": [0, 1]}
    ))

    fig.update_layout(
        height=300,
        template="plotly_white"
    )

    return fig


def create_resource_comparison(warehouse: Dict, pool_config: Dict) -> go.Figure:
    """Create a resource comparison chart."""
    categories = ["Memory (GB)", "vCPU"]
    warehouse_vals = [warehouse["memory_gb"], warehouse["vcpu"]]
    pool_vals = [pool_config["memory_gb"], pool_config["vcpu"]]

    fig = go.Figure(data=[
        go.Bar(
            name="Warehouse",
            x=categories,
            y=warehouse_vals,
            marker_color="#FF6B6B"
        ),
        go.Bar(
            name="Compute Pool (per node)",
            x=categories,
            y=pool_vals,
            marker_color="#29B5E8"
        )
    ])

    fig.update_layout(
        title="Resource Comparison",
        yaxis_title="Amount",
        barmode="group",
        height=400,
        template="plotly_white"
    )

    return fig


def create_credit_usage_timeline(data: List[Dict]) -> go.Figure:
    """Create a timeline chart for credit usage."""
    if not data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

    fig = go.Figure(data=[
        go.Scatter(
            x=[d["date"] for d in data],
            y=[d["credits"] for d in data],
            mode="lines+markers",
            line=dict(color="#29B5E8", width=2),
            marker=dict(size=8),
            fill="tozeroy",
            fillcolor="rgba(41, 181, 232, 0.2)"
        )
    ])

    fig.update_layout(
        title="Daily Credit Consumption",
        xaxis_title="Date",
        yaxis_title="Credits",
        height=400,
        template="plotly_white",
        hovermode="x unified"
    )

    return fig


def create_workload_distribution_pie(workloads: Dict[str, float]) -> go.Figure:
    """Create a pie chart for workload distribution."""
    fig = go.Figure(data=[
        go.Pie(
            labels=list(workloads.keys()),
            values=list(workloads.values()),
            hole=0.3,
            marker=dict(
                colors=["#29B5E8", "#4CAF50", "#FFA500", "#9C27B0"]
            )
        )
    ])

    fig.update_layout(
        title="Workload Distribution",
        height=400,
        template="plotly_white"
    )

    return fig
