import socket
import time
from tasks.tasks.array_sorting import sort_array
from tasks.tasks.file_io import file_io
from tasks.tasks.matmul import matmul_task
from tasks.tasks.prime_calculation import primes_up_to

host = '10.0.0.9'
port = 5000
logger_host = '10.0.0.9'
logger_port = 5001

# Get hostname for logging
hostname = socket.gethostname()


# Helper function to send events to logger
def send_logger_event(message):
    """Send an event message to the logger"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            s.connect((logger_host, logger_port))
            s.sendall(message.encode())
    except Exception as e:
        print(f"Failed to send logger event: {e}")


# open a connection and wait for scheduler to assign task

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except ConnectionRefusedError:
            break

        # Log task request
        request_time = time.time()
        event_msg = f"NODE {hostname} EVENT TASK_REQUESTED TIME {request_time}"
        send_logger_event(event_msg)

        # tell it were ready for a task
        s.sendall('FINISH'.encode())

        # wait for scheduler response
        task = s.recv(1024).decode().split(' ')
        print(task)

        task_start_time = time.time()

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

        # Log task completion
        finish_time = time.time()
        event_msg = (
            f"NODE {hostname} EVENT TASK_FINISHED TIME {finish_time} TASK {task[1]}"
        )
        send_logger_event(event_msg)
