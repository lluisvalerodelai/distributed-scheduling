import socket
import threading
import time
from random import shuffle


# Helper function to send events to logger
def send_logger_event(message, logger_host='10.0.0.9', logger_port=5001):
    """Send an event message to the logger"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            s.connect((logger_host, logger_port))
            s.sendall(message.encode())
    except Exception as e:
        print(f"Failed to send logger event: {e}")


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

node_assignment_queue = []

# listen on socket
host = '10.0.0.9'  # listen only on eth interface
port = 5000


def assign_task(conn, addr):
    global tasks

    # wait to recieve status from the node
    status = conn.recv(1024).decode()
    print(f"PROCESSING NODE [{addr}]  STATUS [{status}]")

    if status in {'FINISH', 'FINISH\n'}:

        if len(tasks) > 0:
            task = tasks.pop()
            conn.sendall(f"TASK {task}".encode())
            print(f"Assigning task {task} to {addr}")

            # Log the task assignment
            # Format: NODE [HOSTNAME] EVENT TASK_ASSIGNED TIME [TIME] TASK [TASK_NAME]
            hostname = addr[0]  # Use IP address as identifier for now
            event_msg = (
                f"NODE {hostname} EVENT TASK_ASSIGNED TIME {time.time()} TASK {task}"
            )
            send_logger_event(event_msg)

        else:
            conn.sendall("TASK FINISH".encode())
            print("Sending FINISHED message")
    else:
        print(status)

    print(f"Tasks left: {tasks}")
    conn.close()


start = time.time()

t = []
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    print("---------------------------------")
    print(f"Listening on {host}:{port} for node work requests")
    print("---------------------------------")

    while True:

        print("waiting for node to connect...")
        conn, addr = s.accept()

        node_thread = threading.Thread(target=assign_task, args=(conn, addr))
        t.append(node_thread)

        node_thread.start()
        if len(tasks) == 0:
            print("---------------------------------")
            print("ALL TASKS ARE FINISHED, WAITING FOR NODES TO FINISH")
            print("---------------------------------")
            break

print("main finishing")
for thrd in t:
    thrd.join()

end = time.time()
print("Total time (final tasks havent finished yet though)", end - start)
