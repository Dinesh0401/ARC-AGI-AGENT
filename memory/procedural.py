from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class StrategyRecord:
    situation: Dict[str, Any]
    strategy: List[str]  # e.g. ["ACTION1", "ACTION2"]
    outcome: str         # e.g. "Success", "Failed"
    efficiency: float    # e.g. reward or steps taken
    confidence: float

class ProceduralMemory:
    """Stores strategies with their context (Situation -> Strategy -> Outcome)."""
    
    def __init__(self):
        self.records: List[StrategyRecord] = []
        
    def add_strategy(self, situation: Dict[str, Any], strategy: List[str], outcome: str, efficiency: float = 1.0, confidence: float = 1.0):
        """Record an action sequence, its context, and outcome."""
        record = StrategyRecord(
            situation=situation,
            strategy=strategy,
            outcome=outcome,
            efficiency=efficiency,
            confidence=confidence
        )
        self.records.append(record)
                
    def get_successful_strategies(self) -> List[StrategyRecord]:
        return [r for r in self.records if r.outcome == "Success"]
        
    def get_failed_strategies(self) -> List[StrategyRecord]:
        return [r for r in self.records if r.outcome == "Failed"]
        
    def find_relevant_strategies(self, current_situation: Dict[str, Any]) -> List[StrategyRecord]:
        """Basic heuristic to find strategies that match the current situation."""
        # For an MVP, we just return successful strategies that share some keys with the situation.
        # A more advanced implementation would compute similarity.
        relevant = []
        for record in self.get_successful_strategies():
            match_count = sum(1 for k, v in current_situation.items() if record.situation.get(k) == v)
            if match_count > 0:
                relevant.append(record)
        # Sort by match strength or confidence (simplifying here by sorting by confidence)
        relevant.sort(key=lambda r: r.confidence, reverse=True)
        return relevant
