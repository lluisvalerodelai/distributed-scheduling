#!/bin/bash

# Nodes to monitor
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
