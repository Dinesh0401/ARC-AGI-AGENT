from typing import List, Optional
from .planner import Plan
from .plan_evaluator import ScoredPlan

class ActionSelector:
    """Selects the best Plan from a set of evaluated/scored plans."""
    
    def select_best_plan(self, scored_plans: List[ScoredPlan]) -> Optional[Plan]:
        """Returns the Plan with the highest score."""
        if not scored_plans:
            return None
            
        best_scored_plan = max(scored_plans, key=lambda sp: sp.score)
        return best_scored_plan.plan
