import heapq
from typing import List, Callable, Optional
from perception.scene_graph import SceneGraph
from reasoning.goal_generator import Goal
from .path_cost import evaluate_cost, heuristic_distance
from .planner import Planner, Plan

class AStarPlanner(Planner):
    """A* Search using h(n) estimating distance to Goal."""
    
    def __init__(self, transition_func, max_depth: int = 3, max_nodes: int = 50):
        super().__init__(transition_func)
        self.max_depth = max_depth
        self.max_nodes = max_nodes
    
    def plan(self, initial_state: SceneGraph, goal: Goal, available_actions: List[str]) -> Optional[Plan]:
        initial_hash = self._state_hash(initial_state)
        pq = [(0 + heuristic_distance(initial_state, goal), 0, [], initial_hash, initial_state)]
        visited = set()
        nodes_explored = 0
        
        while pq:
            f_score, g_score, path, state_hash, current_state = heapq.heappop(pq)
            nodes_explored += 1
            
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

            # Enforce depth and node limits
            if len(path) >= self.max_depth or nodes_explored >= self.max_nodes:
                continue
            
            for action in available_actions:
                next_state = self.transition_func(current_state, action)
                next_hash = self._state_hash(next_state)
                
                if next_hash not in visited:
                    new_g = g_score + evaluate_cost(action, current_state)
                    new_h = heuristic_distance(next_state, goal)
                    heapq.heappush(pq, (new_g + new_h, new_g, path + [action], next_hash, next_state))
                    
        return None

    @staticmethod
    def _state_hash(state: SceneGraph) -> str:
        parts = sorted(f"{oid}:{obj.color}:{obj.centroid}" for oid, obj in state.objects.items())
        return "|".join(parts)

    def _is_goal_met(self, state: SceneGraph, goal: Goal, path: List[str]) -> bool:
        # Generic fallback for ARC: we don't have explicit goal states yet
        # Returning False ensures A* explores fully, but we need it to return the best path eventually.
        # This will require larger refactoring to make A* return partial plans like Beam Search.
        target_action = goal.target_conditions.get("action")
        if target_action and path and path[-1] == target_action:
            return True
        return False
