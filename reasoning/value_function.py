from typing import List, Optional
from perception.scene_graph import SceneGraph
from reasoning.hypothesis_engine import HypothesisEngine
from memory.episodic import EpisodicMemory

class ValueFunction:
    """Evaluates the 'value' of a SceneGraph state based on Goal Progress and Info Gain."""
    
    def __init__(self, episodic_memory: EpisodicMemory, hypothesis_engine: HypothesisEngine):
        self.memory = episodic_memory
        self.hypothesis_engine = hypothesis_engine
        
    def evaluate_state(self, predicted_state: SceneGraph, action_path: List[str], current_state: SceneGraph) -> float:
        """
        Evaluate the predicted state using:
        score = goal_progress*5 + info_gain*2 + novelty*1 - loop_penalty*3 + object_interaction*0.5
        """
        # 1. Goal Progress
        goal_progress = self.compute_goal_progress(predicted_state)
        
        # 2. Information Gain
        info_gain = 0.0
        if action_path:
            last_action = action_path[-1]
            for hyp in self.hypothesis_engine.get_hypotheses_for_action(last_action):
                variance = hyp.confidence * (1.0 - hyp.confidence)
                info_gain += variance * 4.0
                
        # 3. Loop Penalty
        loop_penalty = 0.0
        recent_hashes = self.memory.get_recent_states(limit=5)
        pred_hash = "|".join(sorted(f"{oid}:{obj.color}:{obj.centroid}" for oid, obj in predicted_state.objects.items()))
        if pred_hash in recent_hashes:
            loop_penalty += 1.0 # Will be multiplied by weight
            
        # Detect opposite actions in the hypothetical path (e.g. ACTION1 then ACTION2)
        opposites = {"ACTION1": "ACTION2", "ACTION2": "ACTION1", "ACTION3": "ACTION4", "ACTION4": "ACTION3"}
        if len(action_path) >= 2:
            for i in range(len(action_path) - 1):
                if opposites.get(action_path[i]) == action_path[i+1]:
                    loop_penalty += 2.0
            
        # 4. Novelty
        visit_count = self.memory.get_visit_count(predicted_state)
        novelty = 1.0 / (visit_count + 1)
        
        # 5. Object Interaction
        # Did the state change from the original state?
        object_interaction = 0.0
        orig_hash = "|".join(sorted(f"{oid}:{obj.color}:{obj.centroid}" for oid, obj in current_state.objects.items()))
        if pred_hash != orig_hash:
            object_interaction = 1.0
            
        score = (
            goal_progress * 5.0
            + info_gain * 2.0
            + novelty * 1.0
            - loop_penalty * 3.0
            + object_interaction * 0.5
        )
        
        return score

    def compute_goal_progress(self, state: SceneGraph) -> float:
        """Heuristic for ARC-AGI: reward states with aligned objects or fewer objects (simplification)."""
        import math
        progress = 0.0
        objects = list(state.objects.values())
        if len(objects) > 1:
            total_dist = 0
            pairs = 0
            for i in range(len(objects)):
                for j in range(i+1, len(objects)):
                    c1 = objects[i].centroid
                    c2 = objects[j].centroid
                    dist = abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) # Manhattan
                    total_dist += dist
                    pairs += 1
            if pairs > 0:
                avg_dist = total_dist / pairs
                # Use exponential decay so that score is always positive [0, 1]
                progress += math.exp(-avg_dist * 0.1)
        return progress
