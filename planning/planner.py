from dataclasses import dataclass, field
from typing import List, Callable, Optional, Dict, Any
from perception.scene_graph import SceneGraph
from reasoning.goal_generator import Goal
import abc

@dataclass
class Plan:
    """Encapsulates a proposed action sequence and its evaluation metrics."""
    actions: List[str]
    estimated_cost: float
    confidence: float
    planner_name: str
    expected_reward: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)

class Planner(abc.ABC):
    """Abstract base class for all search algorithms."""
    
    def __init__(self, transition_func: Callable):
        self.transition_func = transition_func
        
    @abc.abstractmethod
    def plan(self, initial_state: SceneGraph, goal: Goal, available_actions: List[str]) -> Optional[Plan]:
        pass

# The PlanningOrchestrator needs the actual planners, so we import them here
# but to avoid circular imports, we might need to structure this carefully.
# We will do local imports inside generate_plan for the orchestrator, or 
# assume they are imported from __init__.

class PlanningOrchestrator:
    """Coordinates search algorithms to find a valid action sequence for a Goal."""
    
    def __init__(self, transition_func: Callable, value_function: 'ValueFunction' = None):
        self.transition_func = transition_func
        self.value_function = value_function
        
        # We will lazy-load the planners to avoid circular imports if needed,
        # but since they inherit from Planner, it's fine to import them directly
        # if structured correctly. For now we will import at the top in the real module.
        from .bfs import BFSPlanner
        from .astar import AStarPlanner
        from .mcts import MCTSPlanner
        from .beam_search import BeamSearchPlanner
        from .action_selector import ActionSelector
        from .plan_evaluator import PlanEvaluator
        
        self.planners: Dict[str, Planner] = {}
        
        # If we have a value function, we can use Beam Search
        if value_function:
            self.planners["beam_search"] = BeamSearchPlanner(transition_func, value_function)
        else:
            self.planners["bfs"] = BFSPlanner(transition_func)
            self.planners["astar"] = AStarPlanner(transition_func)
            self.planners["mcts"] = MCTSPlanner(transition_func)
            
        self.evaluator = PlanEvaluator()
        self.selector = ActionSelector()
        
    def generate_plan(self, initial_state: SceneGraph, goal: Goal, available_actions: List[str]) -> Optional[Plan]:
        """Run planners and select the best sequence of actions."""
        candidate_plans = []
        
        for name, planner in self.planners.items():
            plan = planner.plan(initial_state, goal, available_actions)
            if plan and plan.actions:
                candidate_plans.append(plan)
                
        if not candidate_plans:
            return None
            
        scored_plans = [self.evaluator.evaluate(plan) for plan in candidate_plans]
        return self.selector.select_best_plan(scored_plans)
