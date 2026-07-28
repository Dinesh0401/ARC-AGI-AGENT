from enum import Enum, auto
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field

class HypothesisStatus(Enum):
    ACTIVE = auto()
    REJECTED = auto()
    VERIFIED = auto()

@dataclass
class Hypothesis:
    """A testable assumption about the environment."""
    id: str
    description: str
    target_object_id: Optional[str] = None
    action: Optional[str] = None
    expected_effect: Optional[str] = None
    
    confidence: float = 0.5
    status: HypothesisStatus = HypothesisStatus.ACTIVE
    
    supporting_observations: List[str] = field(default_factory=list)
    contradicting_observations: List[str] = field(default_factory=list)
    
    def add_support(self, obs_id: str, delta: float = 0.2):
        old_conf = self.confidence
        self.supporting_observations.append(obs_id)
        self.confidence = min(1.0, self.confidence + delta)
        import logging
        logging.info(f"Hypothesis confidence ({self.description}): {old_conf:.2f} -> {self.confidence:.2f}")
        if self.confidence > 0.9 and self.status != HypothesisStatus.VERIFIED:
            self.status = HypothesisStatus.VERIFIED
            logging.info(f"Hypothesis verified:\n{self.description}")
            
    def add_contradiction(self, obs_id: str, delta: float = 0.3):
        old_conf = self.confidence
        self.contradicting_observations.append(obs_id)
        self.confidence = max(0.0, self.confidence - delta)
        import logging
        logging.info(f"Hypothesis confidence ({self.description}): {old_conf:.2f} -> {self.confidence:.2f}")
        if self.confidence < 0.2 and self.status != HypothesisStatus.REJECTED:
            self.status = HypothesisStatus.REJECTED
            logging.info(f"Hypothesis rejected:\n{self.description}")

import logging

class HypothesisEngine:
    """The agent's scientific notebook, maintaining and updating testable hypotheses."""
    
    def __init__(self):
        self.hypotheses: Dict[str, Hypothesis] = {}
        self._next_id = 1
        
    def add_hypothesis(self, description: str, target_object_id: Optional[str] = None, action: Optional[str] = None, expected_effect: Optional[str] = None, initial_confidence: float = 0.5) -> str:
        """Register a new hypothesis to test."""
        # Avoid exact duplicates
        for h in self.hypotheses.values():
            if h.description == description and h.target_object_id == target_object_id and h.action == action and h.expected_effect == expected_effect:
                if h.status == HypothesisStatus.REJECTED and initial_confidence > h.confidence:
                    # Resurrect hypothesis if new evidence suggests it
                    h.status = HypothesisStatus.ACTIVE
                    h.confidence = initial_confidence
                    logging.info(f"Resurrected hypothesis: {h.description} (Conf: {h.confidence:.2f})")
                return h.id
                
        h_id = f"Hyp_{self._next_id:03d}"
        self.hypotheses[h_id] = Hypothesis(
            id=h_id,
            description=description,
            target_object_id=target_object_id,
            action=action,
            expected_effect=expected_effect,
            confidence=initial_confidence
        )
        self._next_id += 1
        logging.info(f"Generated hypothesis: {description} (Conf: {initial_confidence:.2f})")
        return h_id
        
    def get_active_hypotheses(self) -> List[Hypothesis]:
        return [h for h in self.hypotheses.values() if h.status == HypothesisStatus.ACTIVE]
        
    def get_verified_hypotheses(self) -> List[Hypothesis]:
        return [h for h in self.hypotheses.values() if h.status == HypothesisStatus.VERIFIED]
        
    def get_hypotheses_for_action(self, action: str) -> List[Hypothesis]:
        """Find active hypotheses that can be tested by taking this action."""
        return [h for h in self.get_active_hypotheses() 
                if (h.action == action or str(action) in h.description)]
                
    def evaluate_action_results(self, action: str, actual_state: 'SceneGraph', pre_state: 'SceneGraph', transition_model: 'TransitionModel'):
        """Evaluate active hypotheses against the actual observation, then update the transition model if verified."""
        import logging
        logging.info(f"Evaluating hypotheses for action: {action}")
        active_hyps = self.get_hypotheses_for_action(action)
        logging.info(f"Found {len(active_hyps)} active hypotheses matching action {action}")
        
        for hyp in active_hyps:
            # Check if expected effect occurred
            effect_occurred = False
            
            if hyp.target_object_id and hyp.target_object_id in actual_state.objects:
                current_obj = actual_state.objects[hyp.target_object_id]
                old_obj = pre_state.objects.get(hyp.target_object_id)
                
                if hyp.expected_effect == "moves":
                    if old_obj and current_obj.centroid != old_obj.centroid:
                        effect_occurred = True
                elif hyp.expected_effect == "changes_color":
                    if old_obj and current_obj.color != old_obj.color:
                        effect_occurred = True
                        
            if effect_occurred:
                hyp.add_support("obs_verified", delta=0.4)
                if hyp.status == HypothesisStatus.VERIFIED:
                    # Knowledge Transfer to planner
                    if hyp.expected_effect == "changes_color":
                        transition_model.add_rule(action, {"changes_color": True}, target_object_id=hyp.target_object_id)
            else:
                hyp.add_contradiction("obs_refuted", delta=0.4)
