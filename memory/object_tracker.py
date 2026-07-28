from typing import Dict, List, Any, Optional
import math
from perception.scene_graph import SceneGraph
from perception.object_parser import Object

class TrackedObject:
    """Maintains the identity and history of an object across frames."""
    def __init__(self, obj: Object):
        self.identity_id = obj.id  # The persistent ID
        self.current_state = obj
        
        # History
        self.position_history: List[tuple] = [obj.centroid]
        self.interaction_history: List[str] = []
        self.color_history: List[int] = [obj.color]
        self.state_changes: int = 0
        
        # Inferred properties
        self.is_movable = False
        self.is_agent = False
        self.last_action_applied = None

    def update(self, new_obj: Object, action_applied: Optional[str] = None, causal_graph: Optional['CausalGraph'] = None):
        """Update tracked object with new state from the environment."""
        if new_obj.centroid != self.current_state.centroid:
            self.is_movable = True
            self.state_changes += 1
            if action_applied and causal_graph:
                causal_graph.record_effect(action_applied, self.identity_id, "MOVED")
            
        if new_obj.color != self.current_state.color:
            self.state_changes += 1
            if action_applied and causal_graph:
                causal_graph.record_effect(action_applied, self.identity_id, "COLOR_CHANGED")
            
        self.position_history.append(new_obj.centroid)
        self.color_history.append(new_obj.color)
        self.current_state = new_obj
        
        if action_applied:
            self.interaction_history.append(action_applied)
            self.last_action_applied = action_applied


class ObjectTracker:
    """Matches and tracks objects across sequential SceneGraphs."""
    
    def __init__(self, causal_graph: Optional['CausalGraph'] = None):
        self.tracked_objects: Dict[str, TrackedObject] = {}
        self.causal_graph = causal_graph
        
    def _distance(self, c1: tuple, c2: tuple) -> float:
        return math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)
        
    def track_scene(self, scene: SceneGraph, last_action: Optional[str] = None) -> None:
        """Map objects in the new scene to tracked objects, creating new ones if necessary."""
        unmatched_new = list(scene.objects.values())
        unmatched_tracked = list(self.tracked_objects.values())
        
        # 1. Exact Match (Same color, shape, and area, very close proximity)
        for tracked in unmatched_tracked[:]:
            best_match = None
            best_dist = float('inf')
            for new_obj in unmatched_new[:]:
                if new_obj.color == tracked.current_state.color and new_obj.area == tracked.current_state.area:
                    dist = self._distance(tracked.current_state.centroid, new_obj.centroid)
                    if dist < best_dist and dist < 10.0:  # Distance threshold
                        best_dist = dist
                        best_match = new_obj
                        
            if best_match:
                tracked.update(best_match, last_action, self.causal_graph)
                best_match.id = tracked.identity_id
                unmatched_new.remove(best_match)
                unmatched_tracked.remove(tracked)
                
        # 2. Relaxed Match (Color change, or area change)
        for tracked in unmatched_tracked[:]:
            best_match = None
            best_dist = float('inf')
            for new_obj in unmatched_new[:]:
                dist = self._distance(tracked.current_state.centroid, new_obj.centroid)
                if dist < best_dist and dist < 3.0: # Must be very close to be considered the same object mutating
                    best_dist = dist
                    best_match = new_obj
                    
            if best_match:
                tracked.update(best_match, last_action, self.causal_graph)
                best_match.id = tracked.identity_id
                unmatched_new.remove(best_match)
                unmatched_tracked.remove(tracked)
                
        # 3. New Objects
        for new_obj in unmatched_new:
            # Create new identity
            tracked = TrackedObject(new_obj)
            self.tracked_objects[tracked.identity_id] = tracked
            
        # Rebuild scene.objects dictionary with stable IDs
        scene.objects = {obj.id: obj for obj in scene.objects.values()}
        
        # We MUST also regenerate relations because the object IDs have changed!
        from perception.relation_detector import detect_relations
        new_relations = detect_relations(list(scene.objects.values()))
        scene.edges = {obj_id: [] for obj_id in scene.objects}
        for source_id, rel_type, target in new_relations:
            if source_id in scene.edges:
                scene.edges[source_id].append((rel_type, target))
        
    def get_tracked_object(self, obj_id: str) -> Optional[TrackedObject]:
        return self.tracked_objects.get(obj_id)
