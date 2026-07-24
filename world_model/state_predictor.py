from dataclasses import dataclass
from typing import Optional
from perception.scene_graph import SceneGraph
from .simulator import Simulator
from .uncertainty import UncertaintyQuantifier
from .transition_model import TransitionModel

@dataclass
class Prediction:
    predicted_state: SceneGraph
    confidence: float
    uncertainty: float
    prediction_error_likelihood: float

class StatePredictor:
    """Wraps the simulator to provide rich Predictions with confidence metrics."""
    
    def __init__(self, simulator: Simulator, uncertainty_quantifier: UncertaintyQuantifier, transition_model: TransitionModel):
        self.simulator = simulator
        self.uncertainty = uncertainty_quantifier
        self.transition_model = transition_model
        
    def predict(self, current_state: SceneGraph, action: str) -> Prediction:
        predicted_state = self.simulator.simulate_action(current_state, action)
        
        # Calculate uncertainty based on how many rules we have for this action
        rule_exists = 1 if action in self.transition_model.rules else 0
        uncertainty = self.uncertainty.calculate_uncertainty(action, rule_exists)
        
        confidence = 1.0 - uncertainty
        
        return Prediction(
            predicted_state=predicted_state,
            confidence=confidence,
            uncertainty=uncertainty,
            prediction_error_likelihood=uncertainty # Highly uncertain predictions are likely to have high errors
        )
