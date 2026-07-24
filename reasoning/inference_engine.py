from typing import List, Dict, Any
from memory.semantic import SemanticMemory
from memory.knowledge_base import KnowledgeBase
from reasoning.hypothesis_manager import HypothesisManager

class InferenceEngine:
    """Applies deductive/inductive logic across Rules and Facts."""
    
    def __init__(self, semantic: SemanticMemory, knowledge_base: KnowledgeBase, hypothesis_manager: HypothesisManager):
        self.semantic = semantic
        self.kb = knowledge_base
        self.hypothesis_manager = hypothesis_manager
        
    def infer(self) -> List[str]:
        """Apply rules to current knowledge base facts to generate hypotheses or conclusions.
        Returns a list of generated Belief IDs.
        """
        new_belief_ids = []
        rules = self.semantic.get_rules()
        
        for rule in rules:
            # Check if condition matches any objects
            # Condition format: {"Left Of": True, ...} (simplified)
            # In a real engine, we'd do unification. Here we do simple property matching.
            
            for obj_id, facts in self.kb.facts.items():
                match = True
                for k, v in rule.condition.items():
                    # Very simple inference mechanism for prototype
                    if k in facts:
                        if facts[k] != v and v not in facts[k]:
                            match = False
                            break
                    else:
                        match = False
                        break
                        
                if match:
                    # The condition holds for obj_id. Create a hypothesis from the outcome.
                    action_or_fact = rule.outcome.get("action_or_fact", "Unknown Action")
                    hypothesis = f"Applying {action_or_fact} on {obj_id} will succeed."
                    b_id = self.hypothesis_manager.generate_hypothesis(hypothesis, initial_confidence=0.6)
                    new_belief_ids.append(b_id)
                    
        return new_belief_ids
