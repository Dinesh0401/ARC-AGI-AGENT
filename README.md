# ARC-AGI-AGENT
### A Modular Cognitive Research Agent for Interactive Reasoning

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-37%20reported-brightgreen.svg)](#testing-and-evaluation)

**ARC-AGI-AGENT** is a Python research project exploring a modular cognitive approach to interactive reasoning tasks inspired by the ARC-AGI-3 benchmark. It combines object-centric perception, multi-store memory, hypothesis-driven reasoning, goal-directed planning, predictive world modeling, and feedback-driven learning in one architecture.

> **Research status:** This repository documents the implemented architecture and its local test workflow. Passing unit tests and successful pipeline execution do not, by themselves, demonstrate strong generalization or competitive ARC-AGI-3 performance. Benchmark scores should be reported with reproducible evaluation details when available.

**Repository:** [Dinesh0401/ARC-AGI-AGENT](https://github.com/Dinesh0401/ARC-AGI-AGENT)

---

## Table of Contents

- [Goals](#goals)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [Getting Started](#getting-started)
- [Run the Agent](#run-the-agent)
- [Testing and Evaluation](#testing-and-evaluation)
- [Project Structure](#project-structure)
- [Design Principles](#design-principles)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Technology Stack](#technology-stack)
- [Contributing](#contributing)
- [License](#license)

## Goals

The project explores several central questions:

- Can visual grid observations be converted into structured objects and spatial relations?
- Can an agent use memory and explicit hypotheses instead of relying only on reactive heuristics?
- Can goal generation be separated from action-sequence planning?
- Can a predictive world model help an agent compare possible actions?
- Can prediction errors and past experience improve subsequent decisions?
- Can individual components be evaluated through controlled ablation experiments?

This is an evolving research and engineering project, not a claim that general intelligence or benchmark-level performance has been solved.

## Architecture

```text
 Environment Observation
          |
          v
 +------------------------+
 | Object-Centric         |
 | Perception / SceneGraph|
 +------------------------+
          |
          v
 +------------------------+       +------------------------+
 | Memory and Knowledge   |<----->| Reasoning and          |
 | Episodic / Semantic /  |       | Hypothesis Evaluation  |
 | Working / Procedural   |       +------------------------+
 +------------------------+                   |
          ^                                    v
          |                         +------------------------+
          |                         | Goal Generation        |
          |                         +------------------------+
          |                                    |
          |                                    v
 +------------------------+        +------------------------+
 | World Model            |<------>| Planner                |
 | Transitions /          |        | BFS / A* / MCTS         |
 | Prediction / Uncertainty|       +------------------------+
 +------------------------+                    |
          ^                                     v
          |                         +------------------------+
          +-------------------------| Action Execution       |
            Observations and        | and Feedback Loop      |
            Prediction Errors       +------------------------+
```

The architecture separates two responsibilities:

- **Reasoning:** What goal should the agent pursue, given its observations, memory, and current hypotheses?
- **Planning:** Which action or sequence of actions is most promising for reaching that goal?

The world model supports prediction and uncertainty estimation, while the learning loop uses observed outcomes and prediction errors to support updates to beliefs or strategies.

## Core Components

| Component | Responsibility |
|---|---|
| Environment | Wraps observations, actions, and episode status |
| Perception | Detects connected components, shape features, and spatial relations |
| Memory | Stores episodic, semantic, working, and procedural information |
| Reasoning | Generates and evaluates hypotheses, tracks confidence, and proposes goals |
| Planning | Searches for action sequences using BFS, A*, and MCTS implementations |
| World Model | Represents transitions and predicts possible next states |
| Learning | Records experience and uses prediction errors to support updates |
| Evaluation | Runs episodes and collects agent metrics |
| Research | Supports comparisons, ablations, statistical analysis, and failure diagnosis |
| Optimization | Provides state hashing, caching, and runtime/memory improvements |
| Submission | Contains competition-oriented wrappers and submission-generation code |

## Getting Started

### Requirements

- Python 3.10 or newer
- Git
- pip

### Installation

Clone the repository:

```bash
git clone https://github.com/Dinesh0401/ARC-AGI-AGENT.git
cd ARC-AGI-AGENT
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you use a different environment manager, activate that environment before installing dependencies.

## Run the Agent

Run the cognitive agent with the sample environment:

```bash
python main.py --agent cognitive --env sample_game --max-steps 20 --visualize
```

Check the available command-line options if needed:

```bash
python main.py --help
```

The available environment names and CLI options depend on the current implementation.

## Testing and Evaluation

### Run the Test Suite

```bash
python -m pytest tests/ -v
```

The previous README reported **37 passing tests**. Re-run this command on your current checkout to verify the present result.

### Compare Agents

```bash
python -m benchmark.compare_agents --episodes 5 --game sample_game
```

Use multiple episodes where supported, and keep the environment, seeds, step limits, and agent configuration consistent when comparing results.

### Competition Mode

```bash
python main.py --agent cognitive --competition
```

This command is intended to exercise the competition-mode submission path. Verify the generated files and required submission format before using the output in an external evaluation.

### Reporting Benchmark Results Responsibly

For meaningful performance claims, record at least:

- Environment or task set and its version
- Number of tasks and episodes evaluated
- Success or completion rate and scoring definition
- Action or step budget
- Runtime and hardware, when relevant
- Random seeds and configuration
- Baselines and ablation settings
- Known failures and limitations

Passing tests, successful execution, or generating a submission file does not establish a particular benchmark score.

## Project Structure

```text
ARC-AGI-AGENT/
├── agents/         # Agent interfaces and cognitive/baseline agents
├── perception/     # Object extraction and scene representation
├── memory/         # Memory stores and knowledge representations
├── reasoning/      # Hypotheses, inference, verification, and goals
├── planning/       # Search planners and plan evaluation
├── world_model/    # State prediction and transition modeling
├── learning/       # Experience and feedback-driven updates
├── environment/    # Environment wrappers and observation handling
├── evaluation/     # Episode execution and evaluation utilities
├── benchmark/      # Agent comparison and metric reporting
├── research/       # Experiments, ablations, and analysis
├── optimization/   # Caching and runtime/memory optimizations
├── submission/     # Competition-oriented execution path
├── analysis/       # Trajectory and action analysis
├── utils/          # Logging, visualization, and replay helpers
├── tests/          # Unit and integration tests
├── docs/           # Design and architecture documentation
└── main.py         # Command-line entry point
```

## Design Principles

### 1. Object-Centric Perception

Convert raw grid observations into objects and spatial relations where the environment supports that representation.

### 2. Separate Goals from Action Search

Keep high-level goal selection distinct from low-level search so each can be tested and improved independently.

### 3. Explicit Uncertainty

Treat predictions and hypotheses as uncertain estimates. Confidence should be calibrated against observed outcomes rather than treated as proof.

### 4. Modular Experiments

Use ablation studies to measure whether memory, planning, the world model, or learning actually improves performance.

### 5. Feedback-Driven Updates

Compare predicted outcomes with observations and use mismatches to diagnose failures and improve future decisions.

### 6. Reproducibility Over Impressive Claims

Prefer repeatable measurements, clear baselines, and documented limitations over unsupported performance claims.

## Current Limitations

- The existence of a module does not guarantee that it improves task-solving performance.
- Search-based planning can become expensive as the state and action spaces grow.
- A transition model may be inaccurate in unfamiliar environments.
- Object extraction and symbolic representations can lose information from raw observations.
- Generalization to unseen tasks must be demonstrated through evaluation, not inferred from architecture or unit tests.
- Compatibility with an official benchmark API and submission requirements should be verified against the exact version being used.

## Roadmap

- [ ] Document the exact environment/API version and setup procedure.
- [ ] Add reproducible evaluation commands, seeds, and configuration examples.
- [ ] Publish baseline-versus-cognitive-agent results on a clearly defined task set.
- [ ] Run ablations to measure the contribution of memory, planning, world modeling, and learning.
- [ ] Track failure cases and classify the causes of unsuccessful episodes.
- [ ] Validate competition submission compatibility end to end.
- [ ] Report runtime, resource usage, and benchmark results with enough detail to reproduce them.

## Technology Stack

- **Language:** Python 3.10+
- **Numerical operations:** NumPy
- **Visualization:** Matplotlib, Pillow
- **Data validation:** Pydantic
- **Testing:** pytest

The exact dependencies are defined in `requirements.txt` and `pyproject.toml`.

## Contributing

Ideas, bug reports, reproducible failure cases, and evaluation improvements are welcome.

When submitting a change:

1. Describe the problem and expected behavior.
2. Add or update tests for the change.
3. Run the relevant test suite.
4. Include benchmark configuration and results when making performance claims.

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.
