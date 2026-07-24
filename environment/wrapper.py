"""ARC-AGI-3 Environment wrapper and local simulator."""

from typing import Any, Dict, List, Tuple
import numpy as np


class ARCEnvironment:
    """Wrapper for ARC-AGI interactive environments.

    Provides reset(), step(), and observation state payload serialization.
    """

    def __init__(self, game_id: str = "sample_game", grid_size: Tuple[int, int] = (10, 10)) -> None:
        self.game_id = game_id
        self.grid_size = grid_size
        self.current_step = 0
        self.max_steps = 100
        self.done = False
        self.grid = np.zeros(grid_size, dtype=int)
        self.available_actions = [0, 1, 2, 3]  # e.g., 0: Up, 1: Right, 2: Down, 3: Left

    def reset(self) -> Dict[str, Any]:
        """Reset environment to initial state and return observation dictionary."""
        self.current_step = 0
        self.done = False
        self.grid = np.random.randint(0, 5, size=self.grid_size)
        return self._get_observation()

    def step(self, action: int) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Execute action and return (observation, reward, done, info).

        Args:
            action: Selected action integer identifier.

        Returns:
            Tuple of (observation_dict, reward, done, info_dict).
        """
        if self.done:
            raise RuntimeError("Cannot call step() on a terminated environment. Call reset() first.")

        self.current_step += 1
        
        # Simulate simple state modification based on action
        if action == 0:
            self.grid = np.roll(self.grid, -1, axis=0)
        elif action == 1:
            self.grid = np.roll(self.grid, 1, axis=1)
        elif action == 2:
            self.grid = np.roll(self.grid, 1, axis=0)
        elif action == 3:
            self.grid = np.roll(self.grid, -1, axis=1)

        # Check win condition or step limit
        reward = 0.0
        if self.current_step >= self.max_steps:
            self.done = True

        observation = self._get_observation()
        info = {"game_id": self.game_id, "step": self.current_step}

        return observation, reward, self.done, info

    def _get_observation(self) -> Dict[str, Any]:
        """Format observation payload."""
        return {
            "game_id": self.game_id,
            "step": self.current_step,
            "grid": self.grid.tolist(),
            "grid_shape": self.grid.shape,
            "available_actions": self.available_actions,
            "done": self.done,
        }
