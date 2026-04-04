from typing import Dict, Any

def get_task_config(task_id: int) -> Dict[str, Any]:
    """
    Returns the initial configuration for the 3 distinct tasks.
    Task 1: Basic Flow Optimization - even traffic, calm conditions.
    Task 2: Rush Hour Imbalance - heavy N/S traffic, light E/W traffic.
    Task 3: Emergency + Chaos - random traffic spikes and emergency vehicles spawn.
    """
    if task_id == 1:
        return {
            "seed": 101,
            "inflow_rates": {"N": 0.2, "S": 0.2, "E": 0.2, "W": 0.2},
            "chaotic": False,
            "max_steps": 1000
        }
    elif task_id == 2:
        return {
            "seed": 202,
            "inflow_rates": {"N": 0.6, "S": 0.1, "E": 0.1, "W": 0.6}, # Imbalanced heavy traffic
            "chaotic": False,
            "max_steps": 1000
        }
    elif task_id == 3:
        return {
            "seed": 303,
            "inflow_rates": {"N": 0.3, "S": 0.3, "E": 0.3, "W": 0.3},
            "chaotic": True, # Enables spikes and emergency spawns
            "max_steps": 1000
        }
    else:
        raise ValueError(f"Unknown task ID: {task_id}")
