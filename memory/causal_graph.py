from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json

@dataclass
class CausalLink:
    """Represents a discovered causal relationship: Action -> Effect on Object."""
    action: str
    target_object_id: str
    effect_type: str # e.g. "MOVED", "COLOR_CHANGED", "DISAPPEARED"
    confidence: float = 0.5
    occurrences: int = 1

class CausalGraph:
    """Stores the agent's learned causal rules about the environment."""
    
    def __init__(self):
        # Mapping from action to a list of known effects
        self.edges: Dict[str, List[CausalLink]] = {}
        
    def record_effect(self, action: str, target_object_id: str, effect_type: str):
        """Update the causal graph with an observed effect."""
        action_str = str(action)
        if action_str not in self.edges:
            self.edges[action_str] = []
            
        # Check if link exists
        for link in self.edges[action_str]:
            if link.target_object_id == target_object_id and link.effect_type == effect_type:
                link.occurrences += 1
                link.confidence = min(1.0, link.confidence + 0.1)
                return
                
        # New link
        new_link = CausalLink(action=action_str, target_object_id=target_object_id, effect_type=effect_type)
        self.edges[action_str].append(new_link)
        
    def get_effects(self, action: str) -> List[CausalLink]:
        return self.edges.get(str(action), [])
