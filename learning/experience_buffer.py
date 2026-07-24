from dataclasses import dataclass
from typing import List, Optional
from perception.scene_graph import SceneGraph
from world_model.state_predictor import Prediction
from planning.planner import Plan

@dataclass
class Experience:
    pre_state: SceneGraph
    action: str
    prediction: Prediction
    actual_state: SceneGraph
    plan: Optional[Plan] = None

class ExperienceBuffer:
    """Stores episodic transitions for the learning loop to analyze."""
    
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.buffer: List[Experience] = []
        
    def add_experience(self, exp: Experience):
        self.buffer.append(exp)
        if len(self.buffer) > self.capacity:
            self.buffer.pop(0)
            
    def get_recent(self, count: int = 1) -> List[Experience]:
        return self.buffer[-count:]
