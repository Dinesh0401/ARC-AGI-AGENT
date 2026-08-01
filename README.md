# ARC-AGI-3 Multi Cognitive Research Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-37%2F37%20passed-brightgreen.svg)](#-testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modular cognitive AI framework for solving interactive, unseen reasoning tasks in the **ARC-AGI-3** benchmark. Implements object-centric perception, multi-store memory, hypothesis-driven reasoning, search-based planning (BFS, A*, MCTS), predictive world modeling, and closed-loop adaptive learning.

---

## Architecture

```text
                                  ┌───────────────────────────┐
                                  │   ARC-AGI-3 Environment    │
                                  └─────────────┬─────────────┘
                                                │ Observation Grid
                                                ▼
                                  ┌───────────────────────────┐
                                  │   Object-Centric Parser   │
                                  │       (Scene Graph)       │
                                  └─────────────┬─────────────┘
                                                │ Stateful Facts
                                                ▼
                                  ┌───────────────────────────┐
                                  │   Knowledge Base & Memory │
                                  │  (Episodic/Semantic/Work) │
                                  └─────────────┬─────────────┘
                                                │ Hypotheses
                                                ▼
  ┌──────────────────────────┐    ┌───────────────────────────┐    ┌──────────────────────────┐
  │      World Model         │◄───┤     Reasoning Layer       ├───►│      Planner Engine      │
  │ (Simulator/Uncertainty)  │    │   (Inference & Goals)     │    │   (BFS / A* / MCTS)      │
  └─────────────┬────────────┘    └─────────────┬─────────────┘    └─────────────┬────────────┘
                │ Prediction                    │ Goal Target                    │ Action Sequence
                └───────────────────────────────┼────────────────────────────────┘
                                                ▼
                                  ┌───────────────────────────┐
                                  │   Action Execution & Loop │
                                  │  (Error / Rule Learning)  │
                                  └───────────────────────────┘
```

The agent separates **"What should I do?"** (Reasoning → Goals) from **"How do I do it?"** (Planning → Action Sequences) — a core design principle from modern cognitive architectures.

---

## Quick Start

### Installation

```bash
git clone https://github.com/Dinesh0401/ARC-AGI-AGENT.git
cd ARC-AGI-AGENT
pip install -r requirements.txt
```

### Run the Cognitive Agent

```bash
python main.py --agent cognitive --env sample_game --max-steps 20 --visualize
```

### Run Comparative Benchmark

```bash
python -m benchmark.compare_agents --episodes 5 --game sample_game
```

### Run the Test Suite

```bash
python -m pytest tests/ -v
```

### Generate Kaggle Submission

```bash
python main.py --agent cognitive --competition
```

---

## Development Phases (Completed 12/12)

| Phase | Module | Description |
|-------|--------|-------------|
| 0 | Setup | Modular architecture, environment wrapper, CLI |
| 1 | Environment | Official action space integration, trajectory visualizer |
| 2 | Baseline Agent | `RandomAgent`, history logger, frame diff metrics |
| 3 | Perception | Connected components, shape features, relation detector, `SceneGraph` |
| 4 | Memory | Episodic, Semantic, Working, Procedural, KnowledgeBase, BeliefMemory |
| 5 | Reasoning | Inference engine, hypothesis manager, verifier, confidence tracker, goal generator |
| 6 | Planning | BFS, A*, MCTS planners with plan evaluation and action selection |
| 7 | World Model | Simulator, transition model, state predictor, uncertainty quantifier |
| 8 | Learning Loop | Experience buffer, prediction error, belief/rule/strategy updaters |
| 9–10 | Benchmarking | Metrics collection, comparative reports, ablation studies |
| 11 | Research | Statistical analysis, experiment runner, failure diagnosis |
| 12 | Competition | Runtime optimization, caching, Kaggle submission pipeline |

---

## Validated Results

| Validation | Status |
|---|---|
| Unit tests | **37/37 passed** (1.98s) |
| Cognitive pipeline | ✅ End-to-end execution |
| Environment integration | ✅ Actions, observations, status tracking |
| Benchmark framework | ✅ Agent comparison reports |
| Competition mode | ✅ `submission.json` generated |
| Runtime profiling | ✅ `runtime_profile.csv` generated |
| No crashes / import errors | ✅ |

---

## Repository Structure

```
ARC-AGI-AGENT/
├── agents/         # BaseAgent, RandomAgent, CognitiveAgent (with ablation toggles)
├── perception/     # Connected components, shape features, relation detector, SceneGraph
├── memory/         # Episodic, Semantic, Working, Procedural, KnowledgeBase, BeliefMemory
├── reasoning/      # Inference engine, hypothesis manager, verifier, goal generator
├── planning/       # BFS, A*, MCTS planners, path cost heuristics, PlanEvaluator
├── world_model/    # Predictive engine, simulator, transition rules, uncertainty
├── learning/       # Experience buffer, prediction error, belief & rule learning loop
├── environment/    # ARC-AGI-3 environment wrapper & observation handling
├── evaluation/     # Episode runner, multi-episode benchmarking
├── benchmark/      # Metrics collection, agent comparison, report generation
├── research/       # Ablation studies, statistical analysis, experiment runner
├── optimization/   # Scene hashing, caching, memory optimization
├── submission/     # Competition agent wrapper, Kaggle submission runner
├── analysis/       # Frame and action trajectory statistics
├── utils/          # Logger, visualizers, replay loggers
├── tests/          # 37 unit and integration tests
├── docs/           # Architectural specification
└── main.py         # CLI entry point (single episode, benchmark, competition)
```

---

## Key Design Decisions

**Object-centric perception** — Raw grids are parsed into symbolic objects with spatial relations, enabling structured reasoning rather than pixel-level heuristics.

**Separated reasoning and planning** — The reasoning layer decides *what* to do (goals), while the planning layer decides *how* (action sequences). This mirrors how modern cognitive architectures are designed.

**Domain-agnostic planner** — The planner knows nothing about doors, keys, or colors. It only knows states, actions, and goals. This allows the same planning infrastructure to generalize across different ARC-AGI-3 environments.

**Ablation toggles** — Each cognitive module (memory, world model, planning, learning) can be independently disabled for controlled experiments.

**Lightweight state transitions** — The world model avoids expensive deep copies by sharing immutable data structures and using identity-based fast paths.

---

## Technologies

- Python 3.10+
- NumPy (grid operations)
- Matplotlib / Pillow (visualization)
- Pydantic (data validation)
- Pytest (testing)

---

## License

MIT License. See [LICENSE](LICENSE) for details.
