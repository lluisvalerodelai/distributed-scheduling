# launch a docker node by its name

#!/bin/bash

# Check if a node name was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <node-name>"
  echo "Available nodes:"
  echo "  laptop-fast"
  echo "  laptop-medium"
  echo "  laptop-constrained"
  echo "  laptop-slow-io"
  echo "  laptop-micro-1"
  echo "  laptop-micro-2"
  exit 1
fi

target_node="$1"

nodes=(
  "laptop-fast:2.0:4g:5001"
  "laptop-medium:1.0:2g:5002"
  "laptop-constrained:0.5:1g:5003"
  "laptop-slow-io:1.0:2g:5004"
  "laptop-micro-1:0.5:1g:5005"
  "laptop-micro-2:0.5:1g:5006"
)

found=false

for node in "${nodes[@]}"; do
  IFS=':' read -r name cpus mem port <<< "$node"
  
  if [ "$name" = "$target_node" ]; then
    found=true
    echo "Starting $name..."
    docker run -d \
      --name "$name" \
      --rm \
      --cpus="$cpus" \
      --memory="$mem" \
      -e NODE_NAME="$name" \
      -e PORT="$port" \
      --network=host \
      dockernode:latest
    break
  fi
done

if [ "$found" = false ]; then
  echo "Error: Node '$target_node' not found."
  exit 1
fi

echo "Node $target_node started!"
utils/view-docker-nodes.sh $target_node
