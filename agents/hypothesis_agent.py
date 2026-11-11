from typing import Any, List
from .multi_agent_system import BaseAgent, Blackboard
from reasoning.hypothesis_engine import HypothesisEngine
from world_model import PredictionEngine
from learning import LearningLoop, Experience

class HypothesisAgent(BaseAgent):
    """Induces logical rules and updates the transition model."""
    
    def __init__(self, blackboard: Blackboard):
        super().__init__("HypothesisAgent", blackboard)
        self.engine = HypothesisEngine()
        self.prediction_engine = PredictionEngine()
        # Initialize learning loop without memory dependency if possible, or pass it later
        
    def run(self) -> None:
        self.blackboard.hypotheses["engine"] = self.engine
        
        last_scene = self.blackboard.observations.get("last_scene")
        current_scene = self.blackboard.observations.get("current_scene")
        last_action = self.blackboard.plans.get("selected_action")
        last_prediction = self.blackboard.predictions.get("predicted_state")
        active_plan = self.blackboard.plans.get("active_plan")
        memory = self.blackboard.memory.get("episodic")
        
        if last_scene is None or last_action is None or memory is None:
            return
            
        # 1. Verify hypotheses against reality
        self.engine.evaluate_action_results(
            str(last_action), current_scene, last_scene, self.prediction_engine.transition_model
        )
        
        # 2. Core learning loop for the world model
        exp = Experience(
            pre_state=last_scene,
            action=last_action,
            prediction=last_prediction,
            actual_state=current_scene,
            plan=active_plan,
        )
        
        # We process the experience to extract rules
        if not hasattr(self, 'learning_loop'):
            # Memory Agent injects memory into blackboard, so we can access it
            mock_memory_wrapper = type('obj', (object,), {'memory': self.blackboard.memory})
            # Wait, LearningLoop takes CognitiveMemory. MemoryAgent has it.
            # I can just pass memory.episodic if LearningLoop doesn't need all.
            pass # We'll recreate learning loop dynamically or pass it.
            # Actually LearningLoop takes full CognitiveMemory. Let's adjust:
        
        # The easiest way is to let HypothesisAgent hold the learning loop, but it needs memory.
        # We'll just manually call prediction_engine.update_from_error
        # since the LearningLoop just delegates to it!
        prediction_error = 1.0
        if last_prediction:
            diff = 0
            for obj_id, obj in current_scene.objects.items():
                if obj_id in last_prediction.objects:
                    pred_obj = last_prediction.objects[obj_id]
                    if pred_obj.centroid != obj.centroid or pred_obj.color != obj.color:
                        diff += 1
            prediction_error = min(1.0, diff / max(1, len(current_scene.objects)))
            
        self.prediction_engine.transition_model.update_from_error(
            str(last_action), prediction_error, current_scene, last_scene
        )
        
        # Write to Blackboard
        self.blackboard.hypotheses["active"] = self.engine.hypotheses
        self.blackboard.hypotheses["verified"] = self.engine.get_verified_hypotheses()
        
        # Extract traces
        rules_added = []
        for r_list in self.prediction_engine.transition_model.rules.values():
            for rule in r_list:
                if rule.total_matches == 1: # Just learned
                    rules_added.append(f"Color {rule.target_color} -> {rule.effects}")
        
        self.blackboard.metrics["hypotheses_generated"] = len(self.engine.hypotheses)
        self.blackboard.metrics["rules_verified"] = len(self.engine.get_verified_hypotheses())
        
        reasoning = [f"Generated {len(self.engine.hypotheses)} hypotheses. Verified {len(self.blackboard.hypotheses['verified'])}."]
        if rules_added:
            reasoning.append(f"Induced new physical rules: {', '.join(rules_added)}.")
            
        self.log_trace(
            action_type="Induction",
            reasoning=reasoning,
            confidence=0.8,
            metrics={"error": prediction_error, "hypotheses": len(self.engine.hypotheses)}
        )
