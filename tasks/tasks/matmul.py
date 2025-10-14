import os
import numpy as np
from numba import njit, prange, types
import multiprocessing


@njit(parallel=True, cache=True)
def matmul_task(n):
    # Allocate matrices
    A = np.empty((n, n), dtype=np.int32)
    B = np.empty((n, n), dtype=np.int32)

    # Fill matrices with random numbers (Numba-compatible)
    for i in prange(n):
        for j in range(n):
            A[i, j] = np.random.randint(-32767, 32767)
            B[i, j] = np.random.randint(-32767, 32767)

    # Allocate result matrix
    C = np.zeros((n, n), dtype=np.int32)

    # Matrix multiplication
    for i in prange(n):
        for j in range(n):
            for k in range(n):
                C[i, j] += A[i, k] * B[k, j]

    return C
