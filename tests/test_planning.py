import pytest
from planning import PlanningOrchestrator, Plan
from reasoning.goal_generator import Goal
from perception.scene_graph import SceneGraph
from perception.object_parser import Object

def test_planner_finds_sequence():
    obj1 = Object(id="obj1", color=0, pixels=[], centroid=(0,0), bbox=(0,0,0,0), area=1, perimeter=1, shape="pixel")
    initial_state = SceneGraph([obj1], [])
    
    goal = Goal(
        description="Target Action Test",
        target_conditions={"action": "target_action"},
        priority=10,
        confidence=1.0,
        source="Test"
    )
    
    def test_transition(state: SceneGraph, action: str) -> SceneGraph:
        obj = state.get_object("obj1")
        new_color = obj.color + (1 if action == "move" else 0)
        new_obj = Object(id="obj1", color=new_color, pixels=[], centroid=(0,0), bbox=(0,0,0,0), area=1, perimeter=1, shape="pixel")
        return SceneGraph([new_obj], [])
        
    planner = PlanningOrchestrator(test_transition)
    available_actions = ["move", "target_action", "do_nothing"]
    
    plan = planner.generate_plan(initial_state, goal, available_actions)
    
    assert isinstance(plan, Plan)
    assert len(plan.actions) == 1
    assert plan.actions[0] == "target_action"
    # Any planner backend is acceptable
    assert plan.planner_name in ["astar", "bfs", "mcts"]
