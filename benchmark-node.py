import csv
import socket
import time
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tasks.tasks.matmul import matmul_task
from tasks.tasks.prime_calculation import primes_up_to
from tasks.tasks.array_sorting import sort_array
from tasks.tasks.file_io import file_io


def time_task(task_func, param_value):
    import traceback
    import gc

    start = time.time()
    try:
        task_func(param_value)
        end = time.time()

        return end - start

    except Exception as e:
        print(f"\n!!! Error executing task: {e}")
        print(f"!!! Task: {task_func.__name__}, Param: {param_value}")
        print("!!! Full traceback:")
        traceback.print_exc()
        return None


def generate_parameter_ranges():
    # Defaults: matmul=1000, primes=2400000, array=5000000, fileIO=1000000
    # create ~20 points spanning from ~10% to ~200% of default values.

    ranges = {
        'matmul': {
            'params': np.linspace(750, 5000, 20, dtype=int).tolist(),
            'param_name': 'size',
            'func': matmul_task,
        },
        'primes': {
            'params': np.linspace(240000, 4800000, 20, dtype=int).tolist(),
            'param_name': 'max_n',
            'func': primes_up_to,
        },
        'array': {
            'params': np.linspace(500000, 10000000, 20, dtype=int).tolist(),
            'param_name': 'array_size',
            'func': sort_array,
        },
        'fileIO': {
            'params': np.linspace(100000, 2000000, 20, dtype=int).tolist(),
            'param_name': 'num_rw',
            'func': file_io,
        },
    }
    return ranges


def run_benchmarks(
    output_file='utils/benchmark-times/benchmark_results.csv', iterations_per_param=1
):

    node_name = socket.gethostname()
    ranges = generate_parameter_ranges()

    # Create output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Starting benchmark sweep on node: {node_name}")
    print(f"Output file: {output_file}")
    print(f"Iterations per parameter: {iterations_per_param}")
    print("-" * 60)

    results = []

    # Run benchmarks for each task
    for task_name, task_config in ranges.items():
        print(f"\n{'='*60}")
        print(f"Benchmarking task: {task_name}")
        print(f"{'='*60}")

        param_name = task_config['param_name']
        task_func = task_config['func']
        params = task_config['params']

        total_runs = len(params) * iterations_per_param
        current_run = 0

        for param_value in params:
            print(f"\n[{task_name}] Testing {param_name}={param_value}")

            for iteration in range(iterations_per_param):
                current_run += 1
                print(
                    f"  Iteration {iteration + 1}/{iterations_per_param} "
                    f"(Progress: {current_run}/{total_runs})",
                    end=" ... ",
                )

                execution_time = time_task(task_func, param_value)

                if execution_time is not None:
                    print(f"{execution_time:.4f}s")
                    results.append(
                        {
                            'node': node_name,
                            'task': task_name,
                            'parameter': param_name,
                            'parameter_value': param_value,
                            'execution_time': execution_time,
                            'iteration': iteration + 1,
                        }
                    )
                else:
                    print("FAILED")

    # Write results to CSV
    print(f"\n{'='*60}")
    print(f"Writing results to {output_file}")
    print(f"{'='*60}")

    with open(output_file, 'w', newline='') as f:
        if results:
            fieldnames = [
                'node',
                'task',
                'parameter',
                'parameter_value',
                'execution_time',
                'iteration',
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            print(f"Successfully wrote {len(results)} data points to {output_file}")
        else:
            print("No results to write!")

    print("\nBenchmark sweep completed!")
    return results


def print_summary(results):
    if not results:
        print("No results to summarize")
        return

    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*60}")

    tasks = set(r['task'] for r in results)
    for task in sorted(tasks):
        task_results = [r for r in results if r['task'] == task]
        times = [r['execution_time'] for r in task_results]

        print(f"\nTask: {task}")
        print(f"  Total runs: {len(task_results)}")
        print(f"  Avg time: {np.mean(times):.4f}s")
        print(f"  Min time: {np.min(times):.4f}s")
        print(f"  Max time: {np.max(times):.4f}s")
        print(f"  Std dev: {np.std(times):.4f}s")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Run benchmark sweep for task performance modeling'
    )
    parser.add_argument(
        '--output',
        '-o',
        default='utils/benchmark-times/benchmark_results.csv',
        help='Output CSV file (default: utils/benchmark-times/benchmark_results.csv)',
    )
    parser.add_argument(
        '--iterations',
        '-i',
        type=int,
        default=1,
        help='Number of iterations per parameter value (default: 1)',
    )
    parser.add_argument(
        '--node-name',
        '-n',
        default=None,
        help='Override node name (default: use hostname)',
    )

    args = parser.parse_args()

    # Override hostname if specified
    if args.node_name:
        original_gethostname = socket.gethostname
        socket.gethostname = lambda: args.node_name

    results = run_benchmarks(
        output_file=args.output, iterations_per_param=args.iterations
    )
    print_summary(results)
