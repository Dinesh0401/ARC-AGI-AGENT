"""Random Agent implementation for ARC-AGI-3 baseline execution."""

import random
from typing import Any, Dict, List, Optional
from .base import BaseAgent


class RandomAgent(BaseAgent):
    """Agent that selects actions uniformly at random from available actions."""

    def __init__(self, name: str = "RandomAgent", seed: Optional[int] = None) -> None:
        super().__init__(name=name)
        if seed is not None:
            random.seed(seed)

    def act(self, observation: Dict[str, Any]) -> Any:
        """Select a random action from the observation's available actions list.

        Args:
            observation: Environment observation containing 'available_actions' key.

        Returns:
            Chosen action.
        """
        available_actions: List[Any] = observation.get("available_actions", [])
        if not available_actions:
            # Fallback action if available_actions is empty or unspecified
            return 0
        return random.choice(available_actions)
