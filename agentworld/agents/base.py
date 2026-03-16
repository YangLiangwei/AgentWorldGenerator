from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol, Any


@dataclass
class Decision:
    action: str
    params: Dict[str, Any]


class BaseAgent(Protocol):
    id: str

    def observe(self, observation: Dict[str, Any]) -> None: ...

    def decide(self) -> Decision: ...


class RuleAgent:
    """Simple baseline agent: gather food at current location if available, else rest."""

    def __init__(self, agent_id: str) -> None:
        self.id = agent_id
        self._obs: Dict[str, Any] = {}

    def observe(self, observation: Dict[str, Any]) -> None:
        self._obs = observation

    def decide(self) -> Decision:
        loc = self._obs.get("location", "start")
        resources = self._obs.get("resources", {})
        if resources.get(loc, {}).get("food", 0) > 0:
            return Decision(action="gather", params={"resource": "food"})
        return Decision(action="rest", params={})
