from typing import Any
from .multi_agent_system import BaseAgent, Blackboard
from reasoning.goal_generator import GoalGenerator

class GoalAgent(BaseAgent):
    """Determines high-level goals based on environment state and memory."""
    
    def __init__(self, blackboard: Blackboard):
        super().__init__("GoalAgent", blackboard)
        
    def run(self) -> None:
        # Read from Blackboard
        current_scene = self.blackboard.observations["current_scene"]
        object_tracker = self.blackboard.memory["object_tracker"]
        working_memory = self.blackboard.memory.get("working") # fallback if needed
        hypothesis_engine = self.blackboard.hypotheses.get("engine")
        
        if not current_scene or not object_tracker or not hypothesis_engine:
            return
            
        generator = GoalGenerator(working_memory, hypothesis_engine)
        goals = generator.generate_goals(current_scene, object_tracker)
        
        # Write to Blackboard
        self.blackboard.goals["active_goals"] = goals
        
        reasoning = []
        if goals:
            for g in goals[:3]:
                reasoning.append(f"Formulated goal: '{g.description}' (Priority: {g.priority})")
        else:
            reasoning.append("No clear goals identified. Defaulting to exploration.")
            
        self.log_trace(
            action_type="Goal Setting",
            reasoning=reasoning,
            confidence=0.9,
            metrics={"goal_count": len(goals)}
        )
