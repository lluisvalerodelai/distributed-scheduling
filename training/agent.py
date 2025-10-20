import torch
import torch.nn as nn
import numpy as np
from env import encode_node, encode_task, TASK_IDLE
from train_utils import encode_state


class SchedulingAgent:
    def __init__(self, input_dim=59, hidden_dim=128):
        """
        Initialize the scheduling agent with a neural network.

        Input dimensions:
        - 9: one-hot encoding of requesting node
        - 45: encoded node status (9 nodes × 5 values: 4 one-hot task + 1 time_remaining)
        - 5: encoded task (4 one-hot task type + 1 normalized parameter)
        Total: 59 elements
        """
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),  # Output a single score
        )

    def score(self, state, requesting_node, queued_tasks):
        """
        Given the current node state, a node requesting a task, and the list of queued tasks,
        return the most suitable task to assign to that node.

        state: np.ndarray of length 18 (raw node_status from env: [task_type_0, time_remaining_0, ...])
        requesting_node: int (0-8, node ID requesting a task)
        queued_tasks: list of (task_type, param) tuples where param is already normalized to [0, 1]
        """
        # Encode the requesting node as one-hot vector (length 9)
        node_vector = encode_node(requesting_node)

        # Encode the state: transform from raw 18-element state to 45-element one-hot encoded state
        # Each node gets 5 values: [one_hot_task (4), time_remaining (1)]
        encoded_node_status = encode_state(state)

        # Concatenate node and encoded state to create the first part of the input
        # This will be reused for all tasks
        node_and_state = np.concatenate([node_vector, encoded_node_status])

        best_task = None
        best_score = float('-inf')

        # For each task in the queue, compute a score
        for task_type, param in queued_tasks:
            # Encode the task (one-hot task type + normalized parameter = 5 values)
            # param is already normalized, so we pass normalize=False

            # CHECK PARAM VALUE (should be normalized)

            task_vector = encode_task(task_type, param, normalize=False)

            # Create full input vector: [node (9) + encoded_state (45) + task (5)] = 59
            full_vector = np.concatenate([node_and_state, task_vector])

            # Convert to torch tensor and run forward pass
            input_tensor = torch.FloatTensor(full_vector).unsqueeze(
                0
            )  # Add batch dimension

            with torch.no_grad():
                task_score = self.model(input_tensor).item()

            # Track the highest scoring task
            if task_score > best_score:
                best_score = task_score
                best_task = (task_type, param)

        # Return the best task (un-encoded as (task_type, param))
        if best_task is not None:
            return best_task
        else:
            # If no tasks in queue, return idle task
            return (TASK_IDLE, 0.0)
