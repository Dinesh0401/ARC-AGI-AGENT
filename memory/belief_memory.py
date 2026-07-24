from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum, auto

class BeliefType(Enum):
    FACT = auto()
    RULE = auto()
    ASSUMPTION = auto()
    HYPOTHESIS = auto()
    GOAL = auto()
    CONSTRAINT = auto()

@dataclass
class Belief:
    """Represents a dynamic assumption or rule about the environment."""
    id: str
    belief_type: BeliefType
    hypothesis: str
    confidence: float
    evidence: int = 0
    contradictions: int = 0

class BeliefMemory:
    """Stores beliefs, adjusting their confidence over time as new evidence arrives."""
    
    def __init__(self):
        self.beliefs: Dict[str, Belief] = {}
        self._next_id = 1
        
    def add_belief(self, hypothesis: str, belief_type: BeliefType = BeliefType.HYPOTHESIS, confidence: float = 0.5) -> str:
        """Register a new belief."""
        b_id = f"Belief_{self._next_id:03d}"
        self.beliefs[b_id] = Belief(
            id=b_id,
            belief_type=belief_type,
            hypothesis=hypothesis,
            confidence=confidence
        )
        self._next_id += 1
        return b_id
        
    def get_belief(self, b_id: str) -> Optional[Belief]:
        return self.beliefs.get(b_id)
        
    def update_evidence(self, b_id: str, is_supportive: bool, delta_confidence: float = 0.1):
        """Update the evidence count and adjust confidence based on new observations."""
        belief = self.beliefs.get(b_id)
        if not belief:
            return
            
        if is_supportive:
            belief.evidence += 1
            belief.confidence = min(1.0, belief.confidence + delta_confidence)
        else:
            belief.contradictions += 1
            belief.confidence = max(0.0, belief.confidence - delta_confidence)
            
    def get_all_beliefs(self) -> List[Belief]:
        return list(self.beliefs.values())
        
    def get_high_confidence_beliefs(self, threshold: float = 0.7) -> List[Belief]:
        return [b for b in self.beliefs.values() if b.confidence >= threshold]
