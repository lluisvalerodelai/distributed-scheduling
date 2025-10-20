"""
Pretty print utilities for the distributed scheduling environment.
"""

import numpy as np
from typing import Dict, List, Optional
from env import (
    decode_task,
    TASK_IDLE,
    TASK_MATMUL,
    TASK_PRIMES,
    TASK_ARRAY,
    TASK_FILEIO,
)

# Task name mappings
TASK_NAMES = {
    TASK_IDLE: "IDLE",
    TASK_MATMUL: "MATMUL",
    TASK_PRIMES: "PRIMES",
    TASK_ARRAY: "ARRAY",
    TASK_FILEIO: "FILEIO",
}


def pretty_print_task(task_vector: np.ndarray) -> str:
    task_type, parameter = decode_task(task_vector)
    task_name = TASK_NAMES.get(task_type, f"UNKNOWN({task_type})")

    if task_type == TASK_IDLE:
        return f"{task_name}"
    return f"{task_name}(param={parameter})"


def pretty_print_state(state: np.ndarray) -> str:
    num_nodes = len(state) // 2
    lines = ["Node Status:"]
    lines.append("─" * 50)

    for i in range(num_nodes):
        task_type = int(state[i * 2])
        time_remaining = state[i * 2 + 1]
        task_name = TASK_NAMES.get(task_type, f"UNKNOWN({task_type})")

        if task_type == TASK_IDLE or time_remaining == 0:
            status = "IDLE"
            lines.append(f"Node {i}: {status}")
        else:
            lines.append(f"Node {i}: {task_name} (remaining: {time_remaining:.2f}s)")

    return "\n".join(lines)


def pretty_print_requesting_nodes(requesting_nodes: Optional[List[int]]) -> str:
    if requesting_nodes is None:
        return "Requesting Nodes: None (all idle, environment done)"

    if not requesting_nodes:
        return "Requesting Nodes: [] (no nodes requesting)"

    node_list = ", ".join(f"Node {node_id}" for node_id in requesting_nodes)
    return f"Requesting Nodes: [{node_list}] ({len(requesting_nodes)} nodes)"


def pretty_print_info(info: Dict) -> str:
    lines = ["Environment Info:"]
    lines.append(f"  Total Time Elapsed: {info.get('total_time', 0):.2f}s")
    lines.append(f"  Tasks Completed: {info.get('tasks_completed', 0)}")
    lines.append(f"  Done: {info.get('done', False)}")
    return "\n".join(lines)


def pretty_print_reward(reward: float) -> str:
    return f"Reward: {reward:.2f}"
