"""Random Agent baseline implementation for ARC-AGI-3 abstract action spaces."""

import random
from typing import Any, Dict, List, Optional
from .base import BaseAgent


class RandomAgent(BaseAgent):
    """Agent that selects actions randomly from available abstract action tokens.

    Supports coordinate parameter sampling for complex actions (e.g. ACTION6).
    """

    def __init__(
        self,
        name: str = "RandomAgent",
        seed: Optional[int] = None,
        action_weights: Optional[Dict[str, float]] = None,
    ) -> None:
        super().__init__(name=name)
        self.seed = seed
        self.action_weights = action_weights
        if seed is not None:
            random.seed(seed)

    def is_done(self, frames: List[Dict[str, Any]], latest_frame: Dict[str, Any]) -> bool:
        return False

    def choose_action(self, frames: List[Dict[str, Any]], latest_frame: Dict[str, Any]) -> Any:
        """Select a random action token or parameterized tuple based on observation payload.

        Args:
            frames: History of frames.
            latest_frame: Environment observation payload.

        Returns:
            Chosen GameAction.
        """
        from integration.arc_adapter import ActionAdapter
        
        available_actions: List[str] = latest_frame.get(
            "available_actions", ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]
        )
        grid_shape = latest_frame.get("grid_shape", (10, 10))

        if not available_actions:
            chosen = "ACTION1"
        elif not self.action_weights:
            chosen = random.choice(available_actions)
        else:
            weights = [self.action_weights.get(act, 1.0) for act in available_actions]
            chosen = random.choices(available_actions, weights=weights, k=1)[0]

        # Handle complex coordinate action (ACTION6)
        if chosen == "ACTION6":
            h, w = grid_shape[0], grid_shape[1]
            rand_x = random.randint(0, max(0, w - 1))
            rand_y = random.randint(0, max(0, h - 1))
            chosen = f"ACTION6({rand_x},{rand_y})"

        return ActionAdapter.to_game_action(chosen)
