"""ARC-AGI-3 Environment wrapper aligned with official competition specifications."""

from typing import Any, Dict, List, Tuple, Union, Optional
import numpy as np


class ARCEnvironment:
    """Wrapper for ARC-AGI-3 interactive environments.

    Uses official abstract action space tokens (RESET, ACTION1..ACTION7),
    official status strings (NOT_FINISHED, WIN, GAME_OVER), and 16-color grids (0-15).
    """

    OFFICIAL_ACTIONS = [
        "RESET",
        "ACTION1",
        "ACTION2",
        "ACTION3",
        "ACTION4",
        "ACTION5",
        "ACTION6",
        "ACTION7",
    ]

    def __init__(self, game_id: str = "sample_game", grid_size: Tuple[int, int] = (10, 10)) -> None:
        self.game_id = game_id
        self.grid_size = grid_size
        self.current_step = 0
        self.max_steps = 100
        self.status = "NOT_FINISHED"  # "NOT_FINISHED", "WIN", "GAME_OVER"
        self.grid = np.zeros(grid_size, dtype=int)
        self.prev_grid: Optional[np.ndarray] = None
        self.available_actions = ["RESET", "ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION6"]

    def reset(self) -> Dict[str, Any]:
        """Reset environment to initial state and return observation dictionary."""
        self.current_step = 0
        self.status = "NOT_FINISHED"
        self.grid = np.random.randint(0, 16, size=self.grid_size)
        self.prev_grid = None
        return self._get_observation()

    def step(self, action: Union[str, Tuple[str, int, int]]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Execute action and return (observation, reward, done, info).

        Args:
            action: Action token (e.g. "ACTION1") or tuple ("ACTION6", x, y).

        Returns:
            Tuple of (observation_dict, reward, done, info_dict).
        """
        if self.status != "NOT_FINISHED":
            raise RuntimeError(f"Cannot call step() when status is '{self.status}'. Call reset() first.")

        self.prev_grid = self.grid.copy()
        self.current_step += 1

        action_name = action[0] if isinstance(action, (list, tuple)) else str(action)

        if action_name == "RESET":
            return self.reset(), 0.0, False, {"game_id": self.game_id, "action": "RESET"}

        # Simulate abstract environment response to actions
        if action_name == "ACTION1":
            self.grid = np.roll(self.grid, -1, axis=0)
        elif action_name == "ACTION2":
            self.grid = np.roll(self.grid, 1, axis=1)
        elif action_name == "ACTION3":
            self.grid = np.roll(self.grid, 1, axis=0)
        elif action_name == "ACTION4":
            self.grid = np.roll(self.grid, -1, axis=1)
        elif action_name == "ACTION6" and isinstance(action, (list, tuple)) and len(action) == 3:
            _, x, y = action
            if 0 <= y < self.grid_size[0] and 0 <= x < self.grid_size[1]:
                self.grid[y, x] = (self.grid[y, x] + 1) % 16

        reward = 0.0
        done = False

        # Simulate potential win condition or max steps limit
        if self.current_step >= self.max_steps:
            self.status = "GAME_OVER"
            done = True

        observation = self._get_observation()
        info = {
            "game_id": self.game_id,
            "step": self.current_step,
            "action": action,
            "status": self.status,
            "diff_cells": self._calculate_diff_count(),
        }

        return observation, reward, done, info

    def _calculate_diff_count(self) -> int:
        """Count modified grid cells since previous step."""
        if self.prev_grid is None:
            return 0
        return int(np.sum(self.grid != self.prev_grid))

    def _get_observation(self) -> Dict[str, Any]:
        """Format official ARC-AGI-3 observation payload."""
        return {
            "game_id": self.game_id,
            "step": self.current_step,
            "frame": self.grid.tolist(),
            "grid_shape": list(self.grid.shape),
            "available_actions": self.available_actions,
            "status": self.status,
            "done": self.status != "NOT_FINISHED",
            "reward": 0.0,
            "diff_cells": self._calculate_diff_count(),
        }
