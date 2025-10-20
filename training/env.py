import numpy as np
from typing import Tuple, Optional, Dict, List

# Task type constants
TASK_IDLE = -1
TASK_MATMUL = 0
TASK_PRIMES = 1
TASK_ARRAY = 2
TASK_FILEIO = 3
TASK_ENCODING_SIZE = 5  # 4 for one-hot + 1 for parameter

# Node constants
NUM_NODES = 9

# Task parameter ranges (min, max)
TASK_PARAM_RANGES = {
    TASK_MATMUL: (250, 5000),
    TASK_PRIMES: (240000, 4800000),
    TASK_ARRAY: (500000, 10000000),
    TASK_FILEIO: (100000, 2000000),
}

NO_OP_TASK = np.array([0.0, 0.0, 0.0, 0.0, 0.0])


# Utility functions
def normalize_parameter(task_type: int, parameter: int) -> float:
    # Normalize a task parameter to [0, 1] range.
    if task_type == TASK_IDLE:
        return 0.0

    min_val, max_val = TASK_PARAM_RANGES[task_type]
    normalized = (parameter - min_val) / (max_val - min_val)
    return np.clip(normalized, 0.0, 1.0)


def denormalize_parameter(task_type: int, normalized_parameter: float) -> int:
    # Denormalize a task parameter from [0, 1] range to original range.

    if task_type == TASK_IDLE:
        return 0

    min_val, max_val = TASK_PARAM_RANGES[task_type]
    parameter = normalized_parameter * (max_val - min_val) + min_val
    return int(parameter)


def encode_task(task_type: int, parameter: float, normalize: bool = True) -> np.ndarray:
    # Encode a task as a one-hot vector with parameter.

    task_vector = np.zeros(TASK_ENCODING_SIZE)
    task_vector[4] = parameter

    if task_type >= 0:  # TASK_IDLE means no-op
        task_vector[task_type] = 1.0
        if normalize:
            task_vector[4] = normalize_parameter(task_type, parameter)
        else:
            task_vector[4] = parameter
    return task_vector


def decode_task(task_vector: np.ndarray, denormalize: bool = True) -> Tuple[int, int]:
    # Decode a task vector into task_type and parameter.

    # if its the idle task, it will be all zeros, pm precision errors. hence the allclose
    if np.allclose(task_vector, 0):
        return TASK_IDLE, 0.0

    task_type = np.argmax(task_vector[:4])
    normalized_parameter = task_vector[4]

    if denormalize:
        parameter = denormalize_parameter(task_type, normalized_parameter)
    else:
        parameter = normalized_parameter

    return int(task_type), int(parameter)


def encode_node(node_id: int) -> np.ndarray:
    # Encode a node as a one-hot vector.

    node_vector = np.zeros(NUM_NODES)
    node_vector[node_id] = 1.0
    return node_vector


class NodeCluster:
    # Simulates a cluster of nodes executing tasks.
    #
    # Tracks the current state of all nodes including:
    # - What task each node is running
    # - How much time is left for each task

    def __init__(self, duration_fn):

        self.duration_fn = duration_fn
        self.num_nodes = NUM_NODES

        # For each node: [task_type, parameter, start_time, expected_duration]
        self.node_tasks = np.full((self.num_nodes, 4), TASK_IDLE)
        self.current_time = 0.0

    def duration(self, task_vector: np.ndarray, node_id: int) -> float:
        # Get the expected duration for a task on a specific node.

        return self.duration_fn(task_vector, node_id)

    def assign_task(self, node_id: int, task_vector: np.ndarray):

        task_type, parameter = decode_task(task_vector)

        if task_type == TASK_IDLE:
            self.node_tasks[node_id] = [TASK_IDLE, 0, self.current_time, 0]
        else:
            duration = self.duration(task_vector, node_id)
            self.node_tasks[node_id] = [
                task_type,
                parameter,
                self.current_time,
                duration,
            ]

    def get_time_remaining(self, node_id: int) -> float:
        # Get the time remaining for a node's current task.

        task_type, parameter, start_time, expected_duration = self.node_tasks[node_id]

        if task_type == TASK_IDLE:
            return 0.0

        elapsed = self.current_time - start_time
        # can be the case that expected duration is wrong (not in this sim yet)
        remaining = max(0.0, expected_duration - elapsed)
        return remaining

    def is_idle(self, node_id: int) -> bool:
        return (
            self.node_tasks[node_id, 0] == TASK_IDLE
            or self.get_time_remaining(node_id) == 0
        )

    def get_idle_nodes(self) -> List[int]:
        # Get all nodes that are currently idle.
        return [node_id for node_id in range(self.num_nodes) if self.is_idle(node_id)]

    def get_node_status(self) -> np.ndarray:
        # Get the current status of all nodes.

        status = np.zeros(self.num_nodes * 2)

        for i in range(self.num_nodes):
            task_type = self.node_tasks[i, 0]
            time_remaining = self.get_time_remaining(i)

            status[i * 2] = task_type
            status[i * 2 + 1] = time_remaining

        return status

    def run_time_forward(self) -> Optional[int]:
        # Run time forward until a busy node becomes free.
        # Returns Node ID of the node that just became free, or None if all nodes are idle

        # Find all busy nodes and their completion times
        completion_times = []

        for node_id in range(self.num_nodes):
            if not self.is_idle(node_id):
                time_remaining = self.get_time_remaining(node_id)
                if time_remaining > 0:
                    completion_time = self.current_time + time_remaining
                    completion_times.append((completion_time, node_id))

        if not completion_times:
            # All nodes are idle
            return None

        # Find the earliest completion time
        completion_times.sort()
        next_completion_time, freed_node_id = completion_times[0]

        # Advance time
        self.current_time = next_completion_time

        # Mark the freed node as idle
        self.node_tasks[freed_node_id] = [TASK_IDLE, 0, self.current_time, 0]

        return freed_node_id

    def reset(self):
        # Reset the cluster to initial state (all nodes idle).
        self.node_tasks = np.full((self.num_nodes, 4), TASK_IDLE)
        self.current_time = 0.0


