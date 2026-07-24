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
        
        # 2. Extract Belief IDs from the Plan's source if available
        # MVP: hardcoded empty list unless we trace back from Plan -> Goal -> Source
        originating_beliefs = []
        
        # 3. Update Beliefs
        self.belief_updater.update_beliefs(error, originating_beliefs)
        
        # 4. Learn Rules
        self.rule_learner.learn_from_transition(experience.pre_state, experience.action, experience.actual_state)
        
        # 5. Update Procedural Strategy
        if experience.plan:
            self.strategy_updater.update_strategy(experience.plan, error)
            
        return error
