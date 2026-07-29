from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from perception.scene_graph import SceneGraph

def get_size_bucket(area: int) -> str:
    if area < 5: return "tiny"
    if area < 20: return "small"
    if area < 50: return "medium"
    return "large"

@dataclass
class TransitionRule:
    effects: Dict[str, Any]
    target_color: Optional[int] = None
    target_shape: Optional[str] = None
    target_area: Optional[int] = None
    target_size_bucket: Optional[str] = None
    target_id: Optional[str] = None
    target_relations: List[tuple] = field(default_factory=list)
    required_adjacent_colors: Optional[set] = None
    
    successful_matches: int = 0
    total_matches: int = 0
    cumulative_error: float = 0.0
    
    @property
    def confidence(self) -> float:
        if self.total_matches == 0:
            return 0.5
        success_ratio = self.successful_matches / self.total_matches
        # Heavy penalty for large coordinate errors (0.1 per pixel error)
        return max(0.0, success_ratio - (self.cumulative_error * 0.1))
        
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
        if self.required_adjacent_colors:
            current_adj_colors = set()
            for source_id, rel_type, target in state.relations:
                if rel_type == "adjacent":
                    if source_id == obj.id:
                        current_adj_colors.add(state.objects[target].color)
                    elif target == obj.id:
                        current_adj_colors.add(state.objects[source_id].color)
            if not self.required_adjacent_colors.issubset(current_adj_colors):
                return False
                
        return True

    def match_score(self, obj) -> int:
        """Returns a score indicating how well the soft constraints match."""
        score = 0
        if self.target_shape is not None:
            if self.target_shape == obj.shape: score += 1
            else: score -= 1
        if self.target_area is not None:
            if self.target_area == obj.area: score += 1
            else: score -= 1
        if self.target_size_bucket is not None:
            if self.target_size_bucket == get_size_bucket(obj.area): score += 1
            else: score -= 1
        return score


