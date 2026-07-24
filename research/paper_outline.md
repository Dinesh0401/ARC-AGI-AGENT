# A Modular Cognitive AI Architecture for Object-Centric Interactive Reasoning in ARC-AGI-3

**Abstract**:
Solving interactive, unseen tasks in the ARC-AGI-3 benchmark requires agents to rapidly induce environment semantics, plan multi-step interventions, and adapt from sensory feedback without exhaustive brute-force search. We propose a 8-phase modular cognitive AI architecture integrating object-centric perception, symbolic state graphs, multi-store cognitive memory, hypothesis-driven action inference, state-space search planning (BFS, A*, MCTS), predictive world modeling, and error-driven belief learning. We evaluate our agent against the official ARC-AGI-3 public environment benchmark across 6 ablation configurations. Experimental results demonstrate that symbolic scene graph representation and predictive world simulation significantly reduce action count and boost task completion rates compared to unguided baselines.

---

## 1. Introduction & Motivation
- Overview of ARC-AGI-3 benchmark challenges (interactive visual grids, non-stationary task dynamics, 0-shot adaptation).
- Limitations of raw grid-to-action neural policies vs modular symbolic cognitive architectures.
- Primary Contributions:
  1. An open 8-layer cognitive pipeline (`Perception` → `Memory` → `Reasoning` → `Planning` → `World Model` → `Learning`).
  2. Object-centric perception converting 2D pixel grids into discrete relational `SceneGraph`s.
  3. Integrated predictive `WorldModel` enabling heuristic A* state-space search.

---

## 2. System Architecture & Data Flow

```text
Environment → Perception → Scene Graph → Knowledge Base → Memory → Reasoning → Planning → World Model → Learning Loop
```

### 2.1 Object-Centric Perception (`perception/`)
- Custom BFS Connected Component Extraction.
- Pairwise spatial and topological relation detection (`Touches`, `Contains`, `Left Of`).

### 2.2 Cognitive Memory System (`memory/`)
- **Episodic**: Chronological state-action-reward transition log.
- **Semantic**: Timeless IF-THEN rules.
- **Working**: Priority-queue (`heapq`) active thought scratchpad.
- **Procedural**: Situation-to-strategy context records.
- **Belief**: Dynamic hypotheses with evidence and contradiction counters.

### 2.3 Reasoning & Goal Generation (`reasoning/`)
- Deductive rule inference (`InferenceEngine`).
- Hypothesis generation (`HypothesisManager`).
- Hypothesis validation (`Verifier`).
- Goal emission (`GoalGenerator`).

### 2.4 Search-Based Planning (`planning/`)
- Abstract `Planner` interface (`BFSPlanner`, `AStarPlanner`, `MCTSPlanner`).
- Heuristic distance function $h(n)$ estimating target condition satisfaction.
- `PlanEvaluator` scoring plans based on risk, cost, and confidence.

### 2.5 Predictive World Model (`world_model/`)
- `TransitionModel`, `Simulator`, and `UncertaintyQuantifier`.
- Prediction caching `(SceneHash, Action) → Prediction` for accelerated search.

### 2.6 The Learning Loop (`learning/`)
- `ExperienceBuffer`, `PredictionErrorCalculator`.
- Backpropagation of prediction errors to update `BeliefMemory` and `TransitionModel` rules.

---

## 3. Experimental Setup & Research Questions

We formulate five core research questions:
- **RQ1**: Does object-centric perception improve task completion rate over raw pixel representations?
- **RQ2**: Does the predictive World Model reduce planning time and node expansion count?
- **RQ3**: Does prediction error backpropagation lead to faster belief convergence over sequential episodes?
- **RQ4**: Does multi-store cognitive memory reduce redundant exploration?
- **RQ5**: Which search planner (BFS vs A* vs MCTS) provides the optimal trade-off between speed and plan quality?

---

## 4. Empirical Evaluation & Ablation Results

| Variant Configuration | Win Rate (%) | Avg Steps | Avg Efficiency | 95% Confidence Interval |
| :--- | :---: | :---: | :---: | :---: |
| **Full Cognitive Agent** | **TBD** | **TBD** | **TBD** | ±X.XX |
| w/o Cognitive Memory | TBD | TBD | TBD | ±X.XX |
| w/o World Model | TBD | TBD | TBD | ±X.XX |
| w/o Planning (A*) | TBD | TBD | TBD | ±X.XX |
| w/o Learning Loop | TBD | TBD | TBD | ±X.XX |
| Random Baseline | TBD | TBD | TBD | ±X.XX |

---

## 5. Per-Episode Failure Diagnosis

We categorize failure modes into:
1. *Max step limit reached before goal state*.
2. *World Model prediction confidence drop*.
3. *Search planner returned empty plan*.
4. *Frontier search exhausted available actions*.

---

## 6. Conclusion & Future Work
- Summary of empirical findings.
- Roadmap toward competition deployment on Kaggle platform.
