from random import randint


def matmul(A, B):
    n = len(A)  # A and B are n x n

    result = [[0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            sum_val = 0
            for k in range(n):
                sum_val += A[i][k] * B[k][j]
            result[i][j] = sum_val
    return result


def matmul_task(n=500):
    mat_a = []
    mat_b = []
    for _ in range(n):
        mat_a.append([randint(-32767, 32767) for _ in range(n)])
        mat_b.append([randint(-32767, 32767) for _ in range(n)])

    return matmul(mat_a, mat_b)
