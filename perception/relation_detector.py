from typing import List, Tuple, Any
import math
from .object_parser import Object

def detect_relations(objects: List[Object]) -> List[Tuple[str, str, Any]]:
    """Detect relationships between objects.
    Returns a list of tuples: (source_id, relation_type, target_id_or_value)
    """
    relations = []
    
    for i, obj_a in enumerate(objects):
        for j, obj_b in enumerate(objects):
            if i == j:
                continue
                
            # Same Color
            if obj_a.color == obj_b.color:
                relations.append((obj_a.id, "Same Color", obj_b.id))
                
            # Same Shape
            if obj_a.shape == obj_b.shape and obj_a.shape not in ("irregular", "empty"):
                relations.append((obj_a.id, "Same Shape", obj_b.id))
                
            # Same Area
            if obj_a.area == obj_b.area:
                relations.append((obj_a.id, "Same Area", obj_b.id))
                
            amin_r, amin_c, amax_r, amax_c = obj_a.bbox
            bmin_r, bmin_c, bmax_r, bmax_c = obj_b.bbox
            
            # Aligned Horizontally (same min_r or max_r, etc.)
            if amin_r == bmin_r or amax_r == bmax_r:
                relations.append((obj_a.id, "Aligned Horizontally", obj_b.id))
                
            # Aligned Vertically
            if amin_c == bmin_c or amax_c == bmax_c:
                relations.append((obj_a.id, "Aligned Vertically", obj_b.id))
                
            # Inside (A is entirely inside B's bounding box)
            if amin_r >= bmin_r and amax_r <= bmax_r and amin_c >= bmin_c and amax_c <= bmax_c:
                relations.append((obj_a.id, "Inside", obj_b.id))
            
            # Contains (A contains B)
            if amin_r <= bmin_r and amax_r >= bmax_r and amin_c <= bmin_c and amax_c >= bmax_c:
                relations.append((obj_a.id, "Contains", obj_b.id))
                
            # Overlaps / Intersects (bbox intersection)
            if not (amax_c < bmin_c or amin_c > bmax_c or amax_r < bmin_r or amin_r > bmax_r):
                relations.append((obj_a.id, "Overlaps", obj_b.id))
                
            # Left Of
            if amax_c < bmin_c:
                relations.append((obj_a.id, "Left Of", obj_b.id))
            # Right Of
            if amin_c > bmax_c:
                relations.append((obj_a.id, "Right Of", obj_b.id))
            # Above
            if amax_r < bmin_r:
                relations.append((obj_a.id, "Above", obj_b.id))
            # Below
            if amin_r > bmax_r:
                relations.append((obj_a.id, "Below", obj_b.id))
                
            # Distance (Centroid distance)
            dist = math.sqrt((obj_a.centroid[0] - obj_b.centroid[0])**2 + (obj_a.centroid[1] - obj_b.centroid[1])**2)
            relations.append((obj_a.id, "Distance", {"target": obj_b.id, "value": round(dist, 2)}))
            
            # Adjacency / Touches (Min distance between pixels is 1)
            if not (amax_c < bmin_c - 1 or amin_c > bmax_c + 1 or amax_r < bmin_r - 1 or amin_r > bmax_r + 1):
                set_b = set(obj_b.pixels)
                is_adj = False
                for r, c in obj_a.pixels:
                    if (r-1, c) in set_b or (r+1, c) in set_b or (r, c-1) in set_b or (r, c+1) in set_b:
                        is_adj = True
                        break
                if is_adj:
                    relations.append((obj_a.id, "Touches", obj_b.id))
                    relations.append((obj_a.id, "Adjacent", obj_b.id))
                    
    return relations
