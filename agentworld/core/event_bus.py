from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Dict, List


class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        self._subs[topic].append(handler)

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        for h in self._subs.get(topic, []):
            h(payload)
