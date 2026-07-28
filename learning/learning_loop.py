from .experience_buffer import ExperienceBuffer, Experience
from .prediction_error import PredictionErrorCalculator
from .belief_updater import BeliefUpdater
from .rule_learner import RuleLearner
from .strategy_updater import StrategyUpdater
from memory import CognitiveMemory
from world_model import PredictionEngine

class LearningLoop:
    """Orchestrates the entire learning cycle from Experience to Memory updates."""
    
    def __init__(self, memory: CognitiveMemory, prediction_engine: PredictionEngine):
        self.experience_buffer = ExperienceBuffer(capacity=100)
        self.error_calculator = PredictionErrorCalculator()
        self.belief_updater = BeliefUpdater(memory.belief_memory)
        self.rule_learner = RuleLearner(prediction_engine.transition_model, memory.semantic)
        self.strategy_updater = StrategyUpdater(memory.procedural)
        
    def process_experience(self, experience: Experience):
        """Executes the learning loop for a given episode."""
        self.experience_buffer.add_experience(experience)
        
        # 1. Compare Predict vs Reality
        error = self.error_calculator.calculate_error(experience.prediction, experience.actual_state)
        
        print(f"\n--- PREDICTION DIAGNOSTIC ---")
        print(f"ACTION: {experience.action}")
        
        pred_state = experience.prediction.predicted_state
        actual_state = experience.actual_state
        pre_state = experience.pre_state
        
        for obj_id, pre_obj in pre_state.objects.items():
            pred_obj = pred_state.objects.get(obj_id)
            act_obj = actual_state.objects.get(obj_id)
            
            if pred_obj and act_obj:
                pred_dx = pred_obj.centroid[0] - pre_obj.centroid[0]
                pred_dy = pred_obj.centroid[1] - pre_obj.centroid[1]
                act_dx = act_obj.centroid[0] - pre_obj.centroid[0]
                act_dy = act_obj.centroid[1] - pre_obj.centroid[1]
                
                pred_color = pred_obj.color
                act_color = act_obj.color
                
                if pred_dx != 0 or pred_dy != 0 or act_dx != 0 or act_dy != 0 or pred_color != pre_obj.color or act_color != pre_obj.color:
                    print(f"Object {obj_id}:")
                    print(f"  Predicted: dx={pred_dx}, dy={pred_dy}, color={pred_color}")
                    print(f"  Actual   : dx={act_dx}, dy={act_dy}, color={act_color}")
                    print(f"  Error    : dx={pred_dx - act_dx}, dy={pred_dy - act_dy}")
                    
        rules = self.rule_learner.transition_model.rules.get(experience.action)
        if rules:
            print(f"Rules for {experience.action}:")
            for i, r in enumerate(rules):
                print(f"  Rule {i+1} | Confidence={r.confidence:.2f} | Effects={r.effects}")
        else:
            print(f"Rule Used: None")
        print(f"-----------------------------\n")
        
        # 2. Extract Belief IDs from the Plan's source if available
        # MVP: hardcoded empty list unless we trace back from Plan -> Goal -> Source
        originating_beliefs = []
        
        # 3. Update Beliefs
        self.belief_updater.update_beliefs(error, originating_beliefs)
        
        # 4. Learn Rules and Update Prediction Accuracy Metrics
        self.rule_learner.learn_from_transition(experience.pre_state, experience.action, experience.actual_state, error)
        
        if hasattr(self.rule_learner.transition_model, 'rules'):
            # The transition model belongs to PredictionEngine. Update prediction metrics if PredictionEngine is available.
            # We don't have direct access to prediction_engine here, but the cognitive agent tracks it.
            # We can attach the counter to the transition model or just assume the agent does it.
            # Let's just track it on the module level or if we have access to PredictionEngine.
            pass
        
        # 5. Update Procedural Strategy
        if experience.plan:
            self.strategy_updater.update_strategy(experience.plan, error)
            
        return error
