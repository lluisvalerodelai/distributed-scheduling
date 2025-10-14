#!/bin/bash

# Script to run benchmarks on all docker nodes and collect results

# Configuration
ITERATIONS=${1:-1}  # 1 iteration if not specified
BENCHMARK_DIR="utils/benchmark-times"

# Ensure benchmark directory exists
mkdir -p "$BENCHMARK_DIR"

# Node definitions (name:cpus:mem:port)
nodes=(
  "laptop-fast:2.0:4g:5001"
  "laptop-medium:1.0:2g:5002"
  "laptop-constrained:0.5:1g:5003"
  "laptop-slow-io:1.0:2g:5004"
  "laptop-micro-1:0.5:1g:5005"
  "laptop-micro-2:0.5:1g:5006"
)

echo "========================================"
echo "Benchmarking All Docker Nodes"
echo "Iterations per parameter: $ITERATIONS"
echo "Output directory: $BENCHMARK_DIR"
echo "========================================"
echo ""

for node in "${nodes[@]}"; do
  IFS=':' read -r name cpus mem port <<< "$node"

  echo "----------------------------------------"
  echo "Processing node: $name"
  echo "----------------------------------------"

  # Define output filename
  output_file="benchmark_results_${name}.csv"

  # Start the node (run in background)
  echo "Starting node $name..."
  docker run -d \
    --name "$name" \
    --rm \
    --cpus="$cpus" \
    --memory="$mem" \
    -e NODE_NAME="$name" \
    -e PORT="$port" \
    --network=host \
    dockernode:latest \
    python3 -u benchmark-node.py \
    --output "/node/utils/benchmark-times/$output_file" \
    --iterations "$ITERATIONS" \
    --node-name "$name"

  if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start container for $name"
    docker rm -f "$name" 2>/dev/null
    continue
  fi

  # Wait for the container to finish
  echo "Running benchmark on $name (this may take a while)..."
  docker wait "$name" > /dev/null

  # Copy results from container
  echo "Copying results from $name..."
  docker cp "${name}:/node/utils/benchmark-times/${output_file}" "$BENCHMARK_DIR/"

  if [ $? -eq 0 ]; then
    echo "✓ Successfully saved results to $BENCHMARK_DIR/$output_file"
  else
    echo "ERROR: Failed to copy results from $name"
  fi

  # Remove the container
  echo "Cleaning up container $name..."
  docker rm "$name" 2>/dev/null

  echo ""
done

echo "========================================"
echo "Benchmark Collection Complete!"
echo "========================================"
echo ""
echo "Results saved in: $BENCHMARK_DIR/"
ls -lh "$BENCHMARK_DIR"/*.csv 2>/dev/null || echo "No CSV files found"
