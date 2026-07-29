from typing import List, Optional
from perception.scene_graph import SceneGraph
from reasoning.hypothesis_engine import HypothesisEngine
from memory.episodic import EpisodicMemory

class ValueFunction:
    """Evaluates the 'value' of a SceneGraph state based on Goal Progress and Info Gain."""
    
    def __init__(self, episodic_memory: EpisodicMemory, hypothesis_engine: HypothesisEngine):
        self.memory = episodic_memory
        self.hypothesis_engine = hypothesis_engine
        
    def evaluate_state(self, predicted_state: SceneGraph, action_path: List[str], current_state: SceneGraph, goal: Optional['Goal'] = None) -> float:
        """
        Evaluate the predicted state using:
        score = goal_progress + exploration_reward - loop_penalty
        """
        # 1. Goal Progress
        goal_progress = self.compute_goal_progress(predicted_state, goal)
        
        # 2. Information Gain
        info_gain = 0.0
        if action_path:
            last_action = action_path[-1]
            for hyp in self.hypothesis_engine.get_hypotheses_for_action(last_action):
                variance = hyp.confidence * (1.0 - hyp.confidence)
                info_gain += variance * 4.0
                
        # 3. Loop Penalty & Novelty (State Hash)
        visit_count = self.memory.get_visit_count(predicted_state)
        
        loop_penalty = 0.0
        # If we've visited this exact state before (e.g. oscillating), massive penalty
        if visit_count > 0:
            loop_penalty += 500.0 * visit_count
            
        recent_hashes = self.memory.get_recent_states(limit=5)
        pixel_tuples = []
        for obj in predicted_state.objects.values():
            pixel_tuples.append(f"{obj.color}:{tuple(sorted(obj.pixels))}")
        pred_hash = str(hash(tuple(sorted(pixel_tuples))))
        if pred_hash in recent_hashes:
            loop_penalty += 500.0
            
        # Detect opposite actions in the hypothetical path
        opposites = {"ACTION1": "ACTION2", "ACTION2": "ACTION1", "ACTION3": "ACTION4", "ACTION4": "ACTION3"}
        if len(action_path) >= 2:
            for i in range(len(action_path) - 1):
                if opposites.get(action_path[i]) == action_path[i+1]:
                    loop_penalty += 200.0
                    
        # 4. Position Tracking (Exploration Reward & Penalty)
        exploration_reward = 0.0
        # Find player position in predicted state
        player_pos = None
        player_id = None
        for obj_id, obj in predicted_state.objects.items():
            # Heuristic: the movable object is the player
            # If tracking isn't passed down, we assume color 12 or just check if it moved relative to current
            if obj_id in current_state.objects:
                if current_state.objects[obj_id].centroid != obj.centroid:
                    player_pos = (int(obj.centroid[0]), int(obj.centroid[1]))
                    player_id = obj_id
                    break
                    
        if player_pos:
            if player_pos in self.memory.visited_tiles:
                loop_penalty += 100.0
            else:
                exploration_reward += 50.0  # Reward for reaching a new tile
                
        # 5. Object Interaction (Only reward if state is novel!)
        object_interaction = 0.0
        if visit_count == 0:
            for obj_id, current_obj in predicted_state.objects.items():
                if obj_id in current_state.objects:
                    old_obj = current_state.objects[obj_id]
                    if old_obj.centroid != current_obj.centroid or old_obj.color != current_obj.color:
                        object_interaction += 1.0
                else:
                    object_interaction += 1.0
                
        import math
        novelty_bonus = 20.0 / math.sqrt(visit_count + 1)
        
        score = (
            goal_progress * 100.0
            + info_gain * 5.0
            + exploration_reward
            + novelty_bonus
            - loop_penalty
            + object_interaction * 10.0
        )
        
        return score

    def compute_goal_progress(self, state: SceneGraph, goal: Optional['Goal']) -> float:
        """Heuristic for ARC-AGI: evaluate distance based on the current Goal."""
        import math
        progress = 0.0
        
        if not goal or not goal.target_conditions:
            return 0.0
            
        goal_type = goal.target_conditions.get("type")
        
        if goal_type == "Reach":
            target_id = goal.target_conditions.get("target_id")
            if target_id and target_id in state.objects:
                target_obj = state.objects[target_id]
                
                # Find the player object (the one that moves)
                # Since we don't have is_movable here directly, we just calculate distance
                # from the target object to all other objects, and reward minimizing the minimum distance.
                min_dist = float('inf')
                for obj_id, obj in state.objects.items():
                    if obj_id != target_id:
                        dist = abs(obj.centroid[0] - target_obj.centroid[0]) + abs(obj.centroid[1] - target_obj.centroid[1])
                        if dist < min_dist:
                            min_dist = dist
                            
                if min_dist < float('inf'):
                    progress = math.exp(-min_dist * 0.2)
                    
        elif goal_type == "Explore":
            # Exploration is rewarded primarily through the exploration_reward in evaluate_state
            # But we can add a slight reward for spreading out objects
            pass
            
        return progress
