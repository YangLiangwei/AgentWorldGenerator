from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ActionProposal:
    action: str
    params: Dict[str, Any]
    rationale: str
    expected: str


def validate_proposals(runtime: Any, actor_id: str, proposals: List[ActionProposal]) -> List[ActionProposal]:
    valid: List[ActionProposal] = []
    for p in proposals:
        try:
            runtime.validate_action(actor_id, p.action, p.params)
            valid.append(p)
        except Exception:
            continue
    return valid[:3]
