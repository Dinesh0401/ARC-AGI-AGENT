"""Unit tests for ActionHistory and StepRecord container."""

from pathlib import Path
import tempfile
import pytest
from agents.history import ActionHistory, StepRecord


def test_step_record_to_dict() -> None:
    record = StepRecord(
        step=1,
        timestamp=1000.0,
        action=0,
        reward=0.5,
        status="NOT_FINISHED",
        diff_cells=0,
        duration_ms=12.5,
        info={"test": True},
    )
    d = record.to_dict()
    assert d["step"] == 1
    assert d["action"] == 0
    assert d["reward"] == 0.5
    assert d["duration_ms"] == 12.5
    assert d["info"]["test"] is True


def test_action_history_summary_and_serialization() -> None:
    history = ActionHistory()
    history.add_step(step=1, action=0, reward=0.0, status="NOT_FINISHED", duration_ms=10.0)
    history.add_step(step=2, action=1, reward=1.0, status="WIN", duration_ms=20.0)

    summary = history.get_summary()
    assert summary["total_steps"] == 2
    assert summary["total_reward"] == 1.0
    assert summary["action_counts"] == {"0": 1, "1": 1}
    assert summary["avg_decision_duration_ms"] == 15.0

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "history.json"
        history.save_json(json_path)
        assert json_path.exists()
        assert json_path.stat().st_size > 0


def test_action_history_clear() -> None:
    history = ActionHistory()
    history.add_step(step=1, action=0, reward=1.0, status="NOT_FINISHED")
    assert len(history.records) == 1

    history.clear()
    assert len(history.records) == 0
    assert history.total_reward == 0.0
    assert len(history.action_counts) == 0
