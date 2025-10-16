import multiprocessing
import numpy as np
import time


def multiply_chunk(args):
    """Top-level function: Multiply a chunk of rows of matrix A by matrix B"""
    A_chunk, B = args
    return np.dot(A_chunk, B)


def parallel_matrix_multiply(n):
    """
    Multiply two random square matrices of size n x n using all CPU cores.

    Parameters:
        n (int): Size of the square matrices.

    Returns:
        np.ndarray: Resulting matrix of size n x n.
        float: Time taken for multiplication in seconds.
    """

    # Generate random square matrices
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)

    num_cores = multiprocessing.cpu_count()

    # Split A into chunks, one per core
    chunk_size = n // num_cores
    A_chunks = [A[i * chunk_size : (i + 1) * chunk_size] for i in range(num_cores)]

    # Handle remaining rows
    remainder = n % num_cores
    if remainder:
        A_chunks[-1] = np.vstack([A_chunks[-1], A[-remainder:]])

    args = [(chunk, B) for chunk in A_chunks]

    # Multiply in parallel
    with multiprocessing.Pool(processes=num_cores) as pool:
        start_time = time.time()
        result_chunks = pool.map(multiply_chunk, args)
        end_time = time.time()

    # Combine the results
    C = np.vstack(result_chunks)

    return C, end_time - start_time


# Example usage
if __name__ == "__main__":
    n = 2000
    result, elapsed = parallel_matrix_multiply(n)
    print(f"Matrix multiplication of size {n}x{n} done in {elapsed:.2f} seconds")
    print(f"Result shape: {result.shape}")
