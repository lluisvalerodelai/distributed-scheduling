from .matmul import matmul_task
import numpy as np

# precompile JIT matmul code
WARMUP_SIZE = 512

# Precompile the function for float64 arrays
matmul_task(WARMUP_SIZE)
