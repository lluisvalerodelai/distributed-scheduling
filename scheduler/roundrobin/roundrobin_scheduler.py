import socket
import threading
from time import time
from random import shuffle

# We have a set of tasks
# We have the 3 nodes

# a task is nothing more than its id
matmul_task = "matmul"
primes = "primes"
array = "array"
fileIO = "fileIO"

# example set of tasks
tasks = [array, fileIO]
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

        else:
            conn.sendall("TASK FINISH".encode())
            print("Sending FINISHED message")
    else:
        print(status)

    print(f"Tasks left: {tasks}")
    conn.close()


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
