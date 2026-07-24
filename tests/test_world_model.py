import pytest
from world_model import PredictionEngine
from perception.scene_graph import SceneGraph
from perception.object_parser import Object

def test_prediction_engine():
    engine = PredictionEngine()
    
    # 1. Setup mock rule in transition model
    engine.transition_model.add_rule("ACTION_TEST", {"changes_color": True})
    
    # 2. Setup initial state
    obj1 = Object(id="obj1", color=5, pixels=[], centroid=(0,0), bbox=(0,0,0,0), area=1, perimeter=1, shape="pixel")
    initial_state = SceneGraph([obj1], [])
    
    # 3. Predict known action
    prediction_known = engine.evaluate_action(initial_state, "ACTION_TEST")
    
    # Color should have changed (5 + 1 % 10 = 6)
    assert prediction_known.predicted_state.get_object("obj1").color == 6
    # We have 1 rule for ACTION_TEST, so uncertainty = 1 / (1 + 1) = 0.5. Confidence = 0.5
    assert prediction_known.uncertainty == 0.5
    assert prediction_known.confidence == 0.5
    
    # 4. Predict unknown action
    prediction_unknown = engine.evaluate_action(initial_state, "ACTION_UNKNOWN")
    
    # State should not change because no rules exist
    assert prediction_unknown.predicted_state.get_object("obj1").color == 5
    # We have 0 rules for ACTION_UNKNOWN, so uncertainty = 1 / (1 + 0) = 1.0. Confidence = 0.0
    assert prediction_unknown.uncertainty == 1.0
    assert prediction_unknown.confidence == 0.0
    
    # 5. Rollout policy
    final_state, cum_conf = engine.rollout_policy(initial_state, ["ACTION_TEST", "ACTION_TEST"])
    # Color should increment twice: 5 -> 6 -> 7
    assert final_state.get_object("obj1").color == 7
    # Confidence: 0.5 * 0.5 = 0.25
    assert cum_conf == 0.25
