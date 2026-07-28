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
            
            if self._is_goal_met(current_state, initial_state, goal, path):
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

    def _is_goal_met(self, state: SceneGraph, initial_state: SceneGraph, goal: Goal, path: List[str]) -> bool:
        if goal.target_conditions.get("type") == "VerifyHypothesis":
            target_obj_id = goal.target_conditions.get("target_obj")
            expected_effect = goal.target_conditions.get("expected_effect")
            target_action = goal.target_conditions.get("target_action")
            
            # If the plan executes the exact action we want to test, that's a valid plan.
            if path and path[-1] == target_action:
                return True
                
            # Or if the predicted state shows the effect we wanted
            if target_obj_id in state.objects and target_obj_id in initial_state.objects:
                obj = state.objects[target_obj_id]
                old_obj = initial_state.objects[target_obj_id]
                if expected_effect == "moves" and obj.centroid != old_obj.centroid:
                    return True
                if expected_effect == "changes_color" and obj.color != old_obj.color:
                    return True
        return False
