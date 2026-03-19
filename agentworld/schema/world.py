from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class ActionSpec:
    name: str
    cost: int = 1
    params: List[str] = field(default_factory=list)


@dataclass
class AgentState:
    id: str
    energy: int = 10
    location: str = "start"
    inventory: Dict[str, int] = field(default_factory=dict)
    traits: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorldState:
    tick: int = 0
    resources: Dict[str, Dict[str, int]] = field(default_factory=dict)
    agents: Dict[str, AgentState] = field(default_factory=dict)


@dataclass
class WorldSpec:
    name: str
    max_ticks: int
    actions: Dict[str, ActionSpec]
    initial_state: WorldState
    metrics: List[str] = field(default_factory=lambda: ["survival", "wealth"])
    rules: Dict[str, Any] = field(default_factory=dict)
    constraints: List[Dict[str, Any]] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "WorldSpec":
        actions = {
            k: ActionSpec(name=k, cost=v.get("cost", 1), params=v.get("params", []))
            for k, v in data["actions"].items()
        }
        agents = {
            aid: AgentState(
                id=aid,
                energy=ainfo.get("energy", 10),
                location=ainfo.get("location", "start"),
                inventory=dict(ainfo.get("inventory", {})),
                traits=dict(ainfo.get("traits", {})),
            )
            for aid, ainfo in data["initial_state"].get("agents", {}).items()
        }
        state = WorldState(
            tick=data["initial_state"].get("tick", 0),
            resources={
                loc: dict(vals)
                for loc, vals in data["initial_state"].get("resources", {}).items()
            },
            agents=agents,
        )
        return WorldSpec(
            name=data["name"],
            max_ticks=data.get("max_ticks", 100),
            actions=actions,
            initial_state=state,
            metrics=data.get("metrics", ["survival", "wealth"]),
            rules=dict(data.get("rules", {})),
            constraints=list(data.get("constraints", [])),
        )
