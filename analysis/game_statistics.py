"""Game-level trajectory statistics and state coverage metrics."""

import hashlib
from typing import Any, Dict, List, Set


class GameStatistics:
    """Computes state coverage, unique states visited, and state repetition metrics."""

    def __init__(self) -> None:
        self.visited_state_hashes: Set[str] = set()
        self.total_state_visits: int = 0
        self.repeated_state_visits: int = 0

    @staticmethod
    def hash_frame(frame: List[List[int]]) -> str:
        """Generate a SHA-256 hash string for a 2D grid frame."""
        frame_str = str(frame)
        return hashlib.sha256(frame_str.encode("utf-8")).hexdigest()[:16]

    def record_frame(self, frame: List[List[int]]) -> str:
        """Record a frame state visit and return its state hash.

        Args:
            frame: 2D integer grid.

        Returns:
            State hash string.
        """
        state_hash = self.hash_frame(frame)
        self.total_state_visits += 1

        if state_hash in self.visited_state_hashes:
            self.repeated_state_visits += 1
        else:
            self.visited_state_hashes.add(state_hash)

        return state_hash

    def compute_summary(self) -> Dict[str, Any]:
        """Return summary of state visits and exploration metrics."""
        unique_count = len(self.visited_state_hashes)
        exploration_efficiency = (
            (unique_count / self.total_state_visits * 100.0) if self.total_state_visits > 0 else 0.0
        )
        return {
            "total_state_visits": self.total_state_visits,
            "unique_states_visited": unique_count,
            "repeated_state_visits": self.repeated_state_visits,
            "exploration_efficiency_percent": round(exploration_efficiency, 2),
        }

    def reset(self) -> None:
        """Reset internal statistical counters."""
        self.visited_state_hashes.clear()
        self.total_state_visits = 0
        self.repeated_state_visits = 0
