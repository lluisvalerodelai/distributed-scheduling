"""
Simple test/example for the distributed scheduling environment.
"""

from random import shuffle
import numpy as np
from env import (
    Env,
    encode_task,
    decode_task,
    encode_node,
    TASK_MATMUL,
    TASK_PRIMES,
    TASK_ARRAY,
    TASK_FILEIO,
    NO_OP_TASK,
    NUM_NODES,
)

from log_utils import (
    pretty_print_state,
    pretty_print_requesting_nodes,
    pretty_print_reward,
    pretty_print_info,
)


def dummy_duration_fn(task_vector, node_id):
    # In reality, this would use regression model from benchmarks.
    task_type, parameter = decode_task(task_vector)

    if task_type == -1:  # No-op
        return 0.0

    # Simple dummy model: duration increases with parameter
    # Different nodes have different speed multipliers
    node_speed = 1.0 + (node_id * 0.1)  # Slower nodes have higher multipliers

    if task_type == TASK_MATMUL:
        base_time = (parameter / 1000) ** 2.5
    elif task_type == TASK_PRIMES:
        base_time = (parameter / 1000000) * 2.0
    elif task_type == TASK_ARRAY:
        base_time = (parameter / 1000000) * 1.5
    elif task_type == TASK_FILEIO:
        base_time = (parameter / 100000) * 0.8
    else:
        base_time = 1.0

    return base_time * node_speed


task_queue = [
    (TASK_MATMUL, 0.5),
    (TASK_FILEIO, 0.5),
    (TASK_MATMUL, 0.5),
    (TASK_MATMUL, 0.5),
    (TASK_MATMUL, 0.5),
    (TASK_ARRAY, 0.5),
    (TASK_ARRAY, 0.5),
    (TASK_MATMUL, 0.5),
    (TASK_PRIMES, 0.5),
    (TASK_PRIMES, 0.5),
    (TASK_MATMUL, 0.5),
    (TASK_PRIMES, 0.5),
    (TASK_FILEIO, 0.5),
    (TASK_ARRAY, 0.5),
    (TASK_FILEIO, 0.5),
    (TASK_FILEIO, 0.5),
]

shuffle(task_queue)


env = Env(dummy_duration_fn, task_queue)

state, requesting_nodes = env.reset()
print("state", state)
print("requesting node", requesting_nodes)

task_assignments = []

for node_id in requesting_nodes:
    task = task_queue.pop()
    task_assignments.append((node_id, task))


next_state, requesting_nodes, reward, info = env.step(task_assignments)
print(pretty_print_state(next_state))
print(next_state)
print(pretty_print_requesting_nodes(requesting_nodes))
print(pretty_print_reward(reward))
print(pretty_print_info(info))
