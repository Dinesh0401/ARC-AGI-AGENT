# ARC-AGI-3 Official Integration Architecture

This document describes how our custom Cognitive AI framework acts as the "brain" behind the official ARC-AGI-3 competition agent interface.

By enforcing an **Adapter Pattern**, we isolate the cognitive reasoning processes from the competition-specific API quirks.

## Architecture Mapping

```text
       OFFICIAL KAGGLE COMPETITION LIFECYCLE
       ──────────────────────────────────────
                      │
                      ▼
┌───────────────────────────────────────────────┐
│              ARC Environment API              │
│       (JSON Frames, 64x64 grids, 0-15)        │
└───────────────────────────────────────────────┘
                      │
                      │ 1. Raw frames passed to choose_action()
                      ▼
┌───────────────────────────────────────────────┐
│            integration/arc_adapter.py         │
│          (Official choose_action entry)       │
└───────────────────────────────────────────────┘
                      │
                      │ 2. Parsing
                      ▼
┌───────────────────────────────────────────────┐
│          integration/frame_adapter.py         │
│         (Raw JSON → Objects/Relations)        │
└───────────────────────────────────────────────┘
                      │
                      │ 3. Normalized SceneGraph
                      ▼
    ╔═══════════════════════════════════════╗
    ║        COGNITIVE RESEARCH AGENT       ║
    ║                                       ║
    ║  ┌─────────────────────────────────┐  ║
    ║  │        Multi-Store Memory       │  ║
    ║  │ (Episodic, Semantic, Procedural)│  ║
    ║  └─────────────────────────────────┘  ║
    ║                 │                     ║
    ║                 ▼                     ║
    ║  ┌─────────────────────────────────┐  ║
    ║  │         Reasoning Engine        │  ║
    ║  │ (Hypotheses, Goals, Inferences) │  ║
    ║  └─────────────────────────────────┘  ║
    ║                 │                     ║
    ║                 ▼                     ║
    ║  ┌─────────────────────────────────┐  ║
    ║  │         Planning Engine         │  ║
    ║  │        (BFS / A* / MCTS)        │  ║
    ║  └─────────────────────────────────┘  ║
    ║                 │                     ║
    ║                 ▼                     ║
    ║  ┌─────────────────────────────────┐  ║
    ║  │           World Model           │  ║
    ║  │   (State Prediction, Simulator) │  ║
    ║  └─────────────────────────────────┘  ║
    ╚═══════════════════════════════════════╝
                      │
                      │ 4. Internal Action Sequence
                      ▼
┌───────────────────────────────────────────────┐
│         integration/action_adapter.py         │
│  (Internal sequence → ACTION1-7, Coordinates) │
└───────────────────────────────────────────────┘
                      │
                      │ 5. Validated action returned
                      ▼
┌───────────────────────────────────────────────┐
│                 ARC Swarm                     │
│           (Parallel Scorecard Runner)         │
└───────────────────────────────────────────────┘
                      │
                      │ 6. Output Generation
                      ▼
┌───────────────────────────────────────────────┐
│               submission.json                 │
└───────────────────────────────────────────────┘
```

## Why this Architecture?

1. **Separation of Concerns:** Our planner never needs to understand what `ACTION6` means or what parameters it takes. It plans in a generalized state space. The `action_adapter.py` translates the generalized decision into the exact syntax the competition expects.
2. **Robustness:** If Kaggle updates the environment rules or changes frame structures (as happens in ARC updates), only `frame_adapter.py` needs to be touched. The Cognitive Agent remains stable.
3. **Dual Use:** We can test the agent locally on custom benchmark rules (`main.py --mode research`) or wrap it for Kaggle (`main.py --mode competition`) without changing a single line in the core logic.
