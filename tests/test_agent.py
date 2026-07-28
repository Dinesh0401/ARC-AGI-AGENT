"""Unit tests for RandomAgent and BaseAgent."""

import pytest
from agents.random_agent import RandomAgent


def test_random_agent_initialization() -> None:
    agent = RandomAgent(name="TestAgent", seed=42)
    assert agent.name == "TestAgent"
    assert agent.step_count == 0
    assert len(agent.history.records) == 0


def test_random_agent_act() -> None:
    agent = RandomAgent(name="TestAgent", seed=42)
    observation = {"available_actions": ["ACTION1", "ACTION2", "ACTION3", "ACTION4"]}
    action = agent.choose_action([observation], observation)
    # The action returned is now an official GameAction. We mock it for the test.
    # In absence of GameAction, our adapter returns the string "ACTION1" etc or the action object.
    assert str(action) in ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "GameAction.ACTION1", "GameAction.ACTION2", "GameAction.ACTION3", "GameAction.ACTION4"]


def test_random_agent_record_and_reset() -> None:
    agent = RandomAgent(name="TestAgent", seed=42)
    obs = {"available_actions": ["ACTION1", "ACTION2"]}
    action = agent.choose_action([obs], obs)
    agent.record_step(obs, action, reward=1.0, status="NOT_FINISHED")

    assert agent.step_count == 1
    assert len(agent.history.records) == 1
    assert len(agent.observation_history) == 1

    agent.reset()
    assert agent.step_count == 0
    assert len(agent.history.records) == 0
    assert len(agent.observation_history) == 0
