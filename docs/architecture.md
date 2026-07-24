# Cognitive Agent Architecture

This document outlines the modular cognitive AI framework for the ARC-AGI-3 Agent, designed to transition from raw environmental data to high-level symbolic reasoning and strategic planning.

## High-Level Data Flow

```text
ARC Environment
        │ (Grid observation)
        ▼
   Perception
        │ (Objects, Geometry)
        ▼
   Scene Graph
        │ (Nodes + Relations)
        ▼
  Knowledge Base
        │ (Stateful Facts)
        ▼
 Cognitive Memory  ◄─── (Evidence/Episodes)
        │
        ▼
  Belief Memory
        │ (Confidence-scored Hypotheses)
        ▼
Hypothesis Manager
        │
        ▼
 Inference Engine
        │ (Deductive/Inductive logic)
        ▼
  Goal Generator
        │ (Concrete Objectives)
        ▼
     Planner
        │ (Search: BFS, A*, MCTS)
        ▼
  Action Selector
        │ (Executable Action Sequence)
        ▼
  ARC Environment
```

## Module Responsibilities

### 1. Perception (`perception/`)
Transforms raw pixel grids into an object-centric **Scene Graph**. It isolates objects using Connected Component Analysis, extracts geometric features (centroids, bounding boxes, shapes), and evaluates pairwise semantic relations (`Touches`, `Contains`, `Left Of`).

### 2. Knowledge Representation (`memory/knowledge_base.py`)
Acts as the intermediary between the visual Scene Graph and the Reasoning layer. It converts the graph into a flat, queryable dictionary of facts (e.g., `Object_001.Contains`).

### 3. Cognitive Memory (`memory/`)
A multi-store memory architecture:
- **Episodic**: Stores chronological transitions `(State, Action, Reward, Next State)`.
- **Semantic**: Stores global, timeless `Rule`s.
- **Working**: A Priority Queue for short-term thoughts and active contexts.
- **Procedural**: Stores contexts and strategies `Situation -> Strategy -> Outcome`.
- **Belief**: Tracks assumptions and hypotheses with dynamic confidence scores based on evidence.

### 4. Reasoning (`reasoning/`)
The "thinking" layer. Rather than searching blindly, it cross-references facts and rules (`InferenceEngine`), forms testable hypotheses (`HypothesisManager`), validates logical consistency (`Verifier`), and evaluates evidence (`ConfidenceTracker`). It ultimately emits structured `Goal`s to the planner.

### 5. Planning (`planning/`)
Strictly focused on state-space search. It receives a `Goal` and evaluates available paths using BFS, A*, or MCTS to find the optimal sequence of actions to satisfy the goal's target conditions.

## Future Roadmap

- **Phase 7: World Model**: Implementing an internal simulator capable of predicting `Next State` given `(Current State, Action)`, allowing the Planner to effectively roll out hypothetical futures.
- **Phase 8: Learning Loop**: Closing the cycle by comparing `Expected Outcomes` vs `Actual Outcomes` to calculate Prediction Errors, subsequently adjusting Semantic Rules and Beliefs.
