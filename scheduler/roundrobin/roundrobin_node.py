import socket
from time import time
from tqdm import tqdm

host = '10.0.0.9'
port = 5001

# open a connection and wait for scheduler to assign task

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        scheduler_conn = s.connect((host, port))

        scheduler_conn.sendall('FINISH'.encode())

        # wait for scheduler response
        task = scheduler_conn.recv(1024).decode().split(' ')
        print(task)
        scheduler_conn.close()
        for i in tqdm(range(20)):
            time.sleep(1)

        if 'FINISH' in task:
            break
