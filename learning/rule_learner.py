from world_model.transition_model import TransitionModel
from memory.semantic import SemanticMemory
from perception.scene_graph import SceneGraph

class RuleLearner:
    """Learns rules by observing what ACTUALLY changed vs what was predicted."""
    
    def __init__(self, transition_model: TransitionModel, semantic_memory: SemanticMemory):
        self.transition_model = transition_model
        self.semantic = semantic_memory
        
    def learn_from_transition(self, pre_state: SceneGraph, action: str, actual_post_state: SceneGraph, prediction_error: float):
        """
        Updates the transition model with the observed error.
        """
        self.transition_model.update_from_error(action, prediction_error, actual_post_state, pre_state)
