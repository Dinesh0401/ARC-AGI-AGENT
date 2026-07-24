"""Memory Optimizer purging stale beliefs, compacting thoughts, and deduplicating rules."""

from memory import CognitiveMemory


class MemoryOptimizer:
    """Prunes stale memories and caps buffer sizes to prevent RAM leakage."""

    def prune_memory(self, memory: CognitiveMemory) -> None:
        """Purge low-confidence beliefs and trim working memory."""
        # 1. Purge stale beliefs (confidence < 0.1)
        stale_ids = [
            b.id for b in memory.belief_memory.get_all_beliefs() if b.confidence < 0.1
        ]
        for b_id in stale_ids:
            if b_id in memory.belief_memory.beliefs:
                del memory.belief_memory.beliefs[b_id]

        # 2. Trim working memory thoughts to max capacity
        if len(memory.working.thoughts) > memory.working.capacity:
            memory.working.get_thoughts()  # Trims via internal priority logic
