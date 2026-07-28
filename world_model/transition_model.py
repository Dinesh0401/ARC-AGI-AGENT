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
        from perception.object_parser import Object
        
        rule = self.rules.get(action)
        
        if rule and rule.get("changes_color"):
            # Only clone when we actually need to mutate
            new_objects = []
            for obj in state.objects.values():
                new_obj = Object(
                    id=obj.id,
                    color=(obj.color + 1) % 10,
                    pixels=obj.pixels,  # share reference, don't copy
                    centroid=obj.centroid,
                    bbox=obj.bbox,
                    area=obj.area,
                    perimeter=obj.perimeter,
                    shape=obj.shape,
                )
                new_objects.append(new_obj)
            return SceneGraph(new_objects, state.relations)
        
        # No mutation needed — return state as-is (immutable usage)
        return state
