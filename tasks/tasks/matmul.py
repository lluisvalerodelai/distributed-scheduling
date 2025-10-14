import numpy as np


def matmul_task(n):
    # Generate random matrices using numpy, multiply with multiple cores with @
    mat_a = np.random.randint(-32767, 32767, size=(n, n), dtype=np.int32)
    mat_b = np.random.randint(-32767, 32767, size=(n, n), dtype=np.int32)

    # Numpy's @ operator uses optimized multi-threaded BLAS
    res = mat_a @ mat_b

    print(f"did a matmul ({n}x{n})")
    return res
