from __future__ import annotations

from copy import deepcopy
from typing import Dict, Any

from .events import Event, EventLog
from .spec import WorldSpec, WorldState


class ValidationError(ValueError):
    pass


class SimulationRuntime:
    def __init__(self, spec: WorldSpec) -> None:
        self.spec = spec
        self.state: WorldState = deepcopy(spec.initial_state)
        self.log = EventLog()

    def observe(self, agent_id: str) -> Dict[str, Any]:
        agent = self.state.agents[agent_id]
        return {
            "tick": self.state.tick,
            "location": agent.location,
            "energy": agent.energy,
            "inventory": dict(agent.inventory),
            "resources": deepcopy(self.state.resources),
        }

    def validate_action(self, actor_id: str, action: str, params: Dict[str, Any]) -> None:
        if action not in self.spec.actions:
            raise ValidationError(f"unknown action: {action}")
        if actor_id not in self.state.agents:
            raise ValidationError(f"unknown actor: {actor_id}")
        spec_action = self.spec.actions[action]
        for required in spec_action.params:
            if required not in params:
                raise ValidationError(f"missing action param: {required}")
        if self.state.agents[actor_id].energy < spec_action.cost:
            raise ValidationError("not enough energy")

    def step_action(self, actor_id: str, action: str, params: Dict[str, Any]) -> None:
        self.validate_action(actor_id, action, params)
        agent = self.state.agents[actor_id]
        cost = self.spec.actions[action].cost
        agent.energy -= cost

        if action == "gather":
            resource = params["resource"]
            available = self.state.resources.get(agent.location, {}).get(resource, 0)
            if available > 0:
                self.state.resources[agent.location][resource] -= 1
                agent.inventory[resource] = agent.inventory.get(resource, 0) + 1
                result = "ok:gather"
            else:
                result = "fail:no_resource"
        elif action == "rest":
            agent.energy = min(agent.energy + 1, 10)
            result = "ok:rest"
        else:
            result = "ok:noop"

        self.log.append(
            Event(
                tick=self.state.tick,
                actor_id=actor_id,
                action=action,
                payload=params,
                result=result,
            )
        )

    def end_tick(self) -> None:
        self.state.tick += 1

    def run_tick(self, decisions: Dict[str, Dict[str, Any]]) -> None:
        for actor_id, cmd in decisions.items():
            self.step_action(actor_id, cmd["action"], cmd.get("params", {}))
        self.end_tick()
