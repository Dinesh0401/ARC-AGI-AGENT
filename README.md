# ARC-AGI-3 Research Agent: A Modular Cognitive AI System for Solving Unseen Interactive Environments

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open, research-grade cognitive AI framework designed to solve interactive, unseen reasoning tasks in the **ARC-AGI-3** benchmark. This project implements object-centric perception, graph state representations, multi-store cognitive memory, hypothesis-driven reasoning, heuristic search-based planning (BFS, A*, MCTS), predictive world modeling, and a closed-loop adaptive learning engine.

---

## 🌟 Architecture Overview

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

---

## 📅 Architectural Milestones (Completed 8/8)

- [x] **Phase 0 — Project Setup**: Modular architecture, environment wrapper, runner, CLI.
- [x] **Phase 1 — Environment Understanding**: Official action space integration, trajectory visualizer, replay viewer.
- [x] **Phase 2 — Baseline Agent**: `RandomAgent`, history logger, frame diff metrics, evaluation runner.
- [x] **Phase 3 — Object-Centric Perception**: Connected components (custom BFS), shape features, pairwise relation detector, `SceneGraph`.
- [x] **Phase 4 — Multi-Store Cognitive Memory**: `EpisodicMemory`, `SemanticMemory` (Rules), priority `WorkingMemory`, `ProceduralMemory`, and `KnowledgeBase`.
- [x] **Phase 5 — Reasoning Layer**: `HypothesisManager`, `InferenceEngine`, `ConfidenceTracker`, `Verifier`, and `GoalGenerator`.
- [x] **Phase 6 — Search-Based Planning**: `PlanningOrchestrator`, `BFSPlanner`, `AStarPlanner`, `MCTSPlanner`, `PlanEvaluator`, and `ActionSelector`.
- [x] **Phase 7 — Predictive World Model**: `Simulator`, `TransitionModel`, `StatePredictor`, `UncertaintyQuantifier`, and `PredictionEngine`.
- [x] **Phase 8 — The Learning Loop**: `ExperienceBuffer`, `PredictionErrorCalculator`, `BeliefUpdater`, `RuleLearner`, `StrategyUpdater`, and `LearningLoop`.

---

## 🛠️ Quick Start

### 1. Installation

Clone the repository and install dependencies:

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

### 2. Run Cognitive Agent

Run an episode using the full Cognitive Agent pipeline:

```bash
python main.py --agent cognitive --env sample_game --max-steps 20 --visualize
```

### 3. Run Comparative Benchmark

Run a 10-episode benchmark comparing agent performance:

```bash
python main.py --agent cognitive --benchmark --num-episodes 10
python main.py --agent random --benchmark --num-episodes 10
```

### 4. Run Unit Test Suite

```bash
python -m pytest tests/
```

---

## 📁 Repository Structure

```
ARC-AGI-AGENT/
├── agents/         # Base and concrete agent implementations (BaseAgent, RandomAgent, CognitiveAgent)
├── perception/     # Connected components, shape features, relation detector, SceneGraph
├── memory/         # Multi-store memory: Episodic, Semantic, Working, Procedural, KnowledgeBase
├── reasoning/      # Inference engine, hypothesis manager, verifier, confidence tracker, goal generator
├── planning/       # Search algorithms: BFS, A*, MCTS, path cost heuristics, PlanEvaluator
├── world_model/    # Predictive engine, simulator, transition rules, uncertainty quantifier
├── learning/       # Experience buffer, prediction error calculator, belief & rule learning loop
├── environment/    # Official ARC-AGI-3 environment wrapper & observation payload handling
├── evaluation/     # Metric logging, multi-episode benchmarking, trajectory runner
├── analysis/       # Frame and action trajectory statistics
├── utils/          # Logger, visualizers, replay loggers
├── docs/           # Full architectural specification (docs/architecture.md)
├── tests/          # Pytest unit and integration test suite
└── main.py         # Primary CLI entry point
```

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
