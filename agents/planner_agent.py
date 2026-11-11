from typing import Any, List
from .multi_agent_system import BaseAgent, Blackboard
from reasoning.goal_generator import GoalGenerator
from planning import PlanningOrchestrator
from reasoning.value_function import ValueFunction
from learning.exploration import CuriosityExplorer

class PlannerAgent(BaseAgent):
    """Runs Beam Search and Rollouts to find optimal sequences of actions."""
    
    def __init__(self, blackboard: Blackboard, hypothesis_agent: Any, memory_agent: Any):
        super().__init__("PlannerAgent", blackboard)
        self.goal_generator = GoalGenerator(memory_agent.memory.working, hypothesis_agent.engine)
        self.value_function = ValueFunction(memory_agent.memory.episodic, hypothesis_agent.engine)
        
        def world_model_transition(state, action_str):
            pred = hypothesis_agent.prediction_engine.evaluate_action(state, action_str)
            return pred.predicted_state

        self.planner = PlanningOrchestrator(world_model_transition, self.value_function)
        self.explorer = CuriosityExplorer(memory_agent.memory.episodic, hypothesis_agent.prediction_engine, hypothesis_agent.engine)
        
        self.state_history = []
        self.recent_actions = []
        self.active_plan = None
        self.last_prediction = None
        
    def check_stalls(self, current_scene: Any) -> bool:
        current_hash = "|".join(sorted(f"{obj.color}:{round(obj.centroid[0], 1)},{round(obj.centroid[1], 1)}" for obj in current_scene.objects.values()))
        self.state_history.append(current_hash)
        if len(self.state_history) > 10:
            self.state_history.pop(0)
            
        is_stalled = False
        
        # Check for A1 A2 A1 A2 oscillation
        if len(self.recent_actions) >= 4:
            a1, a2, a3, a4 = self.recent_actions[-4:]
            if a1 == a3 and a2 == a4 and a1 != a2:
                is_stalled = True
                self.blackboard.plans["banned_actions"].update([a1, a2])
                
        # Check for state stalling
        if len(self.state_history) >= 4 and len(set(self.state_history[-4:])) == 1:
            is_stalled = True
            
        return is_stalled

    def run(self) -> None:
        current_scene = self.blackboard.observations.get("current_scene")
        available_actions = self.blackboard.observations.get("available_actions", [])
        
        if not current_scene:
            return
            
        is_stalled = self.check_stalls(current_scene)
        
        banned = self.blackboard.plans["banned_actions"]
        valid_actions = [a for a in available_actions if isinstance(a, str) and a != "RESET" and a not in banned]
        if not valid_actions:
            valid_actions = [a for a in ["ACTION1", "ACTION2", "ACTION3", "ACTION4"] if a not in banned]
            if not valid_actions:
                valid_actions = ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]
                
        selected_action = None
        reasoning = []
        conf = 0.5
        
        goals = self.blackboard.goals.get("active_goals", [])
        
        if not is_stalled and goals:
            top_goal = goals[0]
            self.active_plan = self.planner.generate_plan(current_scene, top_goal, valid_actions)
            
            if self.active_plan and self.active_plan.actions:
                conf = self.active_plan.confidence
                if conf > 0.7:
                    selected_action = self.active_plan.actions[0]
                    reasoning.append(f"Beam search found optimal path for goal: '{top_goal.description}'")
                    reasoning.append(f"Expected reward: {getattr(self.active_plan, 'expected_reward', 0.0):.2f}")
                    reasoning.append(f"Selected action: {selected_action}")
                    self.blackboard.metrics["planner_success_rate"] = 1.0
                else:
                    reasoning.append(f"Generated plan for '{top_goal.description}' but confidence was too low ({conf:.2f}).")
                    
        if not selected_action:
            if is_stalled:
                selected_action = min(valid_actions, key=lambda a: self.recent_actions.count(a))
                reasoning.append(f"Agent stalled in state cycle. Forced exploration (least-recently-used action).")
                reasoning.append(f"Selected action: {selected_action}")
            else:
                selected_action = self.explorer.choose_action(current_scene, valid_actions, self.recent_actions[-1] if self.recent_actions else None)
                reasoning.append("Executing curiosity-driven exploration for novelty.")
                reasoning.append(f"Selected action: {selected_action}")
                
        self.recent_actions.append(selected_action)
        if len(self.recent_actions) > 10:
            self.recent_actions.pop(0)
            
        self.blackboard.plans["selected_action"] = selected_action
        self.blackboard.plans["active_plan"] = self.active_plan
        
        self.log_trace(
            action_type="Plan",
            reasoning=reasoning,
            confidence=conf,
            metrics={"selected_action": selected_action}
        )