class Env:
    """
    Distributed scheduling environment.

    The environment simulates a cluster of nodes executing tasks.
    The agent assigns tasks to nodes when they request work.
    """

    def __init__(
        self, duration_fn, initial_task_queue: Optional[List[Tuple[int, int]]] = None
    ):

        self.cluster = NodeCluster(duration_fn)

        # Convert task queue from (task_type, parameter) tuples to encoded vectors
        if initial_task_queue:
            self.task_queue = [
                encode_task(task_type, param) for task_type, param in initial_task_queue
            ]
        else:
            self.task_queue = []

        self.total_time_elapsed = 0.0
        self.tasks_completed = 0

    def reset(self) -> Tuple[np.ndarray, List[int]]:
        # returns (state, requesting_node_ids) where state contains node_status

        self.cluster.reset()
        self.total_time_elapsed = 0.0
        self.tasks_completed = 0

        # Set all nodes to idle initially (assign no-op tasks)
        for node_id in range(NUM_NODES):
            self.cluster.assign_task(node_id, NO_OP_TASK)

        # Get all idle nodes (should be all of them after reset)
        idle_nodes = self.cluster.get_idle_nodes()

        state = self._get_state()
        return state, idle_nodes

    def step(
        self, actions: List[Tuple[int, np.ndarray]]
    ) -> Tuple[np.ndarray, Optional[List[int]], float, Dict]:
        """takes a list of (node_id, task) with task being an un-encoded, un-normalized (task_type, param)"""
        # Execute one step in the environment.
        # Takes a list of (node_id, task_vector) pairs and assigns all tasks.

        actions_encoded = []

        # encode the tasks
        for node_id, task in actions:
            task_type, param = task
            # parameter comes normalized, so no need to normalize
            actions_encoded.append(
                (node_id, encode_task(task_type, param, normalize=False))
            )

        # Assign all tasks to their respective nodes
        for node_id, task_vector in actions_encoded:
            self.cluster.assign_task(node_id, task_vector)

        # Run time forward until the next node becomes free
        freed_node_id = self.cluster.run_time_forward()

        # A task was completed if a node was freed
        if freed_node_id is not None:
            self.tasks_completed += 1

        # Update total time
        self.total_time_elapsed = self.cluster.current_time

        # Get the new state
        state = self._get_state()

        # Get all idle nodes (not just the one that was freed)
        # If no node was freed (all idle), we're done
        if freed_node_id is None:
            idle_nodes = None
            done = True
        else:
            idle_nodes = self.cluster.get_idle_nodes()
            done = False

        # Reward is 0 for each step except the final when its 1
        reward = 0 if done == False else -self.total_time_elapsed

        info = {
            'total_time': self.total_time_elapsed,
            'tasks_completed': self.tasks_completed,
            'done': done,
        }

        return state, idle_nodes, reward, info

    def _get_state(self) -> np.ndarray:
        return self.cluster.get_node_status()

    def get_full_state_for_agent(
        self, requesting_node: int, task: np.ndarray
    ) -> np.ndarray:
        # Get the full state vector in the one hot format that the agent uses for scoring.

        node_vector = encode_node(requesting_node)
        node_status = self._get_state()
        return np.concatenate([node_vector, node_status, task])
