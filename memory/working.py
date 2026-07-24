from dataclasses import dataclass, field
from typing import List, Dict, Any
import heapq

@dataclass(order=True)
class Thought:
    priority: int
    text: str = field(compare=False)
    metadata: Dict[str, Any] = field(default_factory=dict, compare=False)

class WorkingMemory:
    """Priority-based scratchpad for active thoughts and current goals."""
    
    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        # We use a list and heapq for a priority queue. 
        # Note: heapq is a min-heap, so we will store negative priorities to make it a max-heap.
        self.thoughts: List[Thought] = []
        
    def add_thought(self, text: str, priority: int = 1, metadata: Dict[str, Any] = None):
        """Add a thought with a priority (higher number = higher priority)."""
        if metadata is None:
            metadata = {}
        # Store priority as negative so that pop() returns the highest priority first
        thought = Thought(priority=-priority, text=text, metadata=metadata)
        
        heapq.heappush(self.thoughts, thought)
        
        # Enforce capacity
        if len(self.thoughts) > self.capacity:
            # We want to remove the lowest priority. Since it's a min-heap (of negative priorities),
            # the lowest priority is the LARGEST negative value. It's actually easier to just re-sort and slice.
            self.thoughts.sort()
            self.thoughts = self.thoughts[:self.capacity]
            heapq.heapify(self.thoughts)
            
    def get_thoughts(self) -> List[Thought]:
        """Return thoughts sorted by highest priority first."""
        # Return sorted list (which is natural order, i.e., most negative first)
        # Convert priority back to positive for the caller
        sorted_thoughts = sorted(self.thoughts)
        return [Thought(priority=-t.priority, text=t.text, metadata=t.metadata) for t in sorted_thoughts]
        
    def clear(self):
        """Clear the working memory."""
        self.thoughts.clear()
