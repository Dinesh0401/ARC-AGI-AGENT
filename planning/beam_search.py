import logging
from typing import List, Callable, Optional
from perception.scene_graph import SceneGraph
from reasoning.goal_generator import Goal
from reasoning.value_function import ValueFunction
from .planner import Planner, Plan

class BeamSearchPlanner(Planner):
    """Beam Search planner for deep multi-step rollouts maximizing a Value Function."""
    
    def __init__(self, transition_func: Callable, value_function: ValueFunction, beam_width: int = 3, max_depth: int = 10):
        super().__init__(transition_func)
        self.value_function = value_function
        self.beam_width = beam_width
        self.max_depth = max_depth
        
    def plan(self, initial_state: SceneGraph, goal: Goal, available_actions: List[str]) -> Optional[Plan]:
        if not available_actions:
            return None
            
        initial_score = self.value_function.evaluate_state(initial_state, [], initial_state)
        # Beam contains tuples of (score, state, path)
        beam = [(initial_score, initial_state, [])]
        best_path = []
        best_score = float('-inf')
        
        expanded_nodes = 0
        unique_states_by_depth = {}
        duplicate_states_by_depth = {}
        
        for depth in range(self.max_depth):
            candidates = []
            unique_hashes = set()
            depth_expanded = 0
            
            for score, state, path in beam:
                for action in available_actions:
                    next_state = self.transition_func(state, action)
                    new_path = path + [action]
                    expanded_nodes += 1
                    depth_expanded += 1
                    
                    # Evaluate rollout
                    new_score = self.value_function.evaluate_state(next_state, new_path, initial_state)
                    
                    pred_hash = "|".join(sorted(f"{oid}:{obj.color}:{obj.centroid}" for oid, obj in next_state.objects.items()))
                    unique_hashes.add(pred_hash)
                    
                    if new_score > best_score:
                        best_score = new_score
                        best_path = new_path
                        
                    candidates.append((new_score, next_state, new_path))
                    
            unique_count = len(unique_hashes)
            unique_states_by_depth[depth + 1] = unique_count
            duplicate_states_by_depth[depth + 1] = depth_expanded - unique_count
            
            logging.info(f"Depth {depth + 1} | Expanded Nodes: {depth_expanded} | Unique States: {unique_count} | Duplicate States: {depth_expanded - unique_count}")
                    
            if not candidates:
                break
                
            # Sort candidates by score descending and take top K
            candidates.sort(key=lambda x: x[0], reverse=True)
            beam = candidates[:self.beam_width]
            
        if not best_path:
            import random
            best_path = [random.choice(available_actions)]
            
        confidence = 0.85 if best_score > initial_score else 0.4
        logging.info(f"Beam Search selected path {best_path} with score {best_score:.2f} (Confidence: {confidence})")
            
        return Plan(
            actions=best_path,
            estimated_cost=float(len(best_path)),
            confidence=confidence,
            planner_name="beam_search",
            expected_reward=best_score,
            metrics={
                "expanded_nodes": expanded_nodes, 
                "unique_states_by_depth": unique_states_by_depth,
                "duplicate_states_by_depth": duplicate_states_by_depth
            }
        )
