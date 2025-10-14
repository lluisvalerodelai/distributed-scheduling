#!/bin/bash

# All available nodes
nodes=(
  "laptop-fast"
  "laptop-medium"
  "laptop-constrained"
  "laptop-slow-io"
  "laptop-micro-1"
  "laptop-micro-2"
)

# Define colors (ANSI escape codes)
colors=(
  $'\033[1;31m'  # Red
  $'\033[1;32m'  # Green
  $'\033[1;33m'  # Yellow
  $'\033[1;34m'  # Blue
  $'\033[1;35m'  # Magenta
  $'\033[1;36m'  # Cyan
)
NC="\033[0m"  # No Color / reset

# Check if docker is installed
if ! command -v docker &>/dev/null; then
  echo "Docker is not installed!"
  exit 1
fi

# If a node name is provided as an argument, filter the list
if [ -n "$1" ]; then
  target_node="$1"
  found=false
  for n in "${nodes[@]}"; do
    if [ "$n" = "$target_node" ]; then
      nodes=("$target_node")
      found=true
      break
    fi
  done

  if [ "$found" = false ]; then
    echo "Error: Node '$target_node' not found."
    echo "Available nodes: ${nodes[*]}"
    exit 1
  fi
fi

# Start logs for each node in background
for i in "${!nodes[@]}"; do
  node="${nodes[$i]}"
  color="${colors[$i % ${#colors[@]}]}"

  # Check if container exists and is running
  if ! docker ps --format '{{.Names}}' | grep -q "^${node}$"; then
    echo -e "${color}[${node}] Container not running${NC}"
    continue
  fi

  # Stream logs with color
  docker logs -f "$node" 2>&1 | sed "s/^/${color}[${node}] ${NC}/" &
done

# Wait for all background log streams
wait
