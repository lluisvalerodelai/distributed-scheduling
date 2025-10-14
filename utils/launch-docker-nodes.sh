#!/bin/bash

nodes=(
  "laptop-fast:2.0:4g:5001"
  "laptop-medium:1.0:2g:5002"
  "laptop-constrained:0.5:1g:5003"
  "laptop-slow-io:1.0:2g:5004"
  "laptop-micro-1:0.5:1g:5005"
  "laptop-micro-2:0.5:1g:5006"
)

for node in "${nodes[@]}"; do
  IFS=':' read -r name cpus mem port <<< "$node"
  
  echo "Starting $name..."
  docker run -d \
    --name $name \
    --rm \
    --cpus="$cpus" \
    --memory="$mem" \
    -e NODE_NAME=$name \
    -e PORT=$port \
    --network=host \
    dockernode:latest
done

echo "All nodes started!"
utils/view-docker-nodes.sh
