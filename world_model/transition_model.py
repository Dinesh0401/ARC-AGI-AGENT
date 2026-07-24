from perception.scene_graph import SceneGraph
from typing import Dict, Any

class TransitionModel:
    """Stores and evaluates the dynamic rules of the environment."""
    
    def __init__(self):
        # Stubbed rules for phase 7. E.g. {"ACTION1": {"changes_color": True}}
        self.rules: Dict[str, Dict[str, Any]] = {}
        
    def add_rule(self, action: str, effects: Dict[str, Any]):
        self.rules[action] = effects
        
    def apply_rules(self, state: SceneGraph, action: str) -> SceneGraph:
        """Applies known transition rules to a clone of the state."""
        # For phase 7 MVP, we just return the state un-mutated unless it's our test action.
        # Deepcopy would be ideal, but for the MVP we will reconstruct or just mock.
        import copy
        new_state = copy.deepcopy(state)
        
        rule = self.rules.get(action)
        if rule and rule.get("changes_color"):
            # Dummy logic for testing
            for obj in new_state.objects.values():
                obj.color = (obj.color + 1) % 10
                
        return new_state
