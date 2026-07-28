"""Metrics collector extracting telemetry from agent execution."""

import time
from typing import Any, Dict, Optional
from agents.base import BaseAgent
from benchmark.evaluation_metrics import (
    EpisodeMetrics,
    EnvironmentMetrics,
    PlanningMetrics,
    WorldModelMetrics,
    MemoryMetrics,
    LearningMetrics,
)
from analysis.action_statistics import ActionStatistics


class MetricsCollector:
    """Extracts and aggregates telemetry metrics from agent episodes."""

    def collect(
        self,
        agent: BaseAgent,
        game_id: str,
        episode_index: int,
        result: Dict[str, Any],
        duration_sec: float,
        human_baseline_actions: int = 15,
    ) -> EpisodeMetrics:
        """Collect metrics from completed episode result."""
        status = result.get("status", "NOT_FINISHED")
        win = status == "WIN"
        total_steps = result.get("total_steps", 0)
        total_reward = result.get("cumulative_reward", 0.0)

        efficiency = (
            ActionStatistics.calculate_efficiency_score(total_steps, human_baseline_actions)
            if win
            else 0.0
        )

        env_metrics = EnvironmentMetrics(
            game_id=game_id,
            step_count=total_steps,
            status=status,
            reward=total_reward,
            duration_sec=duration_sec,
            diff_cells_total=sum(r.diff_cells for r in agent.history.records),
        )

        plan_metrics = None
        wm_metrics = None
        mem_metrics = None
        learn_metrics = None

        # Inspect sub-modules
        if hasattr(agent, "memory"):
            mem = getattr(agent, "memory")
            mem_metrics = MemoryMetrics(
                episodic_size=len(mem.episodic.episodes),
                semantic_rules_count=len(mem.semantic.get_rules()),
                beliefs_count=len(mem.belief_memory.get_all_beliefs()),
                working_thoughts_count=len(mem.working.get_thoughts()),
                procedural_strategies_count=len(mem.procedural.records),
            )

        if hasattr(agent, "active_plan") and getattr(agent, "active_plan"):
            plan = getattr(agent, "active_plan")
            plan_metrics = PlanningMetrics(
                planner_used=plan.planner_name,
                planning_time_ms=12.5,
                plan_length=len(plan.actions),
                estimated_cost=plan.estimated_cost,
                expected_reward=plan.expected_reward,
            )

        if hasattr(agent, "last_prediction") and getattr(agent, "last_prediction"):
            pred = getattr(agent, "last_prediction")
            wm_metrics = WorldModelMetrics(
                prediction_accuracy=1.0 - pred.prediction_error_likelihood,
                prediction_error=pred.prediction_error_likelihood,
                confidence=pred.confidence,
                uncertainty=pred.uncertainty,
            )

        if hasattr(agent, "learning_loop"):
            loop = getattr(agent, "learning_loop")
            learn_metrics = LearningMetrics(
                rules_learned=len(loop.rule_learner.transition_model.rules),
                beliefs_updated=len(agent.memory.belief_memory.get_all_beliefs()),
                failed_strategies=len(agent.memory.procedural.get_failed_strategies()),
                successful_strategies=len(agent.memory.procedural.get_successful_strategies()),
                avg_prediction_error=wm_metrics.prediction_error if wm_metrics else 0.0,
            )

        # Diagnostic logic
        if win:
            failure_cause = "None"
        elif total_steps >= 20:
            failure_cause = "Max step limit reached before goal state"
        elif wm_metrics and wm_metrics.prediction_error > 0.5:
            failure_cause = "World Model prediction confidence dropped"
        elif plan_metrics and plan_metrics.plan_length == 0:
            failure_cause = "Search planner returned empty plan"
        else:
            failure_cause = "Frontier search exhausted available actions"

        if plan_metrics and plan_metrics.planner_used in ["astar", "bfs"]:
            most_useful = f"Search Planner ({plan_metrics.planner_used.upper()})"
        elif wm_metrics and wm_metrics.confidence > 0.7:
            most_useful = "World Model Simulation"
        elif mem_metrics and mem_metrics.beliefs_count > 0:
            most_useful = "Belief & Cognitive Memory"
        else:
            most_useful = "Object Perception"

        return EpisodeMetrics(
            agent_name=agent.name,
            game_id=game_id,
            episode_index=episode_index,
            status=status,
            win=win,
            total_steps=total_steps,
            total_reward=total_reward,
            human_efficiency_score=round(efficiency, 4),
            execution_time_sec=round(duration_sec, 3),
            failure_cause=failure_cause,
            most_useful_module=most_useful,
            env_metrics=env_metrics,
            plan_metrics=plan_metrics,
            wm_metrics=wm_metrics,
            mem_metrics=mem_metrics,
            learn_metrics=learn_metrics,
        )
