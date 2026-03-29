from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentProfile:
    """Agent behavior + rendering identity profile (v1)."""

    id: str
    role: str = "participant"
    persona: str = "pragmatic"
    strategy: str = "balanced"
    visual_anchor: str = "simple-uniform"
    allowed_actions: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(agent_id: str, data: Dict[str, Any]) -> "AgentProfile":
        return AgentProfile(
            id=agent_id,
            role=str(data.get("role", "participant")),
            persona=str(data.get("persona", "pragmatic")),
            strategy=str(data.get("strategy", "balanced")),
            visual_anchor=str(data.get("visual_anchor", "simple-uniform")),
            allowed_actions=list(data.get("allowed_actions", [])),
        )


_DEFAULT_BY_ROLE: Dict[str, Dict[str, Any]] = {
    "manager": {"persona": "coordinator", "strategy": "risk-aware", "visual_anchor": "formal-badge"},
    "doctor": {"persona": "careful", "strategy": "service-first", "visual_anchor": "white-coat"},
    "professor": {"persona": "analytical", "strategy": "long-term", "visual_anchor": "academic-jacket"},
    "cashier": {"persona": "precise", "strategy": "queue-efficient", "visual_anchor": "counter-uniform"},
    "receptionist": {"persona": "friendly", "strategy": "flow-first", "visual_anchor": "frontdesk-uniform"},
    "student": {"persona": "curious", "strategy": "explore", "visual_anchor": "student-casual"},
    "participant": {"persona": "pragmatic", "strategy": "balanced", "visual_anchor": "simple-uniform"},
}


def default_profile(agent_id: str, role: Optional[str] = None) -> AgentProfile:
    role_key = role or "participant"
    base = _DEFAULT_BY_ROLE.get(role_key, _DEFAULT_BY_ROLE["participant"])
    return AgentProfile(id=agent_id, role=role_key, **base)
