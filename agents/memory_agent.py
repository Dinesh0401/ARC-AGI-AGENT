from typing import Any
from .multi_agent_system import BaseAgent, Blackboard
from memory import CognitiveMemory
from memory.object_tracker import ObjectTracker
from memory.causal_graph import CausalGraph

class MemoryAgent(BaseAgent):
    """Manages Episodic, Semantic, and Working Memory. Tracks objects over time."""
    
    def __init__(self, blackboard: Blackboard):
        super().__init__("MemoryAgent", blackboard)
        self.memory = CognitiveMemory()
        self.causal_graph = CausalGraph()
        self.object_tracker = ObjectTracker(self.causal_graph)
        
    def reset(self):
        self.memory.clear_episode()
        self.causal_graph = CausalGraph()
        self.object_tracker = ObjectTracker(self.causal_graph)

    def run(self) -> None:
        current_scene = self.blackboard.observations.get("current_scene")
        last_action = self.blackboard.plans.get("selected_action")
        
        if not current_scene:
            return
            
        # 1. Update Object Tracker
        self.object_tracker.track_scene(current_scene, last_action)
        self.blackboard.memory["object_tracker"] = self.object_tracker
        self.blackboard.memory["episodic"] = self.memory.episodic
        self.blackboard.memory["semantic"] = self.memory.knowledge_base
        self.blackboard.memory["working"] = self.memory.working
        
        # Track player visited tiles in episodic memory
        for obj_id, obj in self.object_tracker.tracked_objects.items():
            if obj.is_movable and obj_id in current_scene.objects:
                centroid = current_scene.objects[obj_id].centroid
                self.memory.episodic.visited_tiles.add((int(centroid[0]), int(centroid[1])))
                break
                
        # 2. Update Knowledge Base (Semantic Memory)
        self.memory.knowledge_base.facts.clear()
        for obj in current_scene.objects.values():
            self.memory.knowledge_base.update_fact(
                obj.id,
                {
                    "color": obj.color,
                    "area": obj.area,
                    "shape": obj.shape,
                    "centroid": obj.centroid,
                },
            )
            
        # Update metrics
        self.blackboard.metrics["states_explored"] = len(self.memory.episodic.visit_counts)
        
        self.log_trace(
            action_type="Memory Update",
            reasoning=[
                f"Updated semantic knowledge base with {len(current_scene.objects)} objects.",
                f"Episodic memory tracks {len(self.memory.episodic.visit_counts)} unique states visited."
            ],
            confidence=1.0,
            metrics={"states_explored": self.blackboard.metrics["states_explored"]}
        )
