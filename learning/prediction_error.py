from perception.scene_graph import SceneGraph
from world_model.state_predictor import Prediction

class PredictionErrorCalculator:
    """Compares the Predicted state against the Actual state to determine the error delta."""
    
    def calculate_error(self, prediction: Prediction, actual_state: SceneGraph) -> float:
        """
        Returns a float between 0.0 (perfect match) and 1.0 (complete mismatch).
        """
        if prediction is None:
            return 1.0  # No prediction available (e.g. world model disabled)
        predicted_state = prediction.predicted_state
        
        # Simple heuristic for MVP: Compare object colors
        mismatches = 0
        total_objects = max(len(predicted_state.objects), 1)
        
        for obj_id, p_obj in predicted_state.objects.items():
            a_obj = actual_state.objects.get(obj_id)
            if not a_obj or a_obj.color != p_obj.color:
                mismatches += 1
                
        # Also check if objects exist in actual but not predicted
        for obj_id in actual_state.objects:
            if obj_id not in predicted_state.objects:
                mismatches += 1
                total_objects += 1
                
        return min(1.0, float(mismatches) / float(total_objects))
