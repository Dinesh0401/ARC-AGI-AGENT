"""Action-level statistics and ARC-AGI-3 efficiency metrics."""

from typing import Any, Dict, List


class ActionStatistics:
    """Computes action usage distributions and ARC-AGI-3 human-baseline efficiency scores."""

    @staticmethod
    def calculate_efficiency_score(agent_actions: int, human_baseline_actions: int) -> float:
        """Calculate official ARC-AGI-3 level efficiency score.

        Formula: min(human_actions / agent_actions, 1.0)^2
        """
        if agent_actions <= 0 or human_baseline_actions <= 0:
            return 0.0
        ratio = min(human_baseline_actions / agent_actions, 1.0)
        return round(ratio ** 2, 4)

    @staticmethod
    def analyze_action_trajectory(trajectory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze action usage distribution across an episode trajectory.

        Args:
            trajectory: List of step dictionary records.

        Returns:
            Dictionary containing action counts, total steps, and complex action counts.
        """
        action_counts: Dict[str, int] = {}
        complex_action_count = 0

        for step in trajectory:
            act = step.get("action")
            act_str = act[0] if isinstance(act, (list, tuple)) else str(act)
            action_counts[act_str] = action_counts.get(act_str, 0) + 1
            if act_str == "ACTION6" or isinstance(act, (list, tuple)):
                complex_action_count += 1

        return {
            "total_actions": len(trajectory),
            "action_counts": action_counts,
            "complex_action_count": complex_action_count,
        }
