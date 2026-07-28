from typing import Dict, Any, List
from perception.scene_graph import SceneGraph
from perception.object_parser import Object

class KnowledgeBase:
    """Stores the active facts about the current state/episode."""
    
    def __init__(self):
        # Format: { "Object_001": {"color": 3, "Reachable": True, "Contains": ["Object_002"]}, ... }
        self.facts: Dict[str, Dict[str, Any]] = {}
        
    def update_from_scene_graph(self, scene_graph: SceneGraph):
        """Translate the SceneGraph into knowledge base facts."""
        self.facts.clear()
        
        for obj_id, obj in scene_graph.objects.items():
            self.facts[obj_id] = {
                "color": obj.color,
                "shape": obj.shape,
                "area": obj.area,
                "movable": obj.movable,
                "visited": obj.visited,
            }
            
        for obj_id in scene_graph.objects:
            relations = scene_graph.get_relations(obj_id)
            for rel_type, target in relations:
                if rel_type not in self.facts[obj_id]:
                    self.facts[obj_id][rel_type] = []
                self.facts[obj_id][rel_type].append(target)
                
    def get_object_facts(self, obj_id: str) -> Dict[str, Any]:
        return self.facts.get(obj_id, {})
        
    def query(self, attribute: str, value: Any) -> List[str]:
        """Find objects matching a specific attribute and value."""
        results = []
        for obj_id, attrs in self.facts.items():
            if attrs.get(attribute) == value:
                results.append(obj_id)
        return results

    def update_fact(self, obj_id: str, attributes: Dict[str, Any]) -> None:
        """Update or insert facts for a single object."""
        if obj_id not in self.facts:
            self.facts[obj_id] = {}
        self.facts[obj_id].update(attributes)
