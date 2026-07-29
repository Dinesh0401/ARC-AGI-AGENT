from typing import List, Dict, Any, Tuple
from perception.scene_graph import SceneGraph

class EpisodicMemory:
    """Stores transitions of the agent's experiences."""
    
    def __init__(self):
        # Format: list of (SceneGraph, action, reward, next_SceneGraph)
        self.episodes: List[Tuple[SceneGraph, Any, float, SceneGraph]] = []
        # Track visit frequencies of state hashes
        self.visit_counts: Dict[int, int] = {}
        # Track physically visited grid coordinates (tiles)
        self.visited_tiles: set[Tuple[int, int]] = set()
        
    def _hash_state(self, state: SceneGraph) -> str:
        """Robust state hashing using exact object pixels to guarantee lossless representation."""
        pixel_tuples = []
        for obj in state.objects.values():
            pixel_tuples.append(f"{obj.color}:{tuple(sorted(obj.pixels))}")
        return str(hash(tuple(sorted(pixel_tuples))))
        
    def add_experience(self, state: SceneGraph, action: Any, reward: float, next_state: SceneGraph):
        """Record a single frame transition."""
        self.episodes.append((state, action, reward, next_state))
        
        # Track visit counts
        state_hash = self._hash_state(state)
        self.visit_counts[state_hash] = self.visit_counts.get(state_hash, 0) + 1
        
    def get_visit_count(self, state: SceneGraph) -> int:
        """Get how many times a state has been visited."""
        return self.visit_counts.get(self._hash_state(state), 0)
        
    def get_recent(self, n: int = 5) -> List[Tuple[SceneGraph, Any, float, SceneGraph]]:
        """Retrieve the n most recent experiences."""
        return self.episodes[-n:]
        
    def get_recent_states(self, limit: int = 5) -> List[str]:
        """Get hashes of recently visited states to prevent deep loops."""
        hashes = []
        for exp in self.episodes[-limit:]:
            hashes.append(self._hash_state(exp[3])) # next_state
        return hashes
        
    def clear(self):
        self.episodes.clear()
        self.visit_counts.clear()
        self.visited_tiles.clear()
