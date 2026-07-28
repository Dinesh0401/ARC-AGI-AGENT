from typing import List, Dict, Any, Tuple
from perception.scene_graph import SceneGraph

class EpisodicMemory:
    """Stores transitions of the agent's experiences."""
    
    def __init__(self):
        # Format: list of (SceneGraph, action, reward, next_SceneGraph)
        self.episodes: List[Tuple[SceneGraph, Any, float, SceneGraph]] = []
        # Track visit frequencies of state hashes
        self.visit_counts: Dict[int, int] = {}
        
    def add_experience(self, state: SceneGraph, action: Any, reward: float, next_state: SceneGraph):
        """Record a single frame transition."""
        self.episodes.append((state, action, reward, next_state))
        
        # Track visit counts
        state_hash = hash(state)
        self.visit_counts[state_hash] = self.visit_counts.get(state_hash, 0) + 1
        
    def get_visit_count(self, state: SceneGraph) -> int:
        """Get how many times a state has been visited."""
        return self.visit_counts.get(hash(state), 0)
        
    def get_recent(self, n: int = 5) -> List[Tuple[SceneGraph, Any, float, SceneGraph]]:
        """Retrieve the n most recent experiences."""
        return self.episodes[-n:]
        
    def get_recent_states(self, limit: int = 5) -> List[str]:
        """Get hashes of recently visited states to prevent deep loops."""
        hashes = []
        for exp in self.episodes[-limit:]:
            state = exp[3] # next_state
            state_hash = "|".join(sorted(f"{oid}:{obj.color}:{obj.centroid}" for oid, obj in state.objects.items()))
            hashes.append(state_hash)
        return hashes
        
    def clear(self):
        self.episodes.clear()
        self.visit_counts.clear()
