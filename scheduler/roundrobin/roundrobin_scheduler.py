import socket
import threading
from random import shuffle

# We have a set of tasks
# We have the 3 nodes

# a task is nothing more than its id
matmul_task = "matmul"
primes = "primes"
array = "array"
fileIO = "fileIO"

# example set of tasks
tasks = [matmul_task, matmul_task, primes, array, array, array, fileIO]
shuffle(tasks)

print("---------------------------------")
print(f"Task set: {tasks}")
print("---------------------------------")

node_assignment_queue = []

# listen on socket
host = '10.0.0.9'  # listen only on eth interface
port = 5001


def assign_task(conn, addr):

    # wait to recieve status from the node
    status = conn.recv(1024).decode()
    print(f"PROCESSING NODE [{addr}] STATE: {status}")

    if status == 'FINISH':
        task = tasks.pop()
        if task:
            conn.sendall(f"TASK {task}".encode())
            print(f"Assigning task {task} to {addr}")
        else:
            conn.sendall("TASK FINISH".encode())
            print("Sending FINISHED message")
    else:
        print("yeah lol this never happens")

    conn.close()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    print("---------------------------------")
    print("Listening on {host}:{port} for node work requests")
    print("---------------------------------")

    while True:
        conn, addr = s.accept()
        node_thread = threading.Thread(target=assign_task, args=(conn, addr))
        node_thread.start()
        if not node_assignment_queue:
            print("---------------------------------")
            print("ALL TASKS ARE FINISHED, WAITING FOR NODES TO FINISH")
            print("---------------------------------")
