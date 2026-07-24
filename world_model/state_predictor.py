from dataclasses import dataclass, field
from typing import Optional, List
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
    changed_objects: List[str] = field(default_factory=list)
    new_relations: List[str] = field(default_factory=list)

class StatePredictor:
    """Wraps the simulator to provide rich Predictions with confidence metrics."""
    
    def __init__(self, simulator: Simulator, uncertainty_quantifier: UncertaintyQuantifier, transition_model: TransitionModel):
        self.simulator = simulator
        self.uncertainty = uncertainty_quantifier
        self.transition_model = transition_model
        
    def predict(self, current_state: SceneGraph, action: str) -> Prediction:
        predicted_state = self.simulator.simulate_action(current_state, action)
        
        rule_exists = 1 if action in self.transition_model.rules else 0
        uncertainty = self.uncertainty.calculate_uncertainty(action, rule_exists)
        
        confidence = 1.0 - uncertainty
        
        # Calculate diffs
        changed_objects = []
        for obj_id, obj in predicted_state.objects.items():
            curr_obj = current_state.objects.get(obj_id)
            if not curr_obj or curr_obj.color != obj.color: # Simplified comparison for MVP
                changed_objects.append(obj_id)
                
        new_relations = []
        for rel in predicted_state.relations:
            if rel not in current_state.relations:
                new_relations.append(str(rel))
        
        return Prediction(
            predicted_state=predicted_state,
            confidence=confidence,
            uncertainty=uncertainty,
            prediction_error_likelihood=uncertainty,
            changed_objects=changed_objects,
            new_relations=new_relations
        )
