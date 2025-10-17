import os
import numpy as np
import multiprocessing
import numpy as np


def matmul_task(n):
    # Generate random square matrices
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)

    C = A @ B

    # Explicitly delete large arrays to free memory immediately
    del A, B, C
