# System Architecture: Neuro-Symbolic Cognitive Multi-Agent System

This document outlines the architecture for the ARC-AGI Agent, which has been refactored from a monolithic search script into a **True Blackboard Cognitive Multi-Agent System**.

## 1. System Design Philosophy
The system combines neural/symbolic reasoning via specialized agents. Instead of a hard-coded procedural loop, the system executes an orchestration of independent agents that read and write to a centralized `Blackboard`. 

This design enables:
- **Model-Based Planning**: Internal physical simulations before execution.
- **Explainable AI**: Natural-language trace generation at every sub-step.
- **Self-Critique**: Agents evaluating and pruning the output of other agents.

## 2. True Blackboard Architecture
The `Blackboard` acts as the shared, centralized state mechanism. 
Agents **do not pass arguments to each other**. Instead, they read from structured fields and write their results back.

### Blackboard Data Structures
- `observations`: Current and previous environment states (SceneGraphs).
- `hypotheses`: Inducted physical rules, verified logic, and pruned candidates.
- `goals`: Active task-completion heuristics and exploration objectives.
- `predictions`: Simulated future states (world models).
- `plans`: Generated action sequences, scores, and active constraints.
- `memory`: Episodic histories (visited tiles, state hashes) and Semantic knowledge bases (object tracking).
- `metrics`: Quantitative analytics tracking execution success.

## 3. Agent Responsibilities

The `CognitiveAgent` serves merely as a deterministic orchestrator, calling `.run()` on each agent sequentially per environment step.

1. **Perception Agent**: Parses the raw pixel grid into a structured `SceneGraph`. Detects objects, shapes, bounding boxes, and relationships. Writes to `blackboard.observations`.
2. **Memory Agent**: Tracks object permanence across frames. Updates the semantic knowledge base (facts about objects) and episodic memory (historical states). Writes to `blackboard.memory`.
3. **Goal Agent**: Evaluates the current state and memory to determine high-level objectives (e.g., "Explore unseen tiles", "Move Object X"). Writes to `blackboard.goals`.
4. **Hypothesis Agent**: The inductive logic engine. Learns transition rules by comparing the last prediction to reality. Writes new rules to `blackboard.hypotheses`.
5. **World Model Agent**: Reads candidate actions and simulates them against the active transition rules to predict the future state. Writes to `blackboard.predictions`.
6. **Critic Agent**: The self-correction module. Evaluates the confidence of generated rules. Prunes hypotheses that consistently fail to predict reality.
7. **Planner Agent**: Model-based Beam Search planner. Uses task-completion heuristics (Goal Progress, Information Gain, Novelty, Loop Penalties) to score the generated world models. Writes the optimal action to `blackboard.plans`.
8. **Executor Agent**: Translates the selected internal action into an environment API call and executes it.

## 4. Explainability Layer & Tracing
Explainability is a core pillar of this architecture. Every agent produces a hierarchical JSON trace logged to `trace.json` every step.

```json
{
  "step": 42,
  "state_hash": "...",
  "timestamp": "...",
  "agent": "PlannerAgent",
  "action": "Plan",
  "confidence": 0.95,
  "reasoning": [
    "Beam search found optimal path for goal: 'Reach Object'",
    "Expected reward: 125.00",
    "Selected action: ACTION1"
  ],
  "metrics": { ... }
}
```

These traces are visualized live via the `dashboard.py` Control Center, transforming the agent from a black box into a fully transparent cognitive architecture.
