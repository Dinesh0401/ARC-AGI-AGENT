"""Unit tests for RandomAgent and BaseAgent."""

import pytest
from agents.random_agent import RandomAgent


def test_random_agent_initialization() -> None:
    agent = RandomAgent(name="TestAgent", seed=42)
    assert agent.name == "TestAgent"
    assert agent.step_count == 0
    assert len(agent.action_history) == 0


def test_random_agent_act() -> None:
    agent = RandomAgent(name="TestAgent", seed=42)
    observation = {"available_actions": [0, 1, 2, 3]}
    action = agent.act(observation)
    assert action in [0, 1, 2, 3]


def test_random_agent_record_and_reset() -> None:
    agent = RandomAgent(name="TestAgent", seed=42)
    obs = {"available_actions": [0, 1]}
    action = agent.act(obs)
    agent.record_step(obs, action, reward=1.0, done=False)

    assert agent.step_count == 1
    assert len(agent.action_history) == 1
    assert len(agent.observation_history) == 1

    agent.reset()
    assert agent.step_count == 0
    assert len(agent.action_history) == 0
    assert len(agent.observation_history) == 0
