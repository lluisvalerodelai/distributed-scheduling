import socket
import threading
import time
import json
from random import shuffle


# We have a set of tasks
# We have the 3 nodes
# a task is nothing more than its id

matmul_task = "matmul"
primes = "primes"
array = "array"
fileIO = "fileIO"

# example set of tasks
tasks = [
    array,
    array,
    array,
    fileIO,
    fileIO,
    matmul_task,
    matmul_task,
    matmul_task,
    primes,
    primes,
    primes,
    primes,
    primes,
]
shuffle(tasks)

print("---------------------------------")
print(f"Task set: {tasks}")
print("---------------------------------")

# Scheduler configuration
host = '10.0.0.9'
port = 5000
scheduler_hostname = socket.gethostname()

# Data structures
registered_nodes = []  # List of registered node hostnames
node_lock = threading.Lock()
task_lock = threading.Lock()

waiting_tasks = tasks.copy()
processing_tasks = {}  # Maps node IP -> task being processed
finished_tasks = []

current_node_index = 0  # For round-robin assignment


def get_task_args(task_name):
    if task_name == 'matmul':
        return {"size": 425}
    elif task_name == 'primes':
        return {"max_n": 2400000}
    elif task_name == 'array':
        return {"array_size": 5000000}
    elif task_name == 'fileIO':
        return {"num_rw": 1000000}
    return {}


def manage_node(conn, addr):
    try:
        message = conn.recv(1024).decode().split('|')

        if len(message) < 2:
            print(f"Invalid message from {addr}: {message}")
            conn.close()
            return

        if message[0] == 'REGISTER':
            # Handle node registration
            if len(message) >= 3:
                node_hostname = message[2]

                with node_lock:
                    if node_hostname not in registered_nodes:
                        registered_nodes.append(node_hostname)
                        print(f"Node registered: {node_hostname} from {addr}")
                    else:
                        print(f"Node re-registered: {node_hostname}")

        elif message[0] == 'TASK':
            if len(message) >= 2:

                if message[1] == 'REQUEST':
                    # Handle task request
                    node_ip = addr[0]  # Use IP address as node identifier

                    with task_lock:
                        if len(waiting_tasks) > 0:
                            # Assign next task
                            task = waiting_tasks.pop(0)
                            processing_tasks[node_ip] = (
                                task  # Track which node has which task
                            )

                            task_args = get_task_args(task)
                            args_json = json.dumps(task_args)

                            # Send task: TASK|ASSIGN|task_name|json_args
                            response = f"TASK|ASSIGN|{task}|{args_json}"
                            conn.sendall(response.encode())

                            print(f"Assigned task '{task}' to node at {node_ip}")
                            print(f"Remaining tasks: {len(waiting_tasks)}")
                        else:
                            # No more tasks, send REST message
                            response = "TASK|ASSIGN|REST"
                            conn.sendall(response.encode())
                            print(f"No more tasks available. Sent REST to {node_ip}")

                elif message[1] == 'FINISH':
                    # Handle task completion: TASK|FINISH|duration
                    node_ip = addr[0]  # Use IP address as node identifier

                    if len(message) >= 3:
                        try:
                            duration = float(message[2])

                            with task_lock:
                                # Look up which task this specific node was working on
                                if node_ip in processing_tasks:
                                    finished_task = processing_tasks.pop(node_ip)
                                    finished_tasks.append(finished_task)

                                    print(
                                        f"Task '{finished_task}' completed by {node_ip} in {duration:.2f}s"
                                    )
                                    print(
                                        f"Progress: {len(finished_tasks)}/{len(tasks)} tasks completed"
                                    )

                                    if len(finished_tasks) == len(tasks):
                                        print("---------------------------------")
                                        print("ALL TASKS COMPLETED!")
                                        print("---------------------------------")
                                else:
                                    print(
                                        f"Warning: Node {node_ip} sent FINISH but no task was assigned to it"
                                    )
                        except ValueError:
                            print(
                                f"Invalid duration value from {node_ip}: {message[2]}"
                            )
                    else:
                        print(f"Invalid TASK|FINISH message from {addr}: {message}")

    except Exception as e:
        print(f"Error handling node {addr}: {e}")

    finally:
        conn.close()


# Main scheduler loop
print("---------------------------------")
print(f"Starting Round-Robin Scheduler on {host}:{port}")
print(f"Scheduler hostname: {scheduler_hostname}")
print("---------------------------------")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    print("---------------------------------")
    print(f"Listening on {host}:{port} for node work requests")
    print("---------------------------------")

    while True:
        print("waiting for node to connect...")
        conn, addr = s.accept()
        print(f"Connection received from {addr}")

        node_thread = threading.Thread(target=manage_node, args=(conn, addr))
        node_thread.start()
