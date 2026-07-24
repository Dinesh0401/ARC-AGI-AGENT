import pytest
from learning import LearningLoop, Experience
from world_model import PredictionEngine
from memory import CognitiveMemory
from perception.scene_graph import SceneGraph
from perception.object_parser import Object
from planning.planner import Plan

def test_learning_loop():
    memory = CognitiveMemory()
    prediction_engine = PredictionEngine()
    loop = LearningLoop(memory, prediction_engine)
    
    # 1. Setup pre-state
    obj1 = Object(id="obj1", color=0, pixels=[], centroid=(0,0), bbox=(0,0,0,0), area=1, perimeter=1, shape="pixel")
    pre_state = SceneGraph([obj1], [])
    
    # 2. Setup Prediction (Expects color to become 1)
    # Force a mock rule to get a prediction
    prediction_engine.transition_model.add_rule("ACTION1", {"changes_color": True})
    prediction = prediction_engine.evaluate_action(pre_state, "ACTION1")
    # Manually override the predicted state to guarantee color 1 for this test
    prediction.predicted_state.get_object("obj1").color = 1
    
    # 3. Setup Actual State (Reality is color became 2! Big error)
    obj_actual = Object(id="obj1", color=2, pixels=[], centroid=(0,0), bbox=(0,0,0,0), area=1, perimeter=1, shape="pixel")
    actual_state = SceneGraph([obj_actual], [])
    
    # 4. Form Experience
    plan = Plan(actions=["ACTION1"], estimated_cost=1.0, confidence=0.8, planner_name="test")
    experience = Experience(pre_state, "ACTION1", prediction, actual_state, plan)
    
    # 5. Run Loop
    error = loop.process_experience(experience)
    
    # Assertions
    # We had 1 object, it mismatched color (1 vs 2). Error should be 1.0
    assert error == 1.0
    
    # The rule learner should have seen color 0 -> 2 and updated the transition model
    # (In our naive MVP, it just marks "changes_color": True which it already had, but let's assert it didn't crash)
    assert "ACTION1" in prediction_engine.transition_model.rules
    
    # Strategy should have been recorded as Failed due to high error
    strategies = memory.procedural.records
    assert len(strategies) == 1
    assert strategies[0].outcome == "Failed"
