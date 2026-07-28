import numpy as np
from typing import Any, Dict, List, Tuple
from perception.scene_graph import SceneGraph
from perception.object_parser import ObjectParser
from perception.relation_detector import RelationDetector


class FrameParser:
    """Translates official ARC JSON frames into internal SceneGraph."""
    def __init__(self):
        self.parser = ObjectParser()
        self.relation_detector = RelationDetector()

    def parse(self, latest_frame: Dict[str, Any]) -> SceneGraph:
        """Parse the official frame dictionary into a SceneGraph."""
        # Official format might have "grid" or "frame"
        grid_data = latest_frame.get("frame", latest_frame.get("grid", []))
        if isinstance(grid_data, list):
            grid = np.array(grid_data)
        else:
            grid = grid_data
            
        # arcengine sometimes returns 3D arrays (layers, y, x)
        if hasattr(grid, 'ndim') and grid.ndim == 3:
            # Collapse layers: taking the maximum value usually overlays sprites on background
            grid = np.max(grid, axis=0)
        
        objects = self.parser.parse_grid(grid)
        relations = self.relation_detector.detect_relations(objects)
        return SceneGraph(objects, relations)


class ActionAdapter:
    """Translates internal action intents into official tokens."""
    
    @staticmethod
    def to_game_action(internal_action: str) -> Any:
        """
        Convert string action to official token.
        Handles ACTION6(x, y) correctly by returning a tuple.
        """
        if internal_action == "RESET":
            return "RESET"
        elif internal_action.startswith("ACTION"):
            if internal_action.startswith("ACTION6"):
                try:
                    coords = internal_action.replace("ACTION6", "").strip("() ")
                    x_str, y_str = coords.split(",")
                    return ("ACTION6", int(x_str.strip()), int(y_str.strip()))
                except Exception:
                    return "ACTION1"
            # Extract just "ACTIONX" from the string if it's longer
            if len(internal_action) >= 7 and internal_action[:7] in ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5", "ACTION7"]:
                return internal_action[:7]
            return "ACTION1"
        else:
            return "ACTION1"
