from typing import List, Dict, Any, Tuple
from perception.scene_graph import SceneGraph

class EpisodicMemory:
    """Stores transitions of the agent's experiences."""
    
    def __init__(self):
        # Format: list of (SceneGraph, action, reward, next_SceneGraph)
        self.episodes: List[Tuple[SceneGraph, Any, float, SceneGraph]] = []
        
    def add_experience(self, state: SceneGraph, action: Any, reward: float, next_state: SceneGraph):
        """Record a single frame transition."""
        self.episodes.append((state, action, reward, next_state))
        
    def get_recent(self, n: int = 5) -> List[Tuple[SceneGraph, Any, float, SceneGraph]]:
        """Retrieve the n most recent experiences."""
        return self.episodes[-n:]
        
    def clear(self):
        self.episodes.clear()
