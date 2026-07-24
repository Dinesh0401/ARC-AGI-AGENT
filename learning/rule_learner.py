from world_model.transition_model import TransitionModel
from memory.semantic import SemanticMemory
from perception.scene_graph import SceneGraph

class RuleLearner:
    """Learns rules by observing what ACTUALLY changed vs what was predicted."""
    
    def __init__(self, transition_model: TransitionModel, semantic_memory: SemanticMemory):
        self.transition_model = transition_model
        self.semantic = semantic_memory
        
    def learn_from_transition(self, pre_state: SceneGraph, action: str, actual_post_state: SceneGraph):
        """
        Compares pre_state to actual_post_state to infer transition rules.
        """
        changed = False
        # Very basic rule inference for MVP
        for obj_id, post_obj in actual_post_state.objects.items():
            pre_obj = pre_state.objects.get(obj_id)
            if pre_obj and pre_obj.color != post_obj.color:
                changed = True
                break
                
        if changed:
            # Add or update the rule in the Transition Model
            self.transition_model.add_rule(action, {"changes_color": True})
