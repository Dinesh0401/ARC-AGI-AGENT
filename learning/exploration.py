from typing import Any, List, Optional
import numpy as np
import math

from perception.scene_graph import SceneGraph
from memory.episodic import EpisodicMemory
from world_model import PredictionEngine
from reasoning.hypothesis_engine import HypothesisEngine

class CuriosityExplorer:
    """Exploration module using Information-Theoretic scoring."""
    
    def __init__(self, memory: EpisodicMemory, prediction_engine: PredictionEngine, hypothesis_engine: Optional[HypothesisEngine] = None):
        self.memory = memory
        self.prediction_engine = prediction_engine
        self.hypothesis_engine = hypothesis_engine
        
    def choose_action(self, state: SceneGraph, valid_actions: List[Any], last_action: Optional[Any] = None) -> Any:
        """Choose an action that maximizes information gain and uncertainty reduction."""
        if not valid_actions:
            return None
            
        action_scores = []
        
        for action in valid_actions:
            action_str = str(action)
            
            # 1. Predict next state and uncertainty
            predicted_state = state 
            uncertainty = 1.0 # High uncertainty if no model
            try:
                pred = self.prediction_engine.evaluate_action(state, action_str)
                if pred and hasattr(pred, 'predicted_state'):
                    predicted_state = pred.predicted_state
                if hasattr(self.prediction_engine, 'get_uncertainty'):
                    uncertainty = self.prediction_engine.get_uncertainty(state, action_str)
            except Exception:
                pass
                
            # 2. Calculate Novelty (Inversely proportional to visit count)
            visit_count = self.memory.get_visit_count(predicted_state)
            novelty = 1.0 / (visit_count + 1)
            
            # 3. Calculate Information Gain based on expected uncertainty reduction
            info_gain = np.random.uniform(0.0, 0.1) # Small random noise to break ties
            if self.hypothesis_engine:
                for hyp in self.hypothesis_engine.get_hypotheses_for_action(action_str):
                    # Maximum uncertainty is when confidence is 0.5
                    # Information gain is proportional to the variance: p * (1 - p)
                    variance = hyp.confidence * (1.0 - hyp.confidence)
                    # Normalize so max gain is 1.0 (variance max is 0.25 at p=0.5)
                    info_gain += variance * 4.0
                    
                    if hyp.confidence < 0.9:
                        # Massive boost to test unknown/unverified hypotheses
                        info_gain += 50.0
            
            # 4. Loop Penalty
            penalty = 0
            
            # Immediate reverse penalty
            if last_action:
                last_action_str = str(last_action)
                opposites = {
                    "ACTION1": "ACTION2", # UP / DOWN
                    "ACTION2": "ACTION1",
                    "ACTION3": "ACTION4", # LEFT / RIGHT
                    "ACTION4": "ACTION3"
                }
                if opposites.get(last_action_str) == action_str:
                    penalty -= 5.0
                    
            # Deep loop penalty (has this predicted state been visited recently?)
            if hasattr(self.memory, 'get_recent_states'):
                recent_hashes = self.memory.get_recent_states(limit=5)
                # Compute hash of predicted_state
                pred_hash = "|".join(sorted(f"{oid}:{obj.color}:{obj.centroid}" for oid, obj in predicted_state.objects.items()))
                if pred_hash in recent_hashes:
                    penalty -= 10.0
                    
            # Total Score
            score = novelty + (uncertainty * 2.0) + info_gain + penalty
            action_scores.append(score)
            
        max_score = max(action_scores)
        best_actions = [a for a, s in zip(valid_actions, action_scores) if s == max_score]
            
        return np.random.choice(best_actions)
