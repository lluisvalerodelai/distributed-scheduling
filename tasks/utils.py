def print_perf_times(perf_dict):
    print("Performance Summary:\n")
    for task, times in perf_dict.items():
        count = len(times)
        avg_time = sum(times) / count if count else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        print(f"Task: {task}")
        print(f"  Runs: {count}")
        print(f"  Avg time: {avg_time:.6f} sec")
        print(f"  Min time: {min_time:.6f} sec")
        print(f"  Max time: {max_time:.6f} sec")
        print("-" * 30)
