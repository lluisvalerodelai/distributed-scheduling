"""
Test file with scheduling heuristics for comparison with RL agent.
Uses dummy_duration_fn to make intelligent task assignments.
"""

from random import shuffle
import numpy as np
from train_utils import dummy_duration_fn, task_queue, encode_state
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
from scheduling_policies import (
    random_scheduler,
    greedy_scheduler,
    shortest_job_first_scheduler,
    optimal_matching_scheduler,
)

shuffle(task_queue)

env = Env(dummy_duration_fn, task_queue)

state, requesting_nodes = env.reset()
done = False
total_reward = 0

while not done:

    task_assignments = greedy_scheduler(
        requesting_nodes, task_queue, state, dummy_duration_fn
    )

    next_state, requesting_nodes, reward, info = env.step(task_assignments)
    total_reward += reward

    print(pretty_print_state(next_state))
    print(pretty_print_requesting_nodes(requesting_nodes))
    print(pretty_print_reward(reward))
    print(pretty_print_info(info))
    print("-" * 50)
    print(encode_state(next_state))

    if info['done'] == True:
        break

print("=" * 50)
print(f"Total reward: {total_reward:.4f}")
