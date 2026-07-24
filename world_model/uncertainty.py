class UncertaintyQuantifier:
    """Evaluates the epistemic and aleatoric uncertainty of a prediction."""
    
    def calculate_uncertainty(self, action: str, known_rules_count: int) -> float:
        """
        Estimates how uncertain we are about the outcome of an action.
        If we have 0 known rules for this action, uncertainty is maximum (1.0).
        """
        if known_rules_count == 0:
            return 1.0
            
        # Simplified uncertainty heuristic: 1 / (1 + known_rules)
        return 1.0 / (1.0 + known_rules_count)
