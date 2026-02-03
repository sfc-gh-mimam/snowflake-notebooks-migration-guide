"""Core logic for mapping warehouses to compute pools."""

import json
import os
from typing import Dict, List, Optional


def load_warehouse_specs() -> List[Dict]:
    """Load warehouse specifications from JSON."""
    path = os.path.join(os.path.dirname(__file__), "../data/warehouse_specs.json")
    with open(path, "r") as f:
        data = json.load(f)
    return data["warehouses"]


def load_compute_pool_specs() -> List[Dict]:
    """Load compute pool specifications from JSON."""
    path = os.path.join(os.path.dirname(__file__), "../data/compute_pool_specs.json")
    with open(path, "r") as f:
        data = json.load(f)
    return data["instance_families"]


def get_warehouse_by_code(code: str) -> Optional[Dict]:
    """Get warehouse configuration by size code."""
    warehouses = load_warehouse_specs()
    for wh in warehouses:
        if wh["code"] == code:
            return wh
    return None


def recommend_compute_pool(
    warehouse_size: str,
    workload_type: str,
    concurrent_users: int,
    gpu_required: bool = False
) -> Dict:
    """
    Recommend a compute pool configuration based on warehouse characteristics.

    Args:
        warehouse_size: Warehouse size code (XS, S, M, L, XL, 2XL, 3XL, 4XL, 5XL, 6XL)
        workload_type: Type of workload (SQL-heavy, ML-heavy, Balanced, Interactive)
        concurrent_users: Expected number of concurrent users
        gpu_required: Whether GPU is needed

    Returns:
        Dictionary with recommendation details
    """
    warehouse = get_warehouse_by_code(warehouse_size)
    if not warehouse:
        raise ValueError(f"Unknown warehouse size: {warehouse_size}")

    compute_pools = load_compute_pool_specs()

    # Apply workload multipliers to memory/CPU requirements
    workload_multipliers = {
        "SQL-heavy": 0.8,  # Notebooks use less than pure SQL
        "ML-heavy": 1.5,   # ML needs more resources
        "Balanced": 1.0,
        "Interactive": 0.9  # Interactive sessions can be lighter
    }

    multiplier = workload_multipliers.get(workload_type, 1.0)
    target_memory = warehouse["memory_gb"] * multiplier
    target_vcpu = warehouse["vcpu"] * multiplier

    # Filter by GPU requirement
    if gpu_required:
        candidates = [p for p in compute_pools if p["type"] == "GPU"]
    else:
        candidates = [p for p in compute_pools if p["type"] == "CPU"]

    # Find best match based on memory and vCPU
    best_match = None
    min_diff = float('inf')

    for pool in candidates:
        memory_diff = abs(pool["memory_gb"] - target_memory)
        vcpu_diff = abs(pool["vcpu"] - target_vcpu)
        total_diff = memory_diff + (vcpu_diff * 2)  # Weight vCPU more

        if total_diff < min_diff:
            min_diff = total_diff
            best_match = pool

    # Calculate recommended node count
    # Heuristic: 2 users per node for interactive workloads
    min_nodes = max(1, (concurrent_users + 1) // 2)
    max_nodes = max(min_nodes, concurrent_users)

    # Auto-suspend recommendation based on workload
    auto_suspend_minutes = {
        "SQL-heavy": 10,
        "ML-heavy": 30,
        "Balanced": 15,
        "Interactive": 5
    }.get(workload_type, 15)

    return {
        "instance_family": best_match["family"],
        "instance_type": best_match["type"],
        "memory_gb": best_match["memory_gb"],
        "vcpu": best_match["vcpu"],
        "credits_per_hour": best_match["credits_per_hour"],
        "description": best_match["description"],
        "recommended_min_nodes": min_nodes,
        "recommended_max_nodes": max_nodes,
        "auto_suspend_minutes": auto_suspend_minutes,
        "gpu_details": {
            "gpu_memory_gb": best_match.get("gpu_memory_gb"),
            "gpu_count": best_match.get("gpu_count")
        } if gpu_required else None,
        "workload_multiplier": multiplier,
        "original_warehouse": warehouse
    }


def get_migration_sql(recommendation: Dict, pool_name: str = "NOTEBOOK_POOL") -> str:
    """Generate SQL to create the recommended compute pool."""

    sql_parts = [
        f"-- Create compute pool for notebook workloads",
        f"CREATE COMPUTE POOL {pool_name}",
        f"  MIN_NODES = {recommendation['recommended_min_nodes']}",
        f"  MAX_NODES = {recommendation['recommended_max_nodes']}",
        f"  INSTANCE_FAMILY = {recommendation['instance_family']}",
        f"  AUTO_RESUME = TRUE",
        f"  AUTO_SUSPEND_SECS = {recommendation['auto_suspend_minutes'] * 60}",
        f"  COMMENT = 'Compute pool for migrated notebook workloads';",
        "",
        f"-- Grant usage to appropriate roles",
        f"GRANT USAGE ON COMPUTE POOL {pool_name} TO ROLE <YOUR_ROLE>;",
        f"GRANT OPERATE ON COMPUTE POOL {pool_name} TO ROLE <YOUR_ROLE>;",
    ]

    return "\n".join(sql_parts)
