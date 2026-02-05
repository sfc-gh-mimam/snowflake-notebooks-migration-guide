"""Cost calculation and comparison logic."""

from typing import Dict, List


def calculate_monthly_cost(
    credits_per_hour: float,
    hours_per_day: float,
    days_per_month: int = 22,
    credit_rate: float = 4.0
) -> float:
    """
    Calculate monthly cost in dollars.

    Args:
        credits_per_hour: Credits consumed per hour
        hours_per_day: Average hours of usage per day
        days_per_month: Working days per month (default: 22)
        credit_rate: Cost per credit in dollars (default: $4)

    Returns:
        Monthly cost in dollars
    """
    total_hours = hours_per_day * days_per_month
    total_credits = credits_per_hour * total_hours
    return total_credits * credit_rate


def calculate_warehouse_cost(
    warehouse: Dict,
    hours_per_day: float,
    days_per_month: int = 22,
    credit_rate: float = 4.0
) -> Dict:
    """Calculate warehouse monthly costs."""
    monthly_cost = calculate_monthly_cost(
        warehouse["credits_per_hour"],
        hours_per_day,
        days_per_month,
        credit_rate
    )

    return {
        "monthly_cost": monthly_cost,
        "credits_per_hour": warehouse["credits_per_hour"],
        "total_hours": hours_per_day * days_per_month,
        "total_credits": warehouse["credits_per_hour"] * hours_per_day * days_per_month
    }


def calculate_compute_pool_cost(
    recommendation: Dict,
    hours_per_day: float,
    days_per_month: int = 22,
    credit_rate: float = 4.0,
    avg_node_count: int = None
) -> Dict:
    """Calculate compute pool monthly costs."""
    if avg_node_count is None:
        # Use average of min and max recommended nodes
        avg_node_count = (
            recommendation["recommended_min_nodes"] +
            recommendation["recommended_max_nodes"]
        ) // 2

    credits_per_hour = recommendation["credits_per_hour"] * avg_node_count
    monthly_cost = calculate_monthly_cost(
        credits_per_hour,
        hours_per_day,
        days_per_month,
        credit_rate
    )

    return {
        "monthly_cost": monthly_cost,
        "credits_per_hour": credits_per_hour,
        "credits_per_hour_per_node": recommendation["credits_per_hour"],
        "avg_node_count": avg_node_count,
        "total_hours": hours_per_day * days_per_month,
        "total_credits": credits_per_hour * hours_per_day * days_per_month
    }


def compare_costs(
    warehouse: Dict,
    recommendation: Dict,
    hours_per_day: float,
    days_per_month: int = 22,
    credit_rate: float = 4.0,
    avg_node_count: int = None
) -> Dict:
    """
    Compare warehouse vs compute pool costs.

    Args:
        warehouse: Warehouse specification
        recommendation: Compute pool recommendation
        hours_per_day: Session hours per day
        days_per_month: Working days per month
        credit_rate: Cost per credit
        avg_node_count: Average nodes for compute pool

    Returns:
        Dictionary with cost comparison details
    """
    warehouse_cost = calculate_warehouse_cost(
        warehouse, hours_per_day, days_per_month, credit_rate
    )

    pool_cost = calculate_compute_pool_cost(
        recommendation, hours_per_day, days_per_month, credit_rate, avg_node_count
    )

    savings = warehouse_cost["monthly_cost"] - pool_cost["monthly_cost"]
    savings_percent = (savings / warehouse_cost["monthly_cost"] * 100) if warehouse_cost["monthly_cost"] > 0 else 0

    return {
        "warehouse_cost": warehouse_cost,
        "compute_pool_cost": pool_cost,
        "monthly_savings": savings,
        "savings_percent": savings_percent,
        "recommendation": "Compute Pool" if savings > 0 else "Warehouse",
        "parameters": {
            "hours_per_day": hours_per_day,
            "days_per_month": days_per_month,
            "credit_rate": credit_rate,
            "avg_node_count": avg_node_count or recommendation.get("recommended_min_nodes", 1)
        }
    }


def estimate_annual_savings(monthly_savings: float, months: int = 12) -> float:
    """Calculate annual savings projection."""
    return monthly_savings * months
