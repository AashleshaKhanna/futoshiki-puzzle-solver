# Constraint Satisfaction Solver for Futoshiki and N-Queens

A Python constraint satisfaction problem (CSP) solver with backtracking search, Forward Checking, Generalized Arc Consistency, and Minimum Remaining Values variable ordering. The project includes Futoshiki puzzle encodings, N-Queens examples, and a custom test suite.

This repository converts an AI/CSP lab into a GitHub-ready engineering project that demonstrates search algorithms, constraint propagation, algorithmic problem solving, and clean Python software design.

## Why this project is useful for engineering roles

- Implements core AI search algorithms from scratch
- Models real problems as constraint satisfaction problems
- Designs reusable Python classes for variables, domains, constraints, and CSPs
- Implements backtracking with pluggable propagators
- Compares plain backtracking, Forward Checking, and Generalized Arc Consistency
- Applies MRV variable ordering to reduce search space
- Solves Futoshiki and N-Queens with automated correctness tests

## Core algorithms

- **Plain Backtracking**: checks fully assigned constraints after each assignment
- **Forward Checking**: prunes unsupported values when a constraint has one unassigned variable
- **Generalized Arc Consistency (GAC)**: iteratively prunes values that have no support in each constraint
- **Minimum Remaining Values (MRV)**: chooses the unassigned variable with the smallest current domain

## Repository structure

```text
constraint-satisfaction-futoshiki-solver/
├── README.md
├── PROJECT_SUMMARY.md
├── requirements.txt
├── futoshiki_csp.py
├── propagators.py
├── csp_sample_run.py
├── run_custom_tests.py
├── test_utils.py
├── tests.py
├── src/
│   ├── __init__.py
│   ├── csp_variable.py
│   ├── csp_constraint.py
│   ├── csp.py
│   └── backtracking.py
├── examples/
│   ├── solve_futoshiki.py
│   └── solve_n_queens.py
└── tests/
    └── test_solver_smoke.py
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python csp_sample_run.py
python run_custom_tests.py
pytest
```

## Solve a Futoshiki puzzle

```bash
python examples/solve_futoshiki.py
```

Example board format:

```python
board = [
    [3, '.', 0, '.', 0, '<', 0],
    [0, '.', 0, '.', 0, '.', 0],
    [0, '.', 0, '<', 0, '.', 0],
    [0, '.', 0, '>', 0, '.', 1],
]
```

Each row has length `2n - 1`, where numbers represent cells and symbols represent horizontal inequality constraints.

## Futoshiki models

1. **Model 1 — Binary constraints**: pairwise not-equal constraints for each row and column plus binary inequality constraints.
2. **Model 2 — N-ary all-different constraints**: one all-different constraint per row and column plus binary inequality constraints.

## Resume bullets

- Built a Python CSP solver implementing backtracking search, Forward Checking, Generalized Arc Consistency, and MRV variable ordering to solve Futoshiki and N-Queens problems.
- Modeled Futoshiki puzzles using binary and n-ary constraint formulations, comparing pruning efficiency and solver behavior across propagation strategies.
- Designed reusable CSP abstractions for variables, constraints, domains, satisfying tuples, and pruning/restoration, supported by automated correctness tests.
