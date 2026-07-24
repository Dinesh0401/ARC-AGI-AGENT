"""Dataclasses defining evaluation metrics across environment, planning, world model, memory, and learning."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EnvironmentMetrics:
    game_id: str
    step_count: int
    status: str
    reward: float
    duration_sec: float
    diff_cells_total: int


@dataclass
class PlanningMetrics:
    planner_used: str
    planning_time_ms: float
    plan_length: int
    estimated_cost: float
    expected_reward: float


@dataclass
class WorldModelMetrics:
    prediction_accuracy: float
    prediction_error: float
    confidence: float
    uncertainty: float


@dataclass
class MemoryMetrics:
    episodic_size: int
    semantic_rules_count: int
    beliefs_count: int
    working_thoughts_count: int
    procedural_strategies_count: int


@dataclass
class LearningMetrics:
    rules_learned: int
    beliefs_updated: int
    failed_strategies: int
    successful_strategies: int
    avg_prediction_error: float


@dataclass
class EpisodeMetrics:
    agent_name: str
    game_id: str
    episode_index: int
    status: str
    win: bool
    total_steps: int
    total_reward: float
    human_efficiency_score: float
    execution_time_sec: float
    failure_cause: str = "None"
    most_useful_module: str = "Cognitive Perception"
    env_metrics: Optional[EnvironmentMetrics] = None
    plan_metrics: Optional[PlanningMetrics] = None
    wm_metrics: Optional[WorldModelMetrics] = None
    mem_metrics: Optional[MemoryMetrics] = None
    learn_metrics: Optional[LearningMetrics] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize episode metrics to dictionary for CSV/JSON export."""
        return {
            "agent_name": self.agent_name,
            "game_id": self.game_id,
            "episode_index": self.episode_index,
            "status": self.status,
            "win": self.win,
            "total_steps": self.total_steps,
            "total_reward": self.total_reward,
            "human_efficiency_score": self.human_efficiency_score,
            "execution_time_sec": self.execution_time_sec,
            "failure_cause": self.failure_cause,
            "most_useful_module": self.most_useful_module,
            "planner_used": self.plan_metrics.planner_used if self.plan_metrics else "N/A",
            "planning_time_ms": self.plan_metrics.planning_time_ms if self.plan_metrics else 0.0,
            "prediction_error": self.wm_metrics.prediction_error if self.wm_metrics else 0.0,
            "beliefs_count": self.mem_metrics.beliefs_count if self.mem_metrics else 0,
            "rules_learned": self.learn_metrics.rules_learned if self.learn_metrics else 0,
        }
