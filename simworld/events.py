from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional
import json


@dataclass
class Event:
    tick: int
    actor_id: str
    action: str
    payload: Dict[str, Any]
    result: str


@dataclass
class Interaction:
    actor_id: str
    action: str
    params: Dict[str, Any]
    target_id: Optional[str] = None


@dataclass
class Outcome:
    tick: int
    interaction: Interaction
    result: str
    state_delta: Dict[str, Any]


class EventLog:
    def __init__(self) -> None:
        self._events: List[Event] = []

    def append(self, event: Event) -> None:
        self._events.append(event)

    def all(self) -> List[Event]:
        return list(self._events)

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(asdict(e), ensure_ascii=False) for e in self._events)

    @staticmethod
    def from_jsonl(lines: Iterable[str]) -> "EventLog":
        log = EventLog()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            log.append(Event(**obj))
        return log
