from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from memory.working import WorkingMemory
from reasoning.hypothesis_engine import HypothesisEngine, HypothesisStatus

@dataclass
class Goal:
    """An objective for the planner. In Phase D, this is primarily to test a hypothesis."""
    description: str
    target_conditions: Dict[str, Any]
    priority: int
    confidence: float
    source: str
    deadline: Optional[int] = None
    hypothesis_id: Optional[str] = None
    
class GoalGenerator:
    """Infers testable hypotheses and generates goals to verify them."""
    
    def __init__(self, working_memory: WorkingMemory, hypothesis_engine: HypothesisEngine):
        self.working = working_memory
        self.hypothesis_engine = hypothesis_engine
        
    def generate_goals(self, current_scene: 'SceneGraph', object_tracker: 'ObjectTracker') -> List[Goal]:
        """Produce goals to verify the most promising active hypotheses."""
        goals = []
        
        # 1. Generate new hypotheses based on object tracker state
        if current_scene and object_tracker:
            for obj_id, tracked_obj in object_tracker.tracked_objects.items():
                if len(tracked_obj.interaction_history) == 0:
                    # Untested object - aggressively seed hypotheses to ensure exploration
                    for action in ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]:
                        desc = f"IF {action} THEN {obj_id} moves"
                        self.hypothesis_engine.add_hypothesis(
                            description=desc,
                            target_object_id=obj_id,
                            action=action,
                            expected_effect="moves",
                            initial_confidence=0.5
                        )
                
                elif tracked_obj.is_movable:
                    for action in ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]:
                        desc = f"IF {action} THEN {obj_id} moves"
                        self.hypothesis_engine.add_hypothesis(
                            description=desc,
                            target_object_id=obj_id,
                            action=action,
                            expected_effect="moves",
                            initial_confidence=0.7
                        )

        # 2. Goal Discovery Module
        player_id = None
        for obj_id, obj in object_tracker.tracked_objects.items():
            if obj.is_movable:
                player_id = obj_id
                break
                
        if current_scene and object_tracker:
            for obj_id, tracked_obj in object_tracker.tracked_objects.items():
                if obj_id == player_id:
                    continue
                    
                # Calculate object importance
                importance = len(tracked_obj.interaction_history) + tracked_obj.state_changes * 2
                
                # Bonus importance for unique colored objects (e.g. key, door, target)
                color_counts = {}
                for other_obj in current_scene.objects.values():
                    color_counts[other_obj.color] = color_counts.get(other_obj.color, 0) + 1
                    
                if obj_id in current_scene.objects:
                    obj_color = current_scene.objects[obj_id].color
                    if color_counts.get(obj_color, 0) == 1:
                        importance += 10  # Unique objects are highly important
                        
                if importance > 0 or len(tracked_obj.interaction_history) == 0:
                    goals.append(Goal(
                        description=f"Interact with {obj_id}",
                        target_conditions={"type": "Reach", "target_id": obj_id},
                        priority=int(importance * 10),
                        confidence=1.0,
                        source="GoalGenerator"
                    ))
                    
        # Emit a fallback explore goal
        goals.append(Goal(
            description="Explore unseen tiles",
            target_conditions={"type": "Explore"},
            priority=5,
            confidence=1.0,
            source="GoalGenerator"
        ))
        
        # 3. Check Working Memory thoughts for overriding tasks
        thoughts = self.working.get_thoughts()
        for thought in thoughts:
            if "Need to" in thought.text:
                goals.append(Goal(
                    description=thought.text,
                    target_conditions={"type": "Task", "target": thought.text},
                    priority=thought.priority,
                    confidence=1.0,
                    source="WorkingMemory"
                ))
                
        # Sort goals by priority
        goals.sort(key=lambda g: g.priority, reverse=True)
        return goals
