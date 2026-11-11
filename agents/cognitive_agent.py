"""Cognitive Agent integrating Perception, Memory, Reasoning, World Model, Planning, and Learning via Multi-Agent System."""

from typing import Any, Dict, List, Optional
from agents.base import BaseAgent as BaseAgentInterface
from agents.multi_agent_system import Blackboard, TraceLog
from agents.goal_agent import GoalAgent
from agents.world_model_agent import WorldModelAgent
from agents.perception_agent import PerceptionAgent
from agents.memory_agent import MemoryAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.critic_agent import CriticAgent
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent

class CognitiveAgent(BaseAgentInterface):
    """Full Cognitive Architecture Agent implemented as a True Blackboard System."""

    def __init__(
        self,
        name: str = "CognitiveAgent",
        seed: int = 42,
        enable_memory: bool = True,
        enable_world_model: bool = True,
        enable_planning: bool = True,
        enable_learning: bool = True,
    ) -> None:
        super().__init__(name=name)
        self.seed = seed

        # Multi-Agent Orchestrator Setup
        self.trace_log = TraceLog()
        self.blackboard = Blackboard(self.trace_log)
        
        self.perception_agent = PerceptionAgent(self.blackboard)
        self.memory_agent = MemoryAgent(self.blackboard)
        self.goal_agent = GoalAgent(self.blackboard)
        self.hypothesis_agent = HypothesisAgent(self.blackboard)
        self.world_model_agent = WorldModelAgent(self.blackboard)
        self.critic_agent = CriticAgent(self.blackboard)
        self.planner_agent = PlannerAgent(self.blackboard, self.hypothesis_agent, self.memory_agent)
        self.executor_agent = ExecutorAgent(self.blackboard)

    def reset(self) -> None:
        """Reset internal agent memory & state between episodes."""
        super().reset()
        self.memory_agent.reset()
        self.blackboard.current_step = 0
        self.blackboard.plans["banned_actions"].clear()
        
        # Reset Blackboard state
        self.blackboard.observations["latest_frame"] = None
        self.blackboard.observations["current_scene"] = None
        self.blackboard.observations["last_scene"] = None
        self.blackboard.plans["selected_action"] = None
        self.blackboard.plans["active_plan"] = None

    def is_done(self, frames: List[Dict[str, Any]], latest_frame: Dict[str, Any]) -> bool:
        """Check if the goal is achieved or if we should terminate."""
        if self.memory_agent.memory.knowledge_base.facts.get("solved", False):
            return True
        return False

    def choose_action(self, frames: List[Dict[str, Any]], latest_frame: Dict[str, Any], human_action: Optional[str] = None) -> Any:
        """Execute Multi-Agent Pipeline via True Blackboard Architecture."""
        self.blackboard.current_step += 1
        
        # Inject raw frame into blackboard
        self.blackboard.observations["latest_frame"] = latest_frame
        
        # Sequential Agent Execution
        self.perception_agent.run()
        self.memory_agent.run()
        self.goal_agent.run()
        self.hypothesis_agent.run()
        self.world_model_agent.run()
        self.critic_agent.run()
        
        if human_action:
            self.blackboard.plans["selected_action"] = human_action
            self.trace_log.log(
                "HumanController", self.blackboard.current_step, "Override",
                [f"Human manually executed {human_action}."]
            )
            game_action = self.executor_agent.run()
        else:
            self.planner_agent.run()
            game_action = self.executor_agent.run()
        
        # Advance State
        self.blackboard.observations["last_scene"] = self.blackboard.observations["current_scene"]
        
        # Keep metrics matching old interface so main.py doesn't crash if it looks for them
        self.prediction_engine = self.hypothesis_agent.prediction_engine
        self.hypothesis_engine = self.hypothesis_agent.engine
        
        return game_action
