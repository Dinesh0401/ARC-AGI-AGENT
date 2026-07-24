import pytest
from research import StatisticalAnalyzer, AblationStudyRunner, ResearchExperimentRunner
from agents.cognitive_agent import CognitiveAgent


def test_statistical_analyzer():
    values = [10.0, 12.0, 14.0, 16.0, 18.0]
    stats = StatisticalAnalyzer.calculate_stats(values)

    assert stats["mean"] == 14.0
    assert stats["median"] == 14.0
    assert stats["std_dev"] > 0.0
    assert stats["ci_95"] > 0.0


def test_cognitive_agent_ablation_toggles():
    agent = CognitiveAgent(
        enable_memory=False,
        enable_world_model=False,
        enable_planning=False,
        enable_learning=False,
    )

    assert agent.enable_memory is False
    assert agent.enable_world_model is False
    assert agent.enable_planning is False
    assert agent.enable_learning is False


def test_ablation_study_runner(tmp_path):
    runner = AblationStudyRunner(output_dir=tmp_path)
    results = runner.run_ablation_study(num_episodes=1, max_steps=2, game_id="sample_game")

    assert "Random Baseline" in results
    assert "Full Cognitive Agent" in results
    assert "w/o Memory" in results
    assert "w/o World Model" in results
    assert "w/o Planning" in results
    assert "w/o Learning" in results
    assert (tmp_path / "ablation_report.md").exists()


def test_research_experiment_runner(tmp_path):
    runner = ResearchExperimentRunner(output_dir=tmp_path)
    rq_summary = runner.run_all_experiments(num_episodes=1, max_steps=2)

    assert "RQ1_Perception_Impact" in rq_summary
    assert "RQ2_World_Model_Impact" in rq_summary
    assert (tmp_path / "research_questions_report.md").exists()
