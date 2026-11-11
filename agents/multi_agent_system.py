import json
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
import os

class TraceLog:
    """Manages the hierarchical reasoning traces emitted by agents."""
    def __init__(self, trace_file: str = "trace.json"):
        self.trace_file = trace_file
        self.traces = []
        # Clear the old trace file on init
        if os.path.exists(self.trace_file):
            with open(self.trace_file, 'w') as f:
                json.dump([], f)

    def log(self, agent_name: str, step: int, action_type: str, reasoning: List[str], confidence: float = 1.0, metrics: Dict[str, Any] = None, state_hash: str = ""):
        trace_entry = {
            "step": step,
            "state_hash": state_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "action": action_type,
            "confidence": confidence,
            "reasoning": reasoning,
            "metrics": metrics or {}
        }
        self.traces.append(trace_entry)
        self._flush()

    def _flush(self):
        try:
            with open(self.trace_file, 'w') as f:
                json.dump(self.traces, f, indent=2)
        except Exception:
            pass

class Blackboard:
    """Shared state mechanism for True Blackboard Architecture."""
    def __init__(self, trace_log: TraceLog):
        self.trace_log = trace_log
        self.current_step = 0
        
        # Core Blackboard Fields
        self.observations = {
            "latest_frame": None, # Raw dict from env
            "available_actions": [],
            "current_scene": None, # SceneGraph
            "last_scene": None
        }
        self.hypotheses = {
            "active": [],
            "verified": [],
            "rejected": [],
            "engine": None # Optional reference to HypothesisEngine state
        }
        self.goals = {
            "active_goals": []
        }
        self.predictions = {
            "predicted_state": None,
            "engine": None # TransitionModel
        }
        self.plans = {
            "banned_actions": set(),
            "active_plan": None,
            "selected_action": None
        }
        self.memory = {
            "object_tracker": None,
            "episodic": None,
            "semantic": None
        }
        self.metrics = {
            "prediction_accuracy": 0.0,
            "states_explored": 0,
            "hypotheses_generated": 0,
            "rules_verified": 0,
            "planner_success_rate": 0.0,
            "goal_progress": 0.0
        }

class BaseAgent:
    """Base class for all specialized cognitive agents."""
    def __init__(self, name: str, blackboard: Blackboard):
        self.name = name
        self.blackboard = blackboard

    def run(self) -> None:
        raise NotImplementedError("Agents must implement run() with no arguments")

    def log_trace(self, action_type: str, reasoning: List[str], confidence: float = 1.0, metrics: Dict[str, Any] = None):
        # Dynamically compute state hash if not passed, based on current scene if available
        state_hash = ""
        current_scene = self.blackboard.observations.get("current_scene")
        if current_scene:
            try:
                # Use the robust hash format
                pixel_tuples = [f"{obj.color}:{tuple(sorted(obj.pixels))}" for obj in current_scene.objects.values()]
                state_hash = str(hash(tuple(sorted(pixel_tuples))))
            except Exception:
                state_hash = "unknown"
                
        self.blackboard.trace_log.log(self.name, self.blackboard.current_step, action_type, reasoning, confidence, metrics, state_hash)
