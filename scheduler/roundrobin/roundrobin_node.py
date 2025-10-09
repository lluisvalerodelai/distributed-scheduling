import socket
from tasks.tasks.array_sorting import sort_array
from tasks.tasks.file_io import file_io
from tasks.tasks.matmul import matmul_task
from tasks.tasks.prime_calculation import primes_up_to

host = '10.0.0.9'
port = 5000

# open a connection and wait for scheduler to assign task

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except ConnectionRefusedError:
            break

        # tell it were ready for a task
        s.sendall('FINISH'.encode())

        # wait for scheduler response
        task = s.recv(1024).decode().split(' ')
        print(task)
        if task[1] == 'matmul':
            print("Doing matmul task")
            matmul_task(425)
        if task[1] == 'primes':
            print("Doing primes task")
            primes_up_to(2400000)
        if task[1] == 'array':
            print("Doing array task")
            sort_array(5000000)
        if task[1] == 'fileIO':
            print("Doing fileIO task")
            file_io(1000000)

        if 'FINISH' in task:
            break
