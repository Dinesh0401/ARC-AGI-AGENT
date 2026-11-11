from typing import Any, Dict, List
from .multi_agent_system import BaseAgent, Blackboard
from perception.object_parser import ObjectParser

class PerceptionAgent(BaseAgent):
    """Processes raw grid frames and detects objects and relations."""
    
    def __init__(self, blackboard: Blackboard):
        super().__init__("PerceptionAgent", blackboard)
        from integration.arc_adapter import FrameParser
        self.parser = FrameParser()
        
    def run(self) -> None:
        latest_frame = self.blackboard.observations.get("latest_frame")
        if not latest_frame:
            return
            
        current_scene = self.parser.parse(latest_frame)
        self.blackboard.observations["current_scene"] = current_scene
        self.blackboard.observations["available_actions"] = latest_frame.get("available_actions", [])
        
        num_objects = len(current_scene.objects)
        player_obj = next((obj for obj in current_scene.objects.values() if getattr(obj, 'movable', False)), None)
        player_pos = player_obj.centroid if player_obj else "Unknown"
        
        self.log_trace(
            action_type="Observe",
            reasoning=[
                f"Parsed frame into {num_objects} objects.",
                f"Identified player at {player_pos}."
            ],
            confidence=1.0,
            metrics={"num_objects": num_objects}
        )
