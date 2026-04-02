from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


class StateStore:
    def __init__(self) -> None:
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    def snapshot(self, runtime: Any) -> Dict[str, Any]:
        return {
            "tick": runtime.state.tick,
            "resources": deepcopy(runtime.state.resources),
            "agents": {
                aid: {
                    "energy": a.energy,
                    "location": a.location,
                    "inventory": deepcopy(a.inventory),
                    "traits": deepcopy(a.traits),
                }
                for aid, a in runtime.state.agents.items()
            },
        }

    def checkpoint(self, name: str, runtime: Any) -> None:
        self._checkpoints[name] = self.snapshot(runtime)

    def get_checkpoint(self, name: str) -> Dict[str, Any]:
        return deepcopy(self._checkpoints[name])

    @staticmethod
    def diff(prev: Dict[str, Any], curr: Dict[str, Any]) -> Dict[str, Any]:
        if prev == curr:
            return {"unchanged": True}
        return {"unchanged": False, "previous": prev, "current": curr}
