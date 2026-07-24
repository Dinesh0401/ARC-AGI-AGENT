"""Unit tests for analysis package modules (GameStatistics, FrameStatistics, ActionStatistics)."""

import pytest
from analysis.game_statistics import GameStatistics
from analysis.frame_statistics import FrameStatistics
from analysis.action_statistics import ActionStatistics


def test_game_statistics_hashing_and_coverage() -> None:
    stats = GameStatistics()
    frame1 = [[0, 1], [2, 3]]
    frame2 = [[0, 1], [2, 3]]
    frame3 = [[5, 6], [7, 8]]

    h1 = stats.record_frame(frame1)
    h2 = stats.record_frame(frame2)
    h3 = stats.record_frame(frame3)

    assert h1 == h2
    assert h1 != h3

    summary = stats.compute_summary()
    assert summary["total_state_visits"] == 3
    assert summary["unique_states_visited"] == 2
    assert summary["repeated_state_visits"] == 1


def test_frame_statistics_histogram() -> None:
    frame = [[0, 1, 15], [0, 0, 5]]
    hist = FrameStatistics.get_color_histogram(frame)
    assert hist[0] == 3
    assert hist[1] == 1
    assert hist[5] == 1
    assert hist[15] == 1


def test_action_statistics_efficiency() -> None:
    eff = ActionStatistics.calculate_efficiency_score(agent_actions=20, human_baseline_actions=10)
    # (10/20)^2 = (0.5)^2 = 0.25
    assert eff == 0.25

    eff_perfect = ActionStatistics.calculate_efficiency_score(agent_actions=8, human_baseline_actions=10)
    # min(10/8, 1.0)^2 = 1.0
    assert eff_perfect == 1.0
