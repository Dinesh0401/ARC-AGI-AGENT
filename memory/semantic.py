from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class Rule:
    """Represents an IF-THEN rule in semantic memory."""
    id: str
    condition: Dict[str, Any]  # e.g. {"state": "Door Closed", "inventory": "Key Owned"}
    outcome: Dict[str, Any]    # e.g. {"action": "ACTION2", "prediction": "success"}

class SemanticMemory:
    """Stores timeless facts, global rules, and generalized knowledge."""
    
    def __init__(self):
        # Format: { "Doors": {"requires": "Key"}, "ACTION1": "Shift Down", ... }
        self.concepts: Dict[str, Dict[str, Any]] = {}
        self.rules: List[Rule] = []
        self._next_rule_id = 1
        
    def add_concept(self, concept_name: str, attributes: Dict[str, Any]):
        """Add or update a high-level concept."""
        if concept_name not in self.concepts:
            self.concepts[concept_name] = {}
        self.concepts[concept_name].update(attributes)
        
    def get_concept(self, concept_name: str) -> Dict[str, Any]:
        """Retrieve generalized knowledge about a concept."""
        return self.concepts.get(concept_name, {})
        
    def add_rule(self, condition: Dict[str, Any], outcome: Dict[str, Any]) -> str:
        """Add an IF-THEN rule."""
        rule_id = f"Rule_{self._next_rule_id:03d}"
        rule = Rule(id=rule_id, condition=condition, outcome=outcome)
        self.rules.append(rule)
        self._next_rule_id += 1
        return rule_id
        
    def get_rules(self) -> List[Rule]:
        return self.rules
