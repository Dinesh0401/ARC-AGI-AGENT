"""Abstract Base Agent interface for ARC-AGI-3 cognitive system."""

from abc import ABC, abstractmethod
import time
from typing import Any, Dict, List, Optional
from .history import ActionHistory


class BaseAgent(ABC):
    """Abstract Base Class for all ARC-AGI-3 agents."""

    def __init__(self, name: str = "BaseAgent") -> None:
        self.name = name
        self.history = ActionHistory()
        self.observation_history: List[Dict[str, Any]] = []
        self.step_count: int = 0

    @abstractmethod
    def act(self, observation: Dict[str, Any]) -> Any:
        """Select an action based on current observation payload.

        Args:
            observation: Current environment observation payload.

        Returns:
            The action to be executed in the environment.
        """
        pass

    def record_step(
        self,
        observation: Dict[str, Any],
        action: Any,
        reward: float,
        status: str,
        diff_cells: int = 0,
        frame: Optional[List[List[int]]] = None,
        duration_ms: float = 0.0,
        info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record step experience into ActionHistory and observation buffers."""
        self.step_count += 1
        self.history.add_step(
            step=self.step_count,
            action=action,
            reward=reward,
            status=status,
            diff_cells=diff_cells,
            frame=frame or observation.get("frame", observation.get("grid")),
            duration_ms=duration_ms,
            info=info,
        )
        self.observation_history.append(observation)

    def on_episode_start(self) -> None:
        """Lifecycle hook triggered before episode begins."""
        self.reset()

    def on_episode_end(self) -> None:
        """Lifecycle hook triggered after episode ends."""
        pass

    def reset(self) -> None:
        """Reset agent internal state and history buffers."""
        self.history.clear()
        self.observation_history.clear()
        self.step_count = 0
