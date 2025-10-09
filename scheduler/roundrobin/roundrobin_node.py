import socket
from tqdm import tqdm
import time

host = '10.0.0.9'
port = 5000

# open a connection and wait for scheduler to assign task

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        s.sendall('FINISH'.encode())

        # wait for scheduler response
        task = s.recv(1024).decode().split(' ')
        print(task)
        s.close()

        for i in tqdm(range(20)):
            time.sleep(1)

        if 'FINISH' in task:
            break
