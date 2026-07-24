"""LRU Cache Manager for scene parsing & prediction reuse."""

from typing import Dict, Any, Optional
from collections import OrderedDict


class CacheManager:
    """Least Recently Used (LRU) Cache Manager for SceneGraphs and Predictions."""

    def __init__(self, max_entries: int = 1000) -> None:
        self.max_entries = max_entries
        self.scene_cache: OrderedDict[str, Any] = OrderedDict()
        self.prediction_cache: OrderedDict[str, Any] = OrderedDict()

    def get_scene(self, scene_hash: str) -> Optional[Any]:
        if scene_hash in self.scene_cache:
            self.scene_cache.move_to_end(scene_hash)
            return self.scene_cache[scene_hash]
        return None

    def put_scene(self, scene_hash: str, scene_graph: Any) -> None:
        if scene_hash in self.scene_cache:
            self.scene_cache.move_to_end(scene_hash)
        self.scene_cache[scene_hash] = scene_graph
        if len(self.scene_cache) > self.max_entries:
            self.scene_cache.popitem(last=False)

    def get_prediction(self, pred_key: str) -> Optional[Any]:
        if pred_key in self.prediction_cache:
            self.prediction_cache.move_to_end(pred_key)
            return self.prediction_cache[pred_key]
        return None

    def put_prediction(self, pred_key: str, prediction: Any) -> None:
        if pred_key in self.prediction_cache:
            self.prediction_cache.move_to_end(pred_key)
        self.prediction_cache[pred_key] = prediction
        if len(self.prediction_cache) > self.max_entries:
            self.prediction_cache.popitem(last=False)

    def clear(self) -> None:
        self.scene_cache.clear()
        self.prediction_cache.clear()
