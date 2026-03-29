from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol

from .profile import AgentProfile


@dataclass
class Decision:
    action: str
    params: Dict[str, Any]


class BaseAgent(Protocol):
    id: str

    def observe(self, observation: Dict[str, Any]) -> None: ...

    def decide(self) -> Decision: ...


class RuleAgent:
    """Simple baseline agent with optional AgentProfile constraints."""

    def __init__(self, agent_id: str, profile: AgentProfile | None = None) -> None:
        self.id = agent_id
        self.profile = profile
        self._obs: Dict[str, Any] = {}

    def observe(self, observation: Dict[str, Any]) -> None:
        self._obs = observation

    def _enforce_profile(self, decision: Decision) -> Decision:
        if not self.profile or not self.profile.allowed_actions:
            return decision
        if decision.action in self.profile.allowed_actions:
            return decision
        return Decision(action="rest", params={})

    def decide(self) -> Decision:
        loc = self._obs.get("location", "start")
        resources = self._obs.get("resources", {})

        decision = Decision(action="rest", params={})
        if resources.get(loc, {}).get("food", 0) > 0:
            decision = Decision(action="gather", params={"resource": "food"})

        return self._enforce_profile(decision)
