"""Scene hashing for fast grid equivalence checking."""

import hashlib
import numpy as np


class SceneHasher:
    """Computes fast MD5 hashes for 2D numpy grids to skip redundant component parsing."""

    @staticmethod
    def hash_grid(grid: np.ndarray) -> str:
        """Compute hex hash of grid array."""
        grid_bytes = grid.tobytes()
        return hashlib.md5(grid_bytes).hexdigest()
