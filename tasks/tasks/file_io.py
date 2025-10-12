import os
import random
from dotenv import load_dotenv

load_dotenv()


def file_io(n):

    filename = os.getenv('IO_FILE_PATH')
    file_size = 6 * 1024 * 1024 * 1024  # 6 GB
    chunk_size = 4 * 1024  # all machines use 4KB pages
    num_operations = n

    with open(filename, "r+b") as f:  # binary mode

        if not os.path.exists(filename):
            raise FileNotFoundError(f"Cant find {filename}")

        for _ in range(num_operations):
            offset = random.randint(0, file_size - chunk_size)
            f.seek(offset)
            data = f.read(chunk_size)

            # write something back
            f.seek(offset)
            f.write(data[::-1])  # just reverse bytes to modify minimally

    print(f"did an io task (n={n})")
