from memory.belief_memory import BeliefMemory

class BeliefUpdater:
    """Updates Belief confidences based on the calculated Prediction Error."""
    
    def __init__(self, belief_memory: BeliefMemory):
        self.belief_memory = belief_memory
        
    def update_beliefs(self, prediction_error: float, originating_belief_ids: list[str]):
        """
        If prediction error is low, the belief is reinforced.
        If prediction error is high, the belief is penalized.
        """
        for b_id in originating_belief_ids:
            belief = self.belief_memory.get_belief(b_id)
            if not belief:
                continue
                
            if prediction_error < 0.2:
                # Strong reinforcement
                self.belief_memory.update_evidence(b_id, is_supportive=True, delta_confidence=0.15)
            elif prediction_error > 0.5:
                # Strong contradiction
                self.belief_memory.update_evidence(b_id, is_supportive=False, delta_confidence=0.3)
            else:
                # Mild contradiction
                self.belief_memory.update_evidence(b_id, is_supportive=False, delta_confidence=0.05)
