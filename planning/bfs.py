from typing import List, Callable, Optional
from perception.scene_graph import SceneGraph
from reasoning.goal_generator import Goal
from .planner import Planner, Plan

class BFSPlanner(Planner):
    """Breadth-First Search Planner for shallow, optimal-step plans."""
    
    def __init__(self, transition_func, max_depth: int = 3, max_nodes: int = 50):
        super().__init__(transition_func)
        self.max_depth = max_depth
        self.max_nodes = max_nodes
    
    def plan(self, initial_state: SceneGraph, goal: Goal, available_actions: List[str]) -> Optional[Plan]:
        queue = [(initial_state, [])]
        visited = set()
        visited.add(self._state_hash(initial_state))
        nodes_explored = 0
        
        while queue:
            current_state, path = queue.pop(0)
            nodes_explored += 1
            
            if self._is_goal_met(current_state, goal, path):
                return Plan(
                    actions=path,
                    estimated_cost=float(len(path)),
                    confidence=0.9,
                    planner_name="bfs",
                    expected_reward=1.0
                )

            # Enforce depth and node limits
            if len(path) >= self.max_depth or nodes_explored >= self.max_nodes:
                continue
                
            for action in available_actions:
                next_state = self.transition_func(current_state, action)
                state_hash = self._state_hash(next_state)
                
                if state_hash not in visited:
                    visited.add(state_hash)
                    queue.append((next_state, path + [action]))
                    
        return None

    @staticmethod
    def _state_hash(state: SceneGraph) -> str:
        parts = sorted(f"{oid}:{obj.color}" for oid, obj in state.objects.items())
        return "|".join(parts)

    def _is_goal_met(self, state: SceneGraph, goal: Goal, path: List[str]) -> bool:
        target_action = goal.target_conditions.get("action")
        if target_action and path and path[-1] == target_action:
            return True
        return False
