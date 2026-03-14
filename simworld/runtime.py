from __future__ import annotations

from copy import deepcopy
from typing import Dict, Any

from .events import Event, EventLog, Interaction, Outcome
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

    def get_object(self, object_id: str) -> Dict[str, Any]:
        """Object atom: return a typed snapshot for an object in world state."""
        if object_id in self.state.agents:
            a = self.state.agents[object_id]
            return {
                "id": a.id,
                "kind": "agent",
                "location": a.location,
                "energy": a.energy,
                "inventory": dict(a.inventory),
                "traits": dict(a.traits),
            }
        if object_id in self.state.resources:
            return {"id": object_id, "kind": "resource_node", "resources": dict(self.state.resources[object_id])}
        raise ValidationError(f"unknown object: {object_id}")

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

    def step_action(self, actor_id: str, action: str, params: Dict[str, Any]) -> Outcome:
        interaction = Interaction(actor_id=actor_id, action=action, params=params)
        return self.apply_interaction(interaction)

    def apply_interaction(self, interaction: Interaction) -> Outcome:
        """Interaction atom -> Outcome atom via deterministic rule resolution."""
        self.validate_action(interaction.actor_id, interaction.action, interaction.params)
        agent = self.state.agents[interaction.actor_id]
        cost = self.spec.actions[interaction.action].cost
        before_energy = agent.energy
        agent.energy -= cost
        delta: Dict[str, Any] = {"energy": agent.energy - before_energy}

        if interaction.action == "gather":
            resource = interaction.params["resource"]
            available = self.state.resources.get(agent.location, {}).get(resource, 0)
            if available > 0:
                self.state.resources[agent.location][resource] -= 1
                agent.inventory[resource] = agent.inventory.get(resource, 0) + 1
                result = "ok:gather"
                delta.update({"inventory": {resource: 1}, "resource_node": {agent.location: {resource: -1}}})
            else:
                result = "fail:no_resource"
        elif interaction.action == "rest":
            prev = agent.energy
            agent.energy = min(agent.energy + 1, 10)
            result = "ok:rest"
            delta["energy"] = agent.energy - before_energy
            delta["restored"] = agent.energy - prev
        else:
            result = "ok:noop"

        self.log.append(
            Event(
                tick=self.state.tick,
                actor_id=interaction.actor_id,
                action=interaction.action,
                payload=interaction.params,
                result=result,
            )
        )
        return Outcome(tick=self.state.tick, interaction=interaction, result=result, state_delta=delta)

    def end_tick(self) -> None:
        self.state.tick += 1

    def run_tick(self, decisions: Dict[str, Dict[str, Any]]) -> None:
        for actor_id, cmd in decisions.items():
            self.step_action(actor_id, cmd["action"], cmd.get("params", {}))
        self.end_tick()
