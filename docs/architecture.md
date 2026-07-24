# System Architecture Documentation

## ARC-AGI-3 Cognitive AI Agent Architecture

The system is designed as a modular, decoupled research architecture where perception, memory, hypothesis generation, search planning, and evaluation are separated into distinct packages.

```
+-------------------------------------------------------------------+
|                        Evaluation Pipeline                        |
|                        (evaluation/runner.py)                     |
+---------------------------------+---------------------------------+
                                  |
                                  v
+---------------------------------+---------------------------------+
|                       ARCEnvironment Wrapper                      |
|                      (environment/wrapper.py)                     |
+---------------------------------+---------------------------------+
                                  | Observations & Feedback
                                  v
+---------------------------------+---------------------------------+
|                         BaseAgent Interface                       |
|                          (agents/base.py)                         |
+---------------+-----------------+----------------+----------------+
                |                 |                |
                v                 v                v
        +---------------+ +---------------+ +---------------+
        | Object Parser | | Memory System | | Planner Engine|
        | (Phase 3)     | | (Phase 4)     | | (Phase 7)     |
        +---------------+ +---------------+ +---------------+
```

### Module Responsibilities

1. **Perception & State Representation (`agents/`, `environment/`)**:
   - Parses raw environment observations (JSON state, grids).
   - Extracts connected objects, color properties, spatial relations, and grid transforms.

2. **Memory System (`memory/`)**:
   - Maintains **Episodic Memory** (log of past step trajectories).
   - Maintains **Semantic Memory** (learned object behaviors and action outcome maps).

3. **Hypothesis & Action Inference (`agents/`, `planner/`)**:
   - Infers action semantics dynamically based on observed state transitions.
   - Evaluates hypothesis confidence scores.

4. **Planning Engine (`planner/`)**:
   - Executes search algorithms (BFS, A*, Beam Search) over state graphs to reach targeted goal configurations.

5. **Benchmarking & Evaluation (`evaluation/`)**:
   - Tracks metrics across environment runs (win rate, action efficiency, runtime).
