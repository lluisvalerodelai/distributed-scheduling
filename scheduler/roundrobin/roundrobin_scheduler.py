import socket
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

# listen on socket
host = '10.0.0.9'  # listen only on eth interface
port = 42069

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    print("socket bound")

    while True:
        conn, addr = s.accept()
        print(f"New connection from {addr}")
        data = conn.recv(1024).decode()
        print(data)

        next_task = 'task'
        conn.send(next_task.encode())
        conn.close()
