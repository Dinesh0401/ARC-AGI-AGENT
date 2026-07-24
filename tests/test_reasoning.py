import pytest
from memory import CognitiveMemory
from reasoning import (
    HypothesisManager,
    InferenceEngine,
    ConfidenceTracker,
    Verifier,
    GoalGenerator
)

def test_reasoning_pipeline():
    mem = CognitiveMemory()
    hm = HypothesisManager(mem.belief_memory)
    ie = InferenceEngine(mem.semantic, mem.knowledge_base, hm)
    gg = GoalGenerator(mem.working, mem.belief_memory)
    vf = Verifier(mem.knowledge_base)
    
    # 1. Setup Rule in Semantic Memory
    mem.semantic.add_rule(
        condition={"color": 1, "shape": "square"},
        outcome={"action_or_fact": "ACTION1"}
    )
    
    # 2. Setup Fact in Knowledge Base
    mem.knowledge_base.facts["Object_001"] = {"color": 1, "shape": "square"}
    
    # 3. Inference Engine should match the rule to the fact and generate a belief
    new_beliefs = ie.infer()
    assert len(new_beliefs) == 1
    
    b_id = new_beliefs[0]
    belief = mem.belief_memory.get_belief(b_id)
    assert belief.confidence == 0.6
    assert "Applying ACTION1 on Object_001 will succeed." in belief.hypothesis
    
    # 4. Verifier check
    is_valid = vf.verify_hypothesis(belief)
    assert is_valid == True
    
    # 5. Goal Generation (Requires high confidence, let's boost it)
    ct = ConfidenceTracker(mem.belief_memory, mem.episodic)
    # Simulate a successful episode explicitly
    mem.belief_memory.update_evidence(b_id, is_supportive=True, delta_confidence=0.2)
    assert belief.confidence == 0.8
    
    goals = gg.generate_goals()
    assert len(goals) == 1
    assert goals[0].target_conditions["action"] == "ACTION1"
    assert goals[0].target_conditions["target_obj"] == "Object_001"
