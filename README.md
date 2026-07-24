# ARC-AGI-3 Research Agent: A Modular Cognitive AI System for Solving Unseen Interactive Environments

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open, research-grade cognitive AI framework designed to solve interactive, unseen reasoning tasks in the **ARC-AGI-3** benchmark. This project implements object-centric perception, graph state representations, episodic/semantic memory, hypothesis-driven action inference, and heuristic search-based planning (BFS, A*).

---

## 🌟 Architecture Overview

```
                          ┌───────────────────────────┐
                          │   ARC-AGI-3 Environment    │
                          └─────────────┬─────────────┘
                                        │ Observation (Grid / State JSON)
                                        ▼
                          ┌───────────────────────────┐
                          │    Object Parser & State  │
                          │          Graph            │
                          └─────────────┬─────────────┘
                                        │ Graph / Symbolic Objects
                                        ▼
    ┌──────────────────┐  ┌───────────────────────────┐  ┌──────────────────┐
    │  Memory Engine   │◄─┤      Cognitive Agent      ├─►│  Planner Engine  │
    │ Episodic/Semantic│  │   (Hypothesis / Reason)   │  │   (BFS / A*)     │
    └──────────────────┘  └─────────────┬─────────────┘  └──────────────────┘
                                        │ Selected Action
                                        ▼
                          ┌───────────────────────────┐
                          │    Action Execution       │
                          └───────────────────────────┘
```

---

## 📅 Research Roadmap (11 Phases)

- [x] **Phase 0 — Setup**: Modular project structure, environment wrapper, baseline runner, logger.
- [ ] **Phase 1 — Understand the Environment**: Action space analysis, frame parser, replay viewer.
- [ ] **Phase 2 — Baseline Agent**: `RandomAgent`, action logging, observation tracking.
- [ ] **Phase 3 — State Representation**: Object extraction, connected component analysis, state graph.
- [ ] **Phase 4 — Memory System**: Episodic memory, semantic memory, action-history indexing.
- [ ] **Phase 5 — Intelligent Exploration**: Frontier search, unknown area targeting.
- [ ] **Phase 6 — Action Inference**: Action meaning hypothesis generation & confidence scoring.
- [ ] **Phase 7 — Planning**: Search-based planning algorithms (BFS, A*, Beam Search).
- [ ] **Phase 8 — World Model**: Transition prediction engine and verification.
- [ ] **Phase 9 — Evaluation**: Performance metrics (win rate, efficiency, step count).
- [ ] **Phase 10 — Optimization**: Caching, heuristic search tuning, speedup.
- [ ] **Phase 11 — Final Submission**: Kaggle notebook packaging, final benchmark results.

---

## 🛠️ Quick Start

### 1. Installation

Clone the repository and create a Python virtual environment:

```bash
git clone https://github.com/Dinesh0401/ARC-AGI-AGENT.git
cd ARC-AGI-AGENT
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Baseline Agent

Run a sample game using the baseline `RandomAgent`:

```bash
python main.py --env sample_game --max-steps 20
```

### 3. Run Unit Tests

```bash
python -m pytest tests/
```

---

## 📁 Repository Structure

```
ARC-AGI-AGENT/
├── agents/         # Base and concrete agent implementations (BaseAgent, RandomAgent)
├── planner/        # Search algorithms and planning engine (Phase 7)
├── memory/         # Memory systems: episodic, semantic, action memory (Phase 4)
├── environment/    # ARC-AGI-3 environment wrapper & frame utilities
├── evaluation/     # Metric logging, benchmarking, and result aggregation
├── utils/          # Logging, configuration, and helpers
├── notebooks/      # Exploratory notebooks and visualization
├── tests/          # Pytest unit and integration test suite
├── docs/           # Architecture diagrams, specifications, setup guides
├── main.py         # Primary CLI entry point
├── requirements.txt# Dependencies
└── README.md       # Project documentation
```

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
