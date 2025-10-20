"""
Test file with scheduling heuristics for comparison with RL agent.
Uses dummy_duration_fn to make intelligent task assignments.
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


def greedy_scheduler(requesting_nodes, task_queue, state, duration_fn):
    """
    Greedy scheduling heuristic: for each requesting node, assign the task
    that will complete fastest on that node.

    This implements a "Shortest Processing Time" heuristic per node.
    """
    if not task_queue or not requesting_nodes:
        return []

    task_assignments = []
    available_tasks = task_queue.copy()

    for node_id in requesting_nodes:
        if not available_tasks:
            break

        # Find the task that will complete fastest on this node
        best_task = None
        best_duration = float('inf')
        best_idx = -1

        for idx, (task_type, param) in enumerate(available_tasks):
            task_vector = encode_task(task_type, param)
            duration = duration_fn(task_vector, node_id)

            if duration < best_duration:
                best_duration = duration
                best_task = (task_type, param)
                best_idx = idx

        if best_task is not None:
            task_assignments.append((node_id, best_task))
            available_tasks.pop(best_idx)

    # Remove assigned tasks from the original queue
    for _, task in task_assignments:
        task_queue.remove(task)

    return task_assignments


def shortest_job_first_scheduler(requesting_nodes, task_queue, state, duration_fn):
    """
    Shortest Job First (SJF): assign shortest duration tasks first.
    Uses the average duration across all nodes to estimate task length.
    """
    if not task_queue or not requesting_nodes:
        return []

    # Calculate average duration for each task
    task_durations = []
    for task_type, param in task_queue:
        task_vector = encode_task(task_type, param)
        avg_duration = np.mean(
            [duration_fn(task_vector, node_id) for node_id in range(NUM_NODES)]
        )
        task_durations.append((avg_duration, task_type, param))

    # Sort tasks by duration (shortest first)
    task_durations.sort(key=lambda x: x[0])

    task_assignments = []
    assigned_count = 0

    for node_id in requesting_nodes:
        if assigned_count >= len(task_durations):
            break

        _, task_type, param = task_durations[assigned_count]
        task_assignments.append((node_id, (task_type, param)))
        assigned_count += 1

    # Remove assigned tasks from queue
    for _, task in task_assignments:
        task_queue.remove(task)

    return task_assignments


def optimal_matching_scheduler(requesting_nodes, task_queue, state, duration_fn):
    """
    Optimal matching heuristic: finds the assignment that minimizes
    total completion time using a greedy approach.

    For each task-node pair, compute duration, then greedily assign
    the minimum duration pairs.
    """
    if not task_queue or not requesting_nodes:
        return []

    # Compute all task-node durations
    candidates = []
    for node_id in requesting_nodes:
        for task_idx, (task_type, param) in enumerate(task_queue):
            task_vector = encode_task(task_type, param)
            duration = duration_fn(task_vector, node_id)
            candidates.append((duration, node_id, task_idx, task_type, param))

    # Sort by duration (lowest first)
    candidates.sort(key=lambda x: x[0])

    task_assignments = []
    assigned_nodes = set()
    assigned_tasks = set()

    # Greedily assign task-node pairs
    for duration, node_id, task_idx, task_type, param in candidates:
        if node_id not in assigned_nodes and task_idx not in assigned_tasks:
            task_assignments.append((node_id, (task_type, param)))
            assigned_nodes.add(node_id)
            assigned_tasks.add(task_idx)

        # Stop when all nodes or tasks are assigned
        if len(assigned_nodes) >= len(requesting_nodes) or len(assigned_tasks) >= len(
            task_queue
        ):
            break

    # Remove assigned tasks from queue
    for _, task in task_assignments:
        task_queue.remove(task)

    return task_assignments


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

shuffle(task_queue)

env = Env(dummy_duration_fn, task_queue)

state, requesting_nodes = env.reset()
done = False

# Choose which scheduler to use
SCHEDULER = "sjf"  # Options: "greedy", "sjf", "optimal_matching"

print(f"Using scheduler: {SCHEDULER}")
print("=" * 50)
print(pretty_print_state(state))
print(pretty_print_requesting_nodes(requesting_nodes))

total_reward = 0

while not done:
    # Use the selected scheduling heuristic
    if SCHEDULER == "greedy":
        task_assignments = greedy_scheduler(
            requesting_nodes, task_queue, state, dummy_duration_fn
        )
    elif SCHEDULER == "sjf":
        task_assignments = shortest_job_first_scheduler(
            requesting_nodes, task_queue, state, dummy_duration_fn
        )
    elif SCHEDULER == "optimal_matching":
        task_assignments = optimal_matching_scheduler(
            requesting_nodes, task_queue, state, dummy_duration_fn
        )
    else:
        raise ValueError(f"Unknown scheduler: {SCHEDULER}")

    next_state, requesting_nodes, reward, info = env.step(task_assignments)
    total_reward += reward

    print(pretty_print_state(next_state))
    print(pretty_print_requesting_nodes(requesting_nodes))
    print(pretty_print_reward(reward))
    print(pretty_print_info(info))
    print("-" * 50)

    if info['done'] == True:
        break

print("=" * 50)
print(f"Total reward: {total_reward:.4f}")
print(f"Scheduler used: {SCHEDULER}")
