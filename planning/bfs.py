from typing import List, Callable, Optional
from perception.scene_graph import SceneGraph
from reasoning.goal_generator import Goal
from .planner import Planner, Plan

class BFSPlanner(Planner):
    """Breadth-First Search Planner for shallow, optimal-step plans."""
    
    def plan(self, initial_state: SceneGraph, goal: Goal, available_actions: List[str]) -> Optional[Plan]:
        queue = [(initial_state, [])]
        visited = set()
        visited.add(str(initial_state.objects.keys()))
        
        while queue:
            current_state, path = queue.pop(0)
            
            if self._is_goal_met(current_state, goal, path):
                return Plan(
                    actions=path,
                    estimated_cost=float(len(path)),
                    confidence=0.9, # BFS is complete and optimal for unweighted graphs
                    planner_name="bfs",
                    expected_reward=1.0
                )
                
            for action in available_actions:
                next_state = self.transition_func(current_state, action)
                state_hash = str(next_state.objects.keys())
                
                if state_hash not in visited:
                    visited.add(state_hash)
                    queue.append((next_state, path + [action]))
                    
        return None

    def _is_goal_met(self, state: SceneGraph, goal: Goal, path: List[str]) -> bool:
        target_action = goal.target_conditions.get("action")
        if target_action and path and path[-1] == target_action:
            return True
        return False
