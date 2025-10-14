from .matmul import matmul_task
import numpy as np

# precompile JIT matmul code
WARMUP_SIZE = 512
WARMUP_SIZE2 = 2000

# Precompile the function for float64 arrays
print("compiling matrix...")
matmul_task(WARMUP_SIZE)
print("50% there...")
matmul_task(WARMUP_SIZE2)
print("finished compiling")
