from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from memory.working import WorkingMemory
from memory.belief_memory import BeliefMemory

@dataclass
class Goal:
    """A concrete objective emitted for the Planner."""
    description: str
    target_conditions: Dict[str, Any]
    priority: int
    confidence: float
    source: str
    deadline: Optional[int] = None
    
class GoalGenerator:
    """Converts beliefs and high-priority thoughts into actionable Goals."""
    
    def __init__(self, working_memory: WorkingMemory, belief_memory: BeliefMemory):
        self.working = working_memory
        self.belief_memory = belief_memory
        
    def generate_goals(self) -> List[Goal]:
        """Produce goals from current thoughts and high-confidence beliefs."""
        goals = []
        
        # 1. Check Working Memory thoughts
        thoughts = self.working.get_thoughts()
        for thought in thoughts:
            if "Need to find" in thought.text:
                goals.append(Goal(
                    description=thought.text,
                    target_conditions={"type": "Search", "target": thought.text.split()[-1]},
                    priority=thought.priority,
                    confidence=1.0,
                    source="WorkingMemory"
                ))
                
        # 2. Check High-Confidence Beliefs
        for belief in self.belief_memory.get_high_confidence_beliefs(threshold=0.7):
            # If belief implies a promising action, generate a goal to execute it
            if "Applying" in belief.hypothesis and "will succeed" in belief.hypothesis:
                action = belief.hypothesis.split()[1]
                target_obj = belief.hypothesis.split()[3]
                
                goals.append(Goal(
                    description=f"Execute {action} on {target_obj}",
                    target_conditions={"action": action, "target_obj": target_obj},
                    priority=int(belief.confidence * 10),
                    confidence=belief.confidence,
                    source=f"BeliefMemory:{belief.id}"
                ))
                
        # Sort goals by priority
        goals.sort(key=lambda g: g.priority, reverse=True)
        return goals
