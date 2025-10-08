from time import time
from utils import print_perf_times
from tasks.array_sorting import sort_array
from tasks.prime_calculation import primes_up_to
from tasks.matmul import matmul_task
from tasks.file_io import file_io


def time_func(func: callable, *args):
    start = time()
    func(*args)
    end = time()
    return end - start


def get_avg_perf_times(iters, mat_size=1, array_size=1, primes_n=1, file_writes=1):

    matmul_times = []
    array_sort_times = []
    primes_calc_times = []
    file_write_times = []

    for _ in range(iters):
        matmul_time = time_func(matmul_task, mat_size)
        array_time = time_func(sort_array, array_size)
        primes_time = time_func(primes_up_to, primes_n)
        file_time = time_func(file_io, file_writes)

        matmul_times.append(matmul_time)
        array_sort_times.append(array_time)
        primes_calc_times.append(primes_time)
        file_write_times.append(file_time)

    return {
        "matmul": matmul_times,
        "array": array_sort_times,
        "primes": primes_calc_times,
        "file-io": file_write_times,
    }


times = get_avg_perf_times(
    iters=20, mat_size=100, array_size=1, primes_n=1, file_writes=1
)

print_perf_times(times)