class TransitionModel:
    """Stores and evaluates the dynamic rules of the environment."""
    
    def __init__(self):
        # Mapping from action -> list of TransitionRule
        self.rules: Dict[str, List[TransitionRule]] = {}
        # Statistics for each color: {'blocked': int, 'passed': int}
        self.collision_stats: Dict[int, Dict[str, int]] = {}
        
    def is_solid(self, color: int) -> bool:
        stats = self.collision_stats.get(color)
        if not stats: return False
        total = stats['blocked'] + stats['passed']
        if total < 2: return False
        return (stats['blocked'] / total) > 0.8
        
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
                                
                                # Penalize rule heavily if the predicted movement doesn't match reality
                                coord_error = abs(dx - mv[0]) + abs(dy - mv[1])
                                rule.cumulative_error += coord_error
                                
                                if abs(dx - mv[0]) > 0.8 or abs(dy - mv[1]) > 0.8:
                                    if abs(dx) <= 0.8 and abs(dy) <= 0.8:
                                        # It didn't move. Was it blocked?
                                        blocked = False
                                        shifted_pixels = {(r + mv[0], c + mv[1]) for r, c in old_obj.pixels}
                                        for other_id, other_obj in pre_state.objects.items():
                                            if other_id != obj_id:
                                                other_pixels = set(other_obj.pixels)
                                                if shifted_pixels & other_pixels:
                                                    blocked = True
                                                    if other_obj.color not in self.collision_stats:
                                                        self.collision_stats[other_obj.color] = {'blocked': 0, 'passed': 0}
                                                    self.collision_stats[other_obj.color]['blocked'] += 1
                                                    break
                                        if blocked:
                                            # It was blocked, so the physical intent was correct. Don't penalize.
                                            succeeded = True
                                        else:
                                            succeeded = False
                                    else:
                                        succeeded = False
                        
                        # Record 'passed' stats for movement that succeeded
                        if "movement" in rule.effects and succeeded and (abs(dx) > 0.8 or abs(dy) > 0.8):
                            actual_pixels = {(r + dx, c + dy) for r, c in old_obj.pixels}
                            for other_id, other_obj in pre_state.objects.items():
                                if other_id != obj_id:
                                    if actual_pixels & set(other_obj.pixels):
                                        if other_obj.color not in self.collision_stats:
                                            self.collision_stats[other_obj.color] = {'blocked': 0, 'passed': 0}
                                        self.collision_stats[other_obj.color]['passed'] += 1
                                        
                        if succeeded:
                            rule.successful_matches += 1
                            if rule.required_adjacent_colors is not None:
                                current_adj_colors = set()
                                for source_id, rel_type, target in pre_state.relations:
                                    if rel_type == "adjacent":
                                        if source_id == obj_id:
                                            current_adj_colors.add(pre_state.objects[target].color)
                                        elif target == obj_id:
                                            current_adj_colors.add(pre_state.objects[source_id].color)
                                rule.required_adjacent_colors &= current_adj_colors
                            
                            
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
                    
                    # Strict movement quantization to prevent tracker noise explosion
                    dx_float = current_obj.centroid[0] - old_obj.centroid[0]
                    dy_float = current_obj.centroid[1] - old_obj.centroid[1]
                    if abs(dx_float) > 0.8 or abs(dy_float) > 0.8:
                        dx = int(round(dx_float))
                        dy = int(round(dy_float))
                        
                        if dx != 0 or dy != 0:
                            obj_effects["movement"] = (dx, dy)
                            
                        # Detect shape change (often causes non-integer centroid shifts)
                        if len(old_obj.pixels) != len(current_obj.pixels) or old_obj.shape != current_obj.shape:
                            obj_effects["changes_shape"] = True
                    
                    if obj_effects:
                        if list(obj_effects.keys()) == ["changes_shape"]:
                            continue # Ignore rules that only change shape since apply_rules doesn't implement shape changing
                            
                        # Do NOT extract relations or adjacent colors for preconditions. 
                        # Overfitting to spatial relations causes rules to break as soon as objects move.
                        safe_rels = []
                        adj_colors = None
                                
                        new_rule = TransitionRule(
                            effects=obj_effects,
                            target_color=old_obj.color,
                            target_shape=old_obj.shape,
                            target_area=old_obj.area,
                            target_size_bucket=get_size_bucket(old_obj.area),
                            target_relations=safe_rels,
                            required_adjacent_colors=adj_colors,
                            successful_matches=1,
                            total_matches=1
                        )
                        
                        # Check if similar rule exists and merge if so
                        exists = False
                        for r in self.rules[action]:
                            if (r.target_color == new_rule.target_color and 
                                r.target_size_bucket == new_rule.target_size_bucket and 
                                r.effects == new_rule.effects):
                                # Merge evidence!
                                r.total_matches += 1
                                r.successful_matches += 1
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
            # Find all matching rules for this object. Soft constraints must not be strongly negative.
            matching_rules = [r for r in rules if r.matches(obj, state) and r.confidence >= 0.5 and r.match_score(obj) >= 0]
            
            if not matching_rules:
                new_objects.append(obj)
                continue
                
            # Conflict resolution: sort by specificity (desc), then match_score (desc), then confidence (desc)
            matching_rules.sort(key=lambda r: (r.specificity, r.match_score(obj), r.confidence), reverse=True)
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
                    shifted_pixels = {(r + dx, c + dy) for r, c in obj.pixels}
                    blocked = False
                    for other_obj in state.objects.values():
                        if other_obj.id != obj.id and self.is_solid(other_obj.color):
                            if shifted_pixels & set(other_obj.pixels):
                                blocked = True
                                break
                    
                    if blocked:
                        # Collision prevented movement
                        pass
                    else:
                        new_centroid = (obj.centroid[0] + dx, obj.centroid[1] + dy)
                        min_r, min_c, max_r, max_c = obj.bbox
                        new_bbox = (min_r + dx, min_c + dy, max_r + dx, max_c + dy)
                        new_pixels = list(shifted_pixels)
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
