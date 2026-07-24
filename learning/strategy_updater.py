from memory.procedural import ProceduralMemory
from planning.planner import Plan

class StrategyUpdater:
    """Updates Procedural Memory strategies based on execution outcomes."""
    
    def __init__(self, procedural_memory: ProceduralMemory):
        self.procedural = procedural_memory
        
    def update_strategy(self, plan: Plan, prediction_error: float):
        """If error is low, the plan succeeded as intended and should be reinforced."""
        outcome = "Success" if prediction_error < 0.2 else "Failed"
        
        # We dummy-construct the situation context for MVP
        self.procedural.add_strategy(
            situation={"context": "unknown"}, 
            strategy=plan.actions,
            outcome=outcome,
            efficiency=plan.estimated_cost,
            confidence=1.0 - prediction_error
        )
