from perception.scene_graph import SceneGraph
from .transition_model import TransitionModel

class Simulator:
    """Clones a state and applies transition rules to create a hypothetical future."""
    
    def __init__(self, transition_model: TransitionModel):
        self.transition_model = transition_model
        
    def simulate_action(self, current_state: SceneGraph, action: str) -> SceneGraph:
        """Generates a hypothetical future SceneGraph."""
        # The simulator delegates the actual physics to the transition model
        predicted_state = self.transition_model.apply_rules(current_state, action)
        return predicted_state
