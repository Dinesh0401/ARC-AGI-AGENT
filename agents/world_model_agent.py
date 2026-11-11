from typing import Any
from .multi_agent_system import BaseAgent, Blackboard
from world_model import PredictionEngine

class WorldModelAgent(BaseAgent):
    """Predicts future states based on current state and induced physical rules."""
    
    def __init__(self, blackboard: Blackboard):
        super().__init__("WorldModelAgent", blackboard)
        self.prediction_engine = PredictionEngine()
        self.blackboard.predictions["engine"] = self.prediction_engine
        
    def run(self) -> None:
        # Read from Blackboard
        current_scene = self.blackboard.observations["current_scene"]
        available_actions = self.blackboard.observations["available_actions"]
        banned = self.blackboard.plans.get("banned_actions", set())
        
        valid_actions = [a for a in available_actions if isinstance(a, str) and a != "RESET" and a not in banned]
        if not valid_actions:
            valid_actions = ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]
            
        # Write to Blackboard
        # Just evaluating a representative action to prove model functionality
        if current_scene and valid_actions:
            test_action = valid_actions[0]
            prediction = self.prediction_engine.evaluate_action(current_scene, test_action)
            self.blackboard.predictions["predicted_state"] = prediction.predicted_state
            
            reasoning = [
                f"Evaluated physical simulation for candidate action: {test_action}",
                f"Predicted state contains {len(prediction.predicted_state.objects)} objects"
            ]
            self.log_trace(
                action_type="Predict",
                reasoning=reasoning,
                confidence=0.85
            )
