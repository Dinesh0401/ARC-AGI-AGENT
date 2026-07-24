"""Abstract Base Agent interface for ARC-AGI-3 cognitive system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import time


class BaseAgent(ABC):
    """Abstract Base Class for all ARC-AGI-3 agents."""

    def __init__(self, name: str = "BaseAgent") -> None:
        self.name = name
        self.action_history: List[Dict[str, Any]] = []
        self.observation_history: List[Dict[str, Any]] = []
        self.step_count: int = 0

    @abstractmethod
    def act(self, observation: Dict[str, Any]) -> Any:
        """Select an action based on current observation.

        Args:
            observation: Current environment observation payload.

        Returns:
            The action to be executed in the environment.
        """
        pass

    def record_step(self, observation: Dict[str, Any], action: Any, reward: float, done: bool) -> None:
        """Record step experience into history buffers."""
        self.step_count += 1
        record = {
            "step": self.step_count,
            "timestamp": time.time(),
            "action": action,
            "reward": reward,
            "done": done,
        }
        self.action_history.append(record)
        self.observation_history.append(observation)

    def reset(self) -> None:
        """Reset agent internal state and history."""
        self.action_history.clear()
        self.observation_history.clear()
        self.step_count = 0
