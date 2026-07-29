from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from perception.scene_graph import SceneGraph

@dataclass
class TransitionRule:
    effects: Dict[str, Any]
    target_color: Optional[int] = None
    target_shape: Optional[str] = None
    target_area: Optional[int] = None
    target_id: Optional[str] = None
    target_relations: List[tuple] = field(default_factory=list)
    
    successful_matches: int = 0
    total_matches: int = 0
    
    @property
    def confidence(self) -> float:
        if self.total_matches == 0:
            return 0.5
        return self.successful_matches / self.total_matches
        
    @property
    def specificity(self) -> int:
        score = 0
        if self.target_color is not None: score += 1
        if self.target_shape is not None: score += 1
        if self.target_area is not None: score += 1
        if self.target_id is not None: score += 2
        score += len(self.target_relations)
        return score
        
    def matches(self, obj, state: SceneGraph) -> bool:
        if self.target_id is not None and self.target_id != obj.id: return False
        if self.target_color is not None and self.target_color != obj.color: return False
        if self.target_shape is not None and self.target_shape != obj.shape: return False
        if self.target_area is not None and self.target_area != obj.area: return False
        
        if self.target_relations:
            current_rels = state.get_relations(obj.id)
            for rel in self.target_relations:
                if rel not in current_rels:
                    return False
        return True


