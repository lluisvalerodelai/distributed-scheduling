import socket
import json
import time
from tasks.tasks.array_sorting import sort_array
from tasks.tasks.matmul import matmul_task as matmul
from tasks.tasks.prime_calculation import primes_up_to as primes
from tasks.tasks.file_io import file_io


class SchedulerInterface:
    def __init__(self, ip: str, port: int, hostname: str):
        self.scheduler_ip = ip
        self.scheduler_port = port
        self.hostname = hostname

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.scheduler_ip, self.scheduler_port))
        self.socket.listen(5)
        print(f"Node listening on {self.scheduler_ip}:{self.scheduler_port}")

    def register(self) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.scheduler_ip, self.scheduler_port))
                sock.sendall(f'REGISTER|REQUEST|{self.hostname}'.encode())

                confirmation = sock.recv(1024).decode().split('|')
                if len(confirmation) >= 3 and confirmation[2] == 'true':
                    print(
                        f"Successfully registered with scheduler @ {self.scheduler_ip}:{self.scheduler_port} \
                        with sched_hostname: {confirmation[3]}"
                    )
                    return True

        except Exception as e:
            print("Error registering with scheduler:", e)
            return False

    def send_finish(self, duration):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as task_sock:
            task_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            task_sock.connect((self.scheduler_ip, self.scheduler_port))
            task_sock.sendall(f"TASK|FINISH|{duration}".encode())

    def run_tasks(self):

        while True:

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as task_sock:
                task_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                task_sock.connect((self.scheduler_ip, self.scheduler_port))
                print("Connected to scheduler to request a task")

                task_sock.sendall("TASK|REQUEST".encode())

                message = task_sock.recv(1024).decode().split("|")

            if len(message) < 3:
                print(f"strange message: {message}")
                break

            if message[2] == 'REST':
                print(f"REST MESSAGE RECIEVED")
                break

            args = json.loads(message[3])
            start = time.time()
            task_runner(message[2], args)
            end = time.time()

            self.send_finish(end - start)


def task_runner(task, args):

    if task == 'matmul':
        matmul(args["size"])
    elif task == 'primes':
        primes(args["max_n"])
    elif task == 'array':
        sort_array(args["array_size"])
    elif task == 'fileIO':
        file_io(args["num_rw"])


scheduler_ip = '10.0.0.9'
scheduler_port = 5000
hostname = socket.gethostname()
scheduler = SchedulerInterface(scheduler_ip, scheduler_port, hostname)

if scheduler.register():
    scheduler.run_tasks()
