from env import (
    Env,
    decode_task,
    TASK_MATMUL,
    TASK_PRIMES,
    TASK_ARRAY,
    TASK_FILEIO,
    NO_OP_TASK,
    NUM_NODES,
)
import numpy as np


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


def encode_state(state: np.ndarray) -> np.ndarray:
    # Transform the raw state from env into one-hot encoded format for neural network.
    #
    # The environment returns state as: [task_type_0, time_remaining_0, task_type_1, time_remaining_1, ...]
    # where task_type is an integer index (TASK_IDLE=-1, TASK_MATMUL=0, etc.)
    #
    # But it needs to be for each node: [one_hot_task (4 values), time_remaining (1 value)]

    num_nodes = len(state) // 2
    encoded_state = np.zeros(num_nodes * 5)

    for i in range(num_nodes):
        task_type = int(state[i * 2])
        time_remaining = state[i * 2 + 1]

        # One-hot encode the task type
        # TASK_IDLE (-1) -> [0, 0, 0, 0] (all zeros)
        # TASK_MATMUL (0) -> [1, 0, 0, 0]
        # TASK_PRIMES (1) -> [0, 1, 0, 0]
        # TASK_ARRAY (2) -> [0, 0, 1, 0]
        # TASK_FILEIO (3) -> [0, 0, 0, 1]

        if task_type >= 0:  # Not TASK_IDLE
            encoded_state[i * 5 + task_type] = 1.0

        # Add time remaining as the 5th value for this node
        encoded_state[i * 5 + 4] = time_remaining

    return encoded_state


task_queue = [
    (TASK_MATMUL, 0.1),
    (TASK_MATMUL, 0.2),
    (TASK_MATMUL, 0.4),
    (TASK_MATMUL, 0.5),
    (TASK_MATMUL, 0.8),
    (TASK_MATMUL, 0.9),
    #
    (TASK_PRIMES, 0.05),
    (TASK_PRIMES, 0.2),
    (TASK_PRIMES, 0.3),
    (TASK_PRIMES, 0.5),
    (TASK_PRIMES, 0.7),
    (TASK_PRIMES, 0.8),
    (TASK_PRIMES, 0.9),
    (TASK_PRIMES, 0.95),
    #
    (TASK_ARRAY, 0.1),
    (TASK_ARRAY, 0.2),
    (TASK_ARRAY, 0.3),
    (TASK_ARRAY, 0.5),
    (TASK_ARRAY, 0.7),
    (TASK_ARRAY, 0.8),
    (TASK_ARRAY, 0.85),
    (TASK_ARRAY, 0.9),
    (TASK_ARRAY, 0.95),
    #
    (TASK_FILEIO, 0.1),
    (TASK_FILEIO, 0.2),
    (TASK_FILEIO, 0.3),
    (TASK_FILEIO, 0.4),
    (TASK_FILEIO, 0.5),
    (TASK_FILEIO, 0.6),
    (TASK_FILEIO, 0.7),
    (TASK_FILEIO, 0.8),
    (TASK_FILEIO, 0.9),
    (TASK_FILEIO, 1.0),
]
