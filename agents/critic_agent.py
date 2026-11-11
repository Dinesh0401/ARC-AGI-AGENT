from typing import Any
from .multi_agent_system import BaseAgent, Blackboard

class CriticAgent(BaseAgent):
    """Evaluates generated hypotheses and rules, rejecting those with low confidence."""
    
    def __init__(self, blackboard: Blackboard):
        super().__init__("CriticAgent", blackboard)
        
    def run(self) -> None:
        transition_model = None
        if self.blackboard.predictions.get("engine"):
            transition_model = self.blackboard.predictions["engine"].transition_model
            
        if not transition_model:
            return
            
        rejected_rules = []
        
        # We prune rules in the transition model based on confidence
        for action, rules in transition_model.rules.items():
            for rule in list(rules):
                # If a rule has failed continuously, its confidence drops
                if rule.total_matches > 3 and rule.confidence < 0.2:
                    rules.remove(rule)
                    rejected_rules.append(f"{rule.effects} (Conf: {rule.confidence:.2f})")
                    
        reasoning = ["Evaluated active physical rules and hypotheses."]
        if rejected_rules:
            for r in rejected_rules:
                reasoning.append(f"Rejected rule: {r}")
            self.blackboard.hypotheses["rejected"].extend(rejected_rules)
        else:
            reasoning.append("All active rules meet confidence thresholds.")
            
        self.log_trace(
            action_type="Critique",
            reasoning=reasoning,
            confidence=0.9,
            metrics={"rejected_count": len(rejected_rules)}
        )