class TransitionModel:
    """Stores and evaluates the dynamic rules of the environment."""
    
    def __init__(self):
        # Mapping from action -> list of TransitionRule
        self.rules: Dict[str, List[TransitionRule]] = {}
        
    def update_from_error(self, action: str, prediction_error: float, actual_state: SceneGraph, pre_state: SceneGraph):
        """Learn from prediction error by comparing pre_state and actual_state."""
        if action not in self.rules:
            self.rules[action] = []
            
        # 1. Update statistics for existing rules
        for rule in self.rules[action]:
            for obj_id, old_obj in pre_state.objects.items():
                if rule.matches(old_obj, pre_state):
                    rule.total_matches += 1
                    current_obj = actual_state.objects.get(obj_id)
                    if current_obj:
                        succeeded = True
                        if rule.effects.get("changes_color"):
                            if old_obj.color == current_obj.color:
                                succeeded = False
                        if "movement" in rule.effects:
                            mv = rule.effects["movement"]
                            if isinstance(mv, tuple) and len(mv) == 2 and mv[0] != 'unknown':
                                dx = current_obj.centroid[0] - old_obj.centroid[0]
                                dy = current_obj.centroid[1] - old_obj.centroid[1]
                                if abs(dx - mv[0]) > 1e-4 or abs(dy - mv[1]) > 1e-4:
                                    succeeded = False
                        if succeeded:
                            rule.successful_matches += 1
                            
        # Prune rules with very poor confidence after enough observations
        self.rules[action] = [r for r in self.rules[action] if r.total_matches < 3 or r.confidence > 0.2]
        
        # 2. Extract new rules if prediction was wrong
        if prediction_error >= 0.1:
            for obj_id, current_obj in actual_state.objects.items():
                if obj_id in pre_state.objects:
                    old_obj = pre_state.objects[obj_id]
                    obj_effects = {}
                    
                    if old_obj.color != current_obj.color:
                        obj_effects["changes_color"] = True
                    
                    # Flexible movement verification
                    if old_obj.centroid != current_obj.centroid:
                        dx = current_obj.centroid[0] - old_obj.centroid[0]
                        dy = current_obj.centroid[1] - old_obj.centroid[1]
                        
                        if abs(dx - round(dx)) < 1e-4 and abs(dy - round(dy)) < 1e-4:
                            obj_effects["movement"] = (int(round(dx)), int(round(dy)))
                        else:
                            obj_effects["movement"] = (round(dx, 2), round(dy, 2))
                            
                        # Detect shape change (often causes non-integer centroid shifts)
                        if len(old_obj.pixels) != len(current_obj.pixels) or old_obj.shape != current_obj.shape:
                            obj_effects["changes_shape"] = True
                    
                    if obj_effects:
                        # Do NOT extract relations for preconditions. 
                        # Overfitting to spatial relations causes rules to break as soon as objects move.
                        safe_rels = []
                                
                        new_rule = TransitionRule(
                            effects=obj_effects,
                            target_color=old_obj.color,
                            target_shape=old_obj.shape,
                            target_area=old_obj.area,
                            target_relations=safe_rels,
                            successful_matches=1,
                            total_matches=1
                        )
                        
                        # Check if similar rule exists
                        exists = False
                        for r in self.rules[action]:
                            if (r.target_color == new_rule.target_color and 
                                r.target_shape == new_rule.target_shape and 
                                r.target_area == new_rule.target_area and
                                r.effects == new_rule.effects):
                                exists = True
                                break
                        if not exists:
                            self.rules[action].append(new_rule)
        
    def add_rule(self, action: str, effects: Dict[str, Any], target_object_id: str = None):
        if action not in self.rules:
            self.rules[action] = []
            
        # Deduplicate
        for r in self.rules[action]:
            if r.target_id == target_object_id and r.effects == effects:
                # Boost confidence if it already exists
                r.total_matches += 1
                r.successful_matches += 1
                return
                
        rule = TransitionRule(
            effects=effects,
            target_id=target_object_id,
            successful_matches=5, # artificially high prior for hypothesis-driven rules
            total_matches=5
        )
        self.rules[action].append(rule)
        
    def apply_rules(self, state: SceneGraph, action: str) -> SceneGraph:
        """Applies known transition rules to a clone of the state."""
        from perception.object_parser import Object
        
        rules = self.rules.get(action, [])
        if not rules:
            return state
            
        mutated = False
        new_objects = []
        
        for obj in state.objects.values():
            # Find all matching rules for this object
            matching_rules = [r for r in rules if r.matches(obj, state) and r.confidence >= 0.5]
            
            if not matching_rules:
                new_objects.append(obj)
                continue
                
            # Conflict resolution: sort by specificity (desc), then confidence (desc)
            matching_rules.sort(key=lambda r: (r.specificity, r.confidence), reverse=True)
            best_rule = matching_rules[0]
            obj_effects = best_rule.effects
            
            new_color = obj.color
            new_centroid = obj.centroid
            new_bbox = obj.bbox
            new_pixels = obj.pixels
            
            if obj_effects.get("changes_color"):
                new_color = (obj.color + 1) % 10
                mutated = True
                
            if "movement" in obj_effects:
                mv = obj_effects["movement"]
                if isinstance(mv, (list, tuple)) and len(mv) >= 2:
                    dx, dy = mv[0], mv[1]
                    if isinstance(dx, (float, str)) and dx != 'unknown':
                        dx = int(round(float(dx)))
                    if isinstance(dy, (float, str)) and dy != 'unknown':
                        dy = int(round(float(dy)))
                else:
                    dx, dy = 0, 0
                    
                if dx != 'unknown' and dy != 'unknown':
                    new_centroid = (obj.centroid[0] + dx, obj.centroid[1] + dy)
                    min_r, min_c, max_r, max_c = obj.bbox
                    new_bbox = (min_r + dx, min_c + dy, max_r + dx, max_c + dy)
                    new_pixels = [(r + dx, c + dy) for r, c in obj.pixels]
                    mutated = True
                
            if new_color != obj.color or new_centroid != obj.centroid:
                new_objects.append(Object(
                    id=obj.id,
                    color=new_color,
                    pixels=new_pixels,
                    centroid=new_centroid,
                    bbox=new_bbox,
                    area=obj.area,
                    perimeter=obj.perimeter,
                    shape=obj.shape
                ))
            else:
                new_objects.append(obj)
                
        if mutated:
            return SceneGraph(new_objects, state.relations)
        return state
