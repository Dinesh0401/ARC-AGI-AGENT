"""Planner optimization pruning state expansions and memoizing search heuristics."""

from typing import Dict, Set


class PlannerOptimizer:
    """Provides duplicate state detection and heuristic memoization for A* planner."""

    def __init__(self) -> None:
        self.memoized_heuristics: Dict[str, float] = {}
        self.visited_hashes: Set[str] = set()

    def is_visited(self, state_hash: str) -> bool:
        return state_hash in self.visited_hashes

    def mark_visited(self, state_hash: str) -> None:
        self.visited_hashes.add(state_hash)

    def get_memoized_heuristic(self, state_hash: str) -> float | None:
        return self.memoized_heuristics.get(state_hash)

    def set_memoized_heuristic(self, state_hash: str, score: float) -> None:
        self.memoized_heuristics[state_hash] = score

    def reset(self) -> None:
        self.visited_hashes.clear()
        self.memoized_heuristics.clear()
