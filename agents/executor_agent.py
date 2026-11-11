from typing import Any
from .multi_agent_system import BaseAgent, Blackboard
from integration.arc_adapter import ActionAdapter

class ExecutorAgent(BaseAgent):
    """Executes the final chosen action in the environment."""
    
    def __init__(self, blackboard: Blackboard):
        super().__init__("ExecutorAgent", blackboard)
        
    def run(self) -> Any:
        selected_internal_action = self.blackboard.plans.get("selected_action")
        if not selected_internal_action:
            return None
            
        game_action = ActionAdapter.to_game_action(selected_internal_action)
        
        self.log_trace(
            action_type="Execute",
            reasoning=[
                f"Selected action: {selected_internal_action}",
                f"Translated to environment API action: {game_action}",
                "Executing action in environment."
            ],
            confidence=1.0
        )
        
        return game_action
