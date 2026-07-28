from typing import List, Tuple, Dict
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
        self.cache: Dict[str, Prediction] = {}
        
        self.total_predictions = 0
        self.correct_predictions = 0
        
    def evaluate_action(self, current_state: SceneGraph, action: str) -> Prediction:
        """Evaluate a single action and return the predicted state with confidence metrics."""
        # Simple cache key: (State Hash, Action)
        state_hash = "|".join(sorted(f"{oid}:{obj.color}:{obj.centroid}" for oid, obj in current_state.objects.items())) + "_" + action
        if state_hash in self.cache:
            return self.cache[state_hash]
            
        prediction = self.state_predictor.predict(current_state, action)
        self.cache[state_hash] = prediction
        return prediction
        
    def rollout_policy(self, current_state: SceneGraph, actions: List[str]) -> Tuple[SceneGraph, float]:
        """Rollout a sequence of actions and return the final predicted state and cumulative confidence."""
        state = current_state
        cumulative_confidence = 1.0
        
        for action in actions:
            prediction = self.evaluate_action(state, action)
            state = prediction.predicted_state
            cumulative_confidence *= prediction.confidence
            
        return state, cumulative_confidence
