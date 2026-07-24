from typing import Dict, Any
from perception.scene_graph import SceneGraph
from reasoning.goal_generator import Goal

def evaluate_cost(action: str, current_state: SceneGraph) -> float:
    """Calculate the step cost g(n) for applying an action."""
    # MVP: All actions cost 1
    return 1.0

def heuristic_distance(current_state: SceneGraph, goal: Goal) -> float:
    """Calculate heuristic h(n) estimating cost from current state to Goal."""
    # Find how many target conditions are not met
    unmet_conditions = 0
    target_conditions = goal.target_conditions
    
    if target_conditions.get("action"):
        # For an action goal, heuristic is just 1 if not done, 0 if done.
        # Since this is a state heuristic, an action goal is slightly awkward
        # until the action is appended. Let's assume h=1 if not met.
        unmet_conditions += 1
        
    return float(unmet_conditions)
