# Distributed Task Scheduler with Learned Embeddings

A reinforcement learning-based distributed job scheduler for allocating unprofiled tasks to heterogeneous compute nodes. The system learns to efficiently schedule novel tasks by leveraging learned embeddings of task characteristics and node capabilities.

## Overview

Traditional job schedulers rely on prior execution profiles to make allocation decisions. This project explores a reinforcement learning approach that can efficiently schedule never-before-seen tasks to heterogeneous nodes with minimal exploration overhead.

**Status**: Work in progress

## Architecture

### Task Embedding System

Tasks are encoded as 5-dimensional vectors capturing:
- Task type (one-hot encoded): matrix multiplication, prime calculation, array sorting, or file I/O
- Normalized parameter value representing task complexity

The embedding encodes task characteristics including:
- Single-core vs multi-core compute demand
- I/O intensity (disk read/write patterns)
- Memory access patterns
- CPU vs I/O bound behavior

### Model Components

**Allocator Network**: Multi-layer perceptron (59 → 128 → 1) that scores task-node assignments
- Input: concatenation of one-hot requesting node, encoded cluster state (9 nodes × 5 features), and task embedding
- Output: scalar assignment score

**Duration Predictor**: Regression-based execution time estimator used during training
- Models task execution characteristics with synthetic noise
- Factors in node heterogeneity (ARM vs x86, varying CPU/RAM/I/O capabilities)

### Training Environment

**Simulated Cluster**: 9 heterogeneous nodes (3 Raspberry Pi + 6 x86 containers)
- Discrete-event simulation tracking task execution and node state
- Regression models with added noise approximate real execution times
- Reward signal: negative total completion time (minimize makespan)

**Reinforcement Learning**: PPO-based training
- Learns allocation policy that generalizes to unseen task parameters
- Objective: minimize total cluster completion time across diverse workloads

## Implementation Details

### Task Types

Four synthetic workload classes with parametric complexity:
- **Matrix Multiplication**: Measures multi-core compute performance (param: matrix size)
- **Prime Calculation**: Single-core integer computation (param: search range)
- **Array Sorting**: Memory-bound operations (param: array size)
- **File I/O**: Disk read/write operations (param: operation count)

### State Representation

45-dimensional cluster state encoding:
- Per-node: 4-element one-hot task type + normalized remaining time
- Global view: concatenated state of all 9 nodes

### Baseline Comparisons

Four scheduling heuristics for evaluation:
- Random assignment
- Greedy shortest-job-first
- Global shortest-job-first
- Optimal greedy matching

## Key Innovation

The primary contribution is learning efficient task allocation with minimal profiling. By training on a diverse set of pre-defined task types with varying parameters, the model learns embeddings that capture task-node affinity. This enables rapid generalization: when presented with an unseen task parameter, the scheduler can make near-optimal allocation decisions in very few iterations, avoiding extensive profiling overhead.

## Repository Structure

```
training/          # RL agent, environment simulation, PPO training
tasks/             # Parametric workload generators
scheduler/         # Distributed scheduler implementation (round-robin baseline)
Node/              # Node configuration and interface
utils/             # Benchmarking and profiling utilities
```

## Future Work

- Complete PPO training loop integration
- Evaluate generalization to novel task types
- Deploy and benchmark on physical cluster
- Explore transformer-based architectures for set-to-set assignment
- Investigate multi-objective optimization (energy efficiency, fairness)
