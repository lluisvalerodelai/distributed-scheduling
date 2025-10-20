from env import encode_task, NUM_NODES
from random import shuffle


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


def random_scheduler(requesting_nodes, task_queue, state, duration_fn):
    """
    Random scheduling baseline: randomly assigns available tasks to requesting nodes.
    This serves as a baseline for comparison with more intelligent heuristics.
    """
    if not task_queue or not requesting_nodes:
        return []

    task_assignments = []
    available_tasks = task_queue.copy()

    # Shuffle tasks for random assignment
    shuffle(available_tasks)

    for idx, node_id in enumerate(requesting_nodes):
        if idx >= len(available_tasks):
            break

        task = available_tasks[idx]
        task_assignments.append((node_id, task))

    # Remove assigned tasks from queue
    for _, task in task_assignments:
        task_queue.remove(task)

    return task_assignments
