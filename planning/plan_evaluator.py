from dataclasses import dataclass
from typing import List, Optional
from .planner import Plan

@dataclass
class ScoredPlan:
    plan: Plan
    score: float

class PlanEvaluator:
    """Scores a proposed Plan based on risk, cost, and confidence."""
    
    def evaluate(self, plan: Plan) -> ScoredPlan:
        # Simple weighted combination
        # Higher score is better
        # Weights:
        # Confidence: highly valued
        # Expected Reward: highly valued
        # Estimated Cost: penalty
        
        cost_penalty = plan.estimated_cost * 0.1
        score = (plan.confidence * 2.0) + (plan.expected_reward * 1.5) - cost_penalty
        
        return ScoredPlan(plan=plan, score=score)
