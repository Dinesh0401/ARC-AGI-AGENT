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
        self.hypothesis_manager = HypothesisManager(self.memory.belief_memory)
        self.inference_engine = InferenceEngine(
            self.memory.semantic, self.memory.knowledge_base, self.hypothesis_manager
        )
        self.confidence_tracker = ConfidenceTracker(
            self.memory.belief_memory, self.memory.episodic
        )
        self.verifier = Verifier(self.memory.knowledge_base)
        self.goal_generator = GoalGenerator(
            self.memory.working, self.memory.belief_memory
        )

        # 4. World Model
        self.prediction_engine = PredictionEngine()

        # 5. Planning
        def world_model_transition(state: SceneGraph, action_str: str) -> SceneGraph:
            if self.enable_world_model:
                pred = self.prediction_engine.evaluate_action(state, action_str)
                return pred.predicted_state
            return state

        self.planner = PlanningOrchestrator(world_model_transition)

        # 6. Learning Loop
        self.learning_loop = LearningLoop(self.memory, self.prediction_engine)

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

    def act(self, observation: Dict[str, Any]) -> Any:
        """Execute Cognitive Pipeline respecting ablation flags."""
        grid_data = observation.get("frame", observation.get("grid", []))
        if isinstance(grid_data, list):
            grid = np.array(grid_data)
        else:
            grid = grid_data

        available_actions = observation.get(
            "available_actions", ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]
        )

        # 1. Perception
        objects = self.parser.parse_grid(grid)
        relations = self.relation_detector.detect_relations(objects)
        current_scene = SceneGraph(objects, relations)

        # 2. Learning Loop (If enabled)
        if (
            self.enable_learning
            and self.last_scene_graph is not None
            and self.last_action is not None
        ):
            exp = Experience(
                pre_state=self.last_scene_graph,
                action=self.last_action,
                prediction=self.last_prediction,
                actual_state=current_scene,
                plan=self.active_plan,
            )
            self.learning_loop.process_experience(exp)

        # 3. Knowledge Base Update (If memory enabled)
        if self.enable_memory:
            self.memory.knowledge_base.facts.clear()
            for obj in objects:
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
                self.memory.working.add_thought("Need to find target pattern", priority=5)

        # 4. Goal Generation & Planning (If planning enabled)
        selected_action = None
        if self.enable_planning:
            goals = self.goal_generator.generate_goals() if self.enable_memory else []
            if goals:
                top_goal = goals[0]
                valid_actions = [
                    a for a in available_actions if isinstance(a, str) and a != "RESET"
                ]
                if not valid_actions:
                    valid_actions = ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]

                self.active_plan = self.planner.generate_plan(
                    current_scene, top_goal, valid_actions
                )

                if self.active_plan and self.active_plan.actions:
                    selected_action = self.active_plan.actions[0]

        # Fallback to intelligent action selection
        if selected_action is None:
            valid_actions = [
                a for a in available_actions if isinstance(a, str) and a != "RESET"
            ]
            if valid_actions:
                selected_action = str(np.random.choice(valid_actions))
            else:
                selected_action = "ACTION1"

        # 5. World Model Prediction (If enabled)
        if self.enable_world_model:
            self.last_prediction = self.prediction_engine.evaluate_action(
                current_scene, selected_action
            )

        self.last_scene_graph = current_scene
        self.last_action = selected_action

        return selected_action
