from .episodic import EpisodicMemory
from .semantic import SemanticMemory
from .working import WorkingMemory
from .procedural import ProceduralMemory
from .knowledge_base import KnowledgeBase
from .belief_memory import BeliefMemory

class CognitiveMemory:
    """Orchestrator for the cognitive memory system, beliefs, and knowledge base."""
    
    def __init__(self):
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.working = WorkingMemory(capacity=10)
        self.procedural = ProceduralMemory()
        self.knowledge_base = KnowledgeBase()
        self.belief_memory = BeliefMemory()
        
    def clear_episode(self):
        """Clear short-term state for a new episode."""
        self.episodic.clear()
        self.working.clear()
        self.knowledge_base.facts.clear()
        # Beliefs might persist across episodes depending on the task, but for ARC they usually reset per task
        self.belief_memory.beliefs.clear()

__all__ = [
    "CognitiveMemory", 
    "EpisodicMemory", 
    "SemanticMemory", 
    "WorkingMemory", 
    "ProceduralMemory", 
    "KnowledgeBase",
    "BeliefMemory"
]
