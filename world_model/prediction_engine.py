from typing import List, Tuple
from perception.scene_graph import SceneGraph
from .transition_model import TransitionModel
from .simulator import Simulator
from .uncertainty import UncertaintyQuantifier
from .state_predictor import StatePredictor, Prediction

class PredictionEngine:
    """The entry point for Planners to query the World Model about hypothetical futures."""
    
    def __init__(self):
        self.transition_model = TransitionModel()
        self.simulator = Simulator(self.transition_model)
        self.uncertainty_quantifier = UncertaintyQuantifier()
        self.state_predictor = StatePredictor(self.simulator, self.uncertainty_quantifier, self.transition_model)
        
    def evaluate_action(self, current_state: SceneGraph, action: str) -> Prediction:
        """Evaluate a single action and return the predicted state with confidence metrics."""
        return self.state_predictor.predict(current_state, action)
        
    def rollout_policy(self, current_state: SceneGraph, actions: List[str]) -> Tuple[SceneGraph, float]:
        """Rollout a sequence of actions and return the final predicted state and cumulative confidence."""
        state = current_state
        cumulative_confidence = 1.0
        
        for action in actions:
            prediction = self.evaluate_action(state, action)
            state = prediction.predicted_state
            # Simple joint probability assumption for MVP
            cumulative_confidence *= prediction.confidence
            
        return state, cumulative_confidence
