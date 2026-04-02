from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ScheduledAction:
    actor_id: str
    action: str
    params: Dict
    priority: int = 0


def build_schedule(decisions: Dict[str, Dict]) -> List[ScheduledAction]:
    items: List[ScheduledAction] = []
    for actor_id, cmd in decisions.items():
        items.append(
            ScheduledAction(
                actor_id=actor_id,
                action=cmd["action"],
                params=cmd.get("params", {}),
                priority=int(cmd.get("priority", 0)),
            )
        )
    # high priority first, then stable actor id tie-break
    return sorted(items, key=lambda x: (-x.priority, x.actor_id))
