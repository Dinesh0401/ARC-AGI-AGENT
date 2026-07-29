"""Cognitive Agent integrating Perception, Memory, Reasoning, World Model, Planning, and Learning."""

import numpy as np
from typing import Any, Dict, List, Optional, Tuple

from agents.base import BaseAgent
from perception.object_parser import ObjectParser
from perception.relation_detector import RelationDetector
from perception.scene_graph import SceneGraph
from memory import CognitiveMemory
from reasoning import (
    HypothesisManager,
    InferenceEngine,
    ConfidenceTracker,
    Verifier,
    GoalGenerator,
    Goal,
)
from world_model import PredictionEngine
from planning import PlanningOrchestrator, Plan
from learning import LearningLoop, Experience
from learning.exploration import CuriosityExplorer
from memory.object_tracker import ObjectTracker

class CognitiveAgent(BaseAgent):
    """Full Cognitive Architecture Agent for ARC-AGI-3 environments with Ablation Toggles."""

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
        np.random.seed(seed)

        self.enable_memory = enable_memory
        self.enable_world_model = enable_world_model
        self.enable_planning = enable_planning
        self.enable_learning = enable_learning

        # 1. Perception
        self.parser = ObjectParser()
        self.relation_detector = RelationDetector()

        # 2. Cognitive Memory
        self.memory = CognitiveMemory()

        # 3. Reasoning
        from reasoning.hypothesis_engine import HypothesisEngine
        self.hypothesis_engine = HypothesisEngine()
        self.inference_engine = InferenceEngine(
            self.memory.semantic, self.memory.knowledge_base, self.hypothesis_engine
        )
        self.confidence_tracker = ConfidenceTracker(
            self.memory.belief_memory, self.memory.episodic
        )
        self.verifier = Verifier(self.memory.knowledge_base)
        self.goal_generator = GoalGenerator(
            self.memory.working, self.hypothesis_engine
        )
        from reasoning.value_function import ValueFunction
        self.value_function = ValueFunction(self.memory.episodic, self.hypothesis_engine)

        # 4. World Model
        self.prediction_engine = PredictionEngine()

        # 5. Planning
        def world_model_transition(state: SceneGraph, action_str: str) -> SceneGraph:
            if self.enable_world_model:
                pred = self.prediction_engine.evaluate_action(state, action_str)
                return pred.predicted_state
            return state

        self.planner = PlanningOrchestrator(world_model_transition, self.value_function)

        # 6. Learning Loop
        self.learning_loop = LearningLoop(self.memory, self.prediction_engine)
        
        # 7. Object Tracking & Exploration
        from learning.exploration import CuriosityExplorer
        from memory.object_tracker import ObjectTracker
        from memory.causal_graph import CausalGraph
        self.explorer = CuriosityExplorer(self.memory.episodic, self.prediction_engine, self.hypothesis_engine)
        self.causal_graph = CausalGraph()
        self.object_tracker = ObjectTracker(self.causal_graph)

        # State tracking
        self.last_scene_graph: Optional[SceneGraph] = None
        self.last_action: Optional[str] = None
        self.last_prediction: Optional[Any] = None
        self.active_plan: Optional[Plan] = None

    def reset(self) -> None:
        """Reset internal agent memory & state between episodes."""
        super().reset()
        self.memory.clear_episode()
        self.last_scene_graph = None
        self.last_action = None
        self.last_prediction = None
        self.active_plan = None
        from memory.object_tracker import ObjectTracker
        from memory.causal_graph import CausalGraph
        self.causal_graph = CausalGraph()
        self.object_tracker = ObjectTracker(self.causal_graph) # Reset tracking
        
        # Cognitive Metrics
        self.planner_invocations = 0
        self.total_planning_depth = 0
        self.repeated_loop_count = 0
        self.object_interactions = 0
        self.planner_successes = 0
        self.planner_fallbacks = 0
        self.total_beam_score = 0.0
        self.total_planner_confidence = 0.0

    def is_done(self, frames: List[Dict[str, Any]], latest_frame: Dict[str, Any]) -> bool:
        """Check if the goal is achieved or if we should terminate."""
        if self.enable_memory and self.memory.knowledge_base.facts.get("solved", False):
            return True
        return False

    def choose_action(self, frames: List[Dict[str, Any]], latest_frame: Dict[str, Any]) -> Any:
        """Execute Cognitive Pipeline respecting ablation flags and returning official GameAction."""
        # 0. Import adapters locally to avoid circular dependencies if any
        from integration.arc_adapter import FrameParser, ActionAdapter
        
        parser = FrameParser()
        current_scene = parser.parse(latest_frame)

        available_actions = latest_frame.get(
            "available_actions", ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]
        )
        
        # 1. Update Object Tracker and Episodic Memory
        self.object_tracker.track_scene(current_scene, self.last_action)
        
        # Track player visited tiles
        for obj_id, obj in self.object_tracker.tracked_objects.items():
            if obj.is_movable and obj_id in current_scene.objects:
                centroid = current_scene.objects[obj_id].centroid
                self.memory.episodic.visited_tiles.add((int(centroid[0]), int(centroid[1])))
                break
                
        if self.enable_memory and self.last_scene_graph and self.last_action:
            # We assume a sparse reward (0) for now until the level ends
            self.memory.episodic.add_experience(self.last_scene_graph, self.last_action, 0.0, current_scene)
        
        # 2. Learning & Verification Loop
        if (
            self.last_scene_graph is not None
            and self.last_action is not None
        ):
            # 2a. Verify hypotheses against reality
            self.hypothesis_engine.evaluate_action_results(
                str(self.last_action), current_scene, self.last_scene_graph, self.prediction_engine.transition_model
            )
            
            # 2b. Core learning loop
            if self.enable_learning:
                exp = Experience(
                    pre_state=self.last_scene_graph,
                    action=self.last_action,
                    prediction=self.last_prediction,
                    actual_state=current_scene,
                    plan=self.active_plan,
                )
                error = self.learning_loop.process_experience(exp)
                
                # Update prediction metrics
                if self.last_prediction and hasattr(self, 'prediction_engine'):
                    self.prediction_engine.total_predictions += 1
                    if error < 0.1:
                        self.prediction_engine.correct_predictions += 1

        # 3. Knowledge Base Update (If memory enabled)
        if self.enable_memory:
            self.memory.knowledge_base.facts.clear()
            for obj in current_scene.objects.values():
                self.memory.knowledge_base.update_fact(
                    obj.id,
                    {
                        "color": obj.color,
                        "area": obj.area,
                        "shape": obj.shape,
                        "centroid": obj.centroid,
                    },
                )
            self.inference_engine.infer()
            if not self.memory.working.get_thoughts():
                self.memory.working.add_thought("Need to explore environment", priority=5)

        # 3b. Anti-Loop & Stall Detection (Run BEFORE planning)
        current_hash = "|".join(sorted(f"{obj.color}:{round(obj.centroid[0], 1)},{round(obj.centroid[1], 1)}" for obj in current_scene.objects.values()))
        if not hasattr(self, 'state_history'):
            self.state_history = []
        self.state_history.append(current_hash)
        if len(self.state_history) > 10:
            self.state_history.pop(0)
            
        if not hasattr(self, 'recent_actions'):
            self.recent_actions = []
        
        is_stalled = False
        banned_actions = set()
        
        # Check for A1 A2 A1 A2 oscillation
        if len(self.recent_actions) >= 4:
            a1, a2, a3, a4 = self.recent_actions[-4:]
            if a1 == a3 and a2 == a4 and a1 != a2:
                is_stalled = True
                banned_actions.update([a1, a2])
                import logging
                logging.warning(f"Oscillation detected! Banning {a1} and {a2}.")
                
        # Check for state stalling (no progress)
        if len(self.state_history) >= 4 and len(set(self.state_history[-4:])) == 1:
            is_stalled = True
            import logging
            logging.warning("Agent stalled in same state for 3 steps! Enforcing exploration.")
            
        # 4. Goal Generation & Planning (If planning enabled)
        selected_internal_action = None
        if self.enable_planning and not is_stalled:
            goals = self.goal_generator.generate_goals(current_scene, self.object_tracker) if self.enable_memory else []
            if goals:
                top_goal = goals[0]
                valid_actions = [
                    a for a in available_actions if isinstance(a, str) and a != "RESET" and a not in banned_actions
                ]
                if not valid_actions:
                    valid_actions = ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]

                self.planner_invocations += 1
                self.active_plan = self.planner.generate_plan(
                    current_scene, top_goal, valid_actions
                )

                if self.active_plan and self.active_plan.actions:
                    planner_confidence = self.active_plan.confidence
                    self.total_planner_confidence += planner_confidence
                    self.total_beam_score += getattr(self.active_plan, "expected_reward", 0.0)
                    
                    metrics = getattr(self.active_plan, "metrics", {})
                    self.total_rollouts_expanded = getattr(self, "total_rollouts_expanded", 0) + metrics.get("expanded_nodes", 0)
                    if not hasattr(self, "unique_predicted_states_by_depth"):
                        self.unique_predicted_states_by_depth = {}
                    for d, count in metrics.get("unique_states_by_depth", {}).items():
                        self.unique_predicted_states_by_depth[d] = self.unique_predicted_states_by_depth.get(d, 0) + count
                        
                    if planner_confidence > 0.7:
                        self.planner_successes += 1
                        self.total_planning_depth += len(self.active_plan.actions)
                        selected_internal_action = self.active_plan.actions[0]
                    else:
                        self.planner_fallbacks += 1

        if selected_internal_action:
            self.recent_actions.append(selected_internal_action)
            if len(self.recent_actions) > 10:
                self.recent_actions.pop(0)

        # Fallback to intelligent action selection (Curiosity) if planner lacks confidence or stalled
        if selected_internal_action is None:
            valid_actions = [
                a for a in available_actions if isinstance(a, str) and a != "RESET" and a not in banned_actions
            ]
            if not valid_actions:
                valid_actions = ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]
                
            if valid_actions:
                if is_stalled:
                    # Force deterministic least-tried action in this state
                    if not hasattr(self, 'state_action_counts'):
                        self.state_action_counts = {}
                    candidates = valid_actions
                    
                    # Log state action counts for debugging
                    counts_debug = {a: self.state_action_counts.get(f"{current_hash}_{a}", 0) for a in candidates}
                    print(f"Stalled at hash {hash(current_hash)}. Action counts: {counts_debug}")
                    
                    selected_internal_action = min(candidates, key=lambda a: self.state_action_counts.get(f"{current_hash}_{a}", 0))
                    print(f"Selected least-tried action: {selected_internal_action}")
                else:
                    selected_internal_action = self.explorer.choose_action(current_scene, valid_actions, self.last_action)
                
                print(f"Selected experiment: {selected_internal_action}")
            else:
                selected_internal_action = "ACTION1"

        # 5. World Model Prediction (If enabled)
        if self.enable_world_model:
            self.last_prediction = self.prediction_engine.evaluate_action(
                current_scene, selected_internal_action
            )
            
        # Log Observation (Object Tracker tracks state changes)
        for obj_id, tracked_obj in self.object_tracker.tracked_objects.items():
            if tracked_obj.state_changes > 0 and tracked_obj.last_action_applied == self.last_action:
                import logging
                logging.info(f"Observation:\n{obj_id} state changed")
                self.object_interactions += 1
                
        # Simple loop detection for metric tracking
        if self.last_action and selected_internal_action:
            opposites = {
                "ACTION1": "ACTION2",
                "ACTION2": "ACTION1",
                "ACTION3": "ACTION4",
                "ACTION4": "ACTION3"
            }
            if opposites.get(str(self.last_action)) == str(selected_internal_action):
                self.repeated_loop_count += 1

        self.last_scene_graph = current_scene
        self.last_action = selected_internal_action
        
        if not hasattr(self, 'state_action_counts'):
            self.state_action_counts = {}
        state_action = f"{current_hash}_{selected_internal_action}"
        self.state_action_counts[state_action] = self.state_action_counts.get(state_action, 0) + 1

        # 6. Adapt internal action to official GameAction
        return ActionAdapter.to_game_action(selected_internal_action)
