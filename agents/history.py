"""Action history tracking and state coverage statistics container for ARC-AGI-3 agents."""

from dataclasses import dataclass, field
from pathlib import Path
import json
import time
from typing import Any, Dict, List, Optional
from analysis.game_statistics import GameStatistics


@dataclass
class StepRecord:
    """Dataclass holding detailed step trajectory information."""

    step: int
    timestamp: float
    action: Any
    reward: float
    status: str
    diff_cells: int
    duration_ms: float = 0.0
    info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize StepRecord to dictionary."""
        return {
            "step": self.step,
            "timestamp": self.timestamp,
            "action": self.action,
            "reward": self.reward,
            "status": self.status,
            "diff_cells": self.diff_cells,
            "duration_ms": self.duration_ms,
            "info": self.info,
        }


class ActionHistory:
    """Manages agent step history, action distributions, state coverage, and timing metrics."""

    def __init__(self) -> None:
        self.records: List[StepRecord] = []
        self.action_counts: Dict[str, int] = {}
        self.total_reward: float = 0.0
        self.game_stats = GameStatistics()

    def add_step(
        self,
        step: int,
        action: Any,
        reward: float,
        status: str,
        diff_cells: int = 0,
        frame: Optional[List[List[int]]] = None,
        duration_ms: float = 0.0,
        info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a step record to history.

        Args:
            step: Step index.
            action: Action executed.
            reward: Step reward received.
            status: Game status string ("NOT_FINISHED", "WIN", "GAME_OVER").
            diff_cells: Modified cell count.
            frame: 2D frame grid for state coverage tracking.
            duration_ms: Decision latency in milliseconds.
            info: Optional metadata dictionary.
        """
        record = StepRecord(
            step=step,
            timestamp=time.time(),
            action=action,
            reward=reward,
            status=status,
            diff_cells=diff_cells,
            duration_ms=duration_ms,
            info=info or {},
        )
        self.records.append(record)
        self.total_reward += reward

        act_str = action[0] if isinstance(action, (list, tuple)) else str(action)
        self.action_counts[act_str] = self.action_counts.get(act_str, 0) + 1

        if frame:
            self.game_stats.record_frame(frame)

    def get_summary(self) -> Dict[str, Any]:
        """Compute aggregate trajectory summary statistics."""
        total_steps = len(self.records)
        avg_duration = (
            sum(r.duration_ms for r in self.records) / total_steps if total_steps > 0 else 0.0
        )
        coverage_summary = self.game_stats.compute_summary()

        return {
            "total_steps": total_steps,
            "total_reward": self.total_reward,
            "action_counts": dict(self.action_counts),
            "avg_decision_duration_ms": round(avg_duration, 3),
            "state_coverage": coverage_summary,
        }

    def clear(self) -> None:
        """Reset all history records."""
        self.records.clear()
        self.action_counts.clear()
        self.total_reward = 0.0
        self.game_stats.reset()

    def save_json(self, filepath: Path) -> None:
        """Export history to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "summary": self.get_summary(),
            "records": [r.to_dict() for r in self.records],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
