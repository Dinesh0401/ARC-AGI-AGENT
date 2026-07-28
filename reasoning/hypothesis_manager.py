from typing import Any
from memory.belief_memory import BeliefMemory

class HypothesisManager:
    """Formulates and registers new hypotheses as beliefs."""
    
    def __init__(self, belief_memory: BeliefMemory):
        self.belief_memory = belief_memory
        
    def generate_hypothesis(self, hypothesis_text: str, initial_confidence: float = 0.5) -> str:
        """Create a new hypothesis to test in the environment."""
        # Check if identical hypothesis exists
        for b in self.belief_memory.get_all_beliefs():
            if b.hypothesis == hypothesis_text:
                return b.id
                
        belief_id = self.belief_memory.add_belief(hypothesis_text, confidence=initial_confidence)
        return belief_id
