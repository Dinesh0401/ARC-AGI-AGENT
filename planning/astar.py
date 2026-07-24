import heapq
from typing import List, Callable, Optional
from perception.scene_graph import SceneGraph
from reasoning.goal_generator import Goal
from .path_cost import evaluate_cost, heuristic_distance
from .planner import Planner, Plan

class AStarPlanner(Planner):
    """A* Search using h(n) estimating distance to Goal."""
    
    def plan(self, initial_state: SceneGraph, goal: Goal, available_actions: List[str]) -> Optional[Plan]:
        initial_hash = str(initial_state.objects.keys())
        pq = [(0 + heuristic_distance(initial_state, goal), 0, [], initial_hash, initial_state)]
        visited = set()
        
        while pq:
            f_score, g_score, path, state_hash, current_state = heapq.heappop(pq)
            
            if self._is_goal_met(current_state, goal, path):
                return Plan(
                    actions=path,
                    estimated_cost=g_score,
                    confidence=0.95,
                    planner_name="astar",
                    expected_reward=1.0
                )
                
            if state_hash in visited:
                continue
            visited.add(state_hash)
            
            for action in available_actions:
                next_state = self.transition_func(current_state, action)
                next_hash = str(next_state.objects.keys())
                
                if next_hash not in visited:
                    new_g = g_score + evaluate_cost(action, current_state)
                    new_h = heuristic_distance(next_state, goal)
                    heapq.heappush(pq, (new_g + new_h, new_g, path + [action], next_hash, next_state))
                    
        return None

    def _is_goal_met(self, state: SceneGraph, goal: Goal, path: List[str]) -> bool:
        target_action = goal.target_conditions.get("action")
        if target_action and path and path[-1] == target_action:
            return True
        return False
