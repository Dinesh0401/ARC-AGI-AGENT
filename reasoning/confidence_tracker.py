from memory.belief_memory import BeliefMemory
from memory.episodic import EpisodicMemory

class ConfidenceTracker:
    """Adjusts confidence scores in beliefs based on episodic evidence."""
    
    def __init__(self, belief_memory: BeliefMemory, episodic: EpisodicMemory):
        self.belief_memory = belief_memory
        self.episodic = episodic
        
    def evaluate_recent_evidence(self):
        """Review recent episodes and adjust confidence of active beliefs.
        Note: In a full implementation, this maps the episode's reward/next_state to specific beliefs.
        """
        recent = self.episodic.get_recent(1)
        if not recent:
            return
            
        state, action, reward, next_state = recent[0]
        
        # Prototype: if reward > 0, boost all active hypotheses related to that action
        is_supportive = reward > 0
        
        for belief in self.belief_memory.get_all_beliefs():
            if str(action) in belief.hypothesis:
                self.belief_memory.update_evidence(belief.id, is_supportive, delta_confidence=0.2)
