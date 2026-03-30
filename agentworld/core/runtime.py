from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict, Tuple

from .events import Event, EventLog, Interaction, Outcome
from ..rules import AccessRule, QueueRule, TransferRule, validate_rule_pack_config
from ..schema.world import AgentState, WorldSpec, WorldState


class ValidationError(ValueError):
    pass


class InvariantError(ValueError):
    pass


ActionHandler = Callable[[AgentState, Dict[str, Any]], Tuple[str, Dict[str, Any]]]


class SimulationRuntime:
    def __init__(self, spec: WorldSpec) -> None:
        self.spec = spec
        self.state: WorldState = deepcopy(spec.initial_state)
        self.log = EventLog()
        self._handlers: Dict[str, ActionHandler] = {}
        self._rules = []
        self._register_default_handlers()
        self._register_default_rules()

    def register_action_handler(self, action: str, handler: ActionHandler) -> None:
        self._handlers[action] = handler

    def _register_default_handlers(self) -> None:
        self.register_action_handler("gather", self._handle_gather)
        self.register_action_handler("rest", self._handle_rest)
        self.register_action_handler("move", self._handle_move)
        self.register_action_handler("transfer", self._handle_transfer)
        self.register_action_handler("enqueue", self._handle_enqueue)
        self.register_action_handler("service", self._handle_service)

    def _register_default_rules(self) -> None:
        cfg = self.spec.rules if isinstance(self.spec.rules, dict) else {}
        cfg_issues = validate_rule_pack_config(cfg)
        errors = [i for i in cfg_issues if i.level == "error"]
        if errors:
            raise ValidationError("invalid rule pack config: " + "; ".join(i.message for i in errors))

        queue_cfg = cfg.get("queue", {})
        access_cfg = cfg.get("access", {})
        transfer_cfg = cfg.get("transfer", True)
        transfer_enabled = bool(transfer_cfg if isinstance(transfer_cfg, bool) else transfer_cfg.get("enabled", True))

        self._rules.append(QueueRule(queue_map=queue_cfg.get("queues", {})))
        self._rules.append(AccessRule(policies=access_cfg.get("policies", {})))
        if transfer_enabled:
            self._rules.append(TransferRule())

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
            return {
                "id": object_id,
                "kind": "resource_node",
                "resources": dict(self.state.resources[object_id]),
            }
        raise ValidationError(f"unknown object: {object_id}")

    def _check_constraints(self, actor_id: str, action: str) -> None:
        actor = self.state.agents[actor_id]
        for c in self.spec.constraints:
            if c.get("action") != action:
                continue
            kind = c.get("kind")
            if kind == "requires_role":
                allowed = set(c.get("roles", []))
                if actor.traits.get("role") not in allowed:
                    raise ValidationError(f"constraint failed: action '{action}' requires role in {sorted(allowed)}")

    def _pre_validate(self, actor_id: str, action: str, params: Dict[str, Any]) -> None:
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

    def _rule_validate(self, actor_id: str, action: str, params: Dict[str, Any]) -> None:
        self._check_constraints(actor_id, action)
        for rule in self._rules:
            try:
                rule.validate(self, actor_id, action, params)
            except ValueError as e:
                raise ValidationError(str(e)) from e

    def _invariant_check(self) -> None:
        for aid, a in self.state.agents.items():
            if a.energy < 0:
                raise InvariantError(f"invariant violated: agent {aid} has negative energy")
            for res, amount in a.inventory.items():
                if amount < 0:
                    raise InvariantError(f"invariant violated: agent {aid} inventory {res} is negative")
        for loc, pool in self.state.resources.items():
            for res, amount in pool.items():
                if amount < 0:
                    raise InvariantError(f"invariant violated: resource {res} at {loc} is negative")

    def validate_action(self, actor_id: str, action: str, params: Dict[str, Any]) -> None:
        self._pre_validate(actor_id, action, params)
        self._rule_validate(actor_id, action, params)

    def step_action(self, actor_id: str, action: str, params: Dict[str, Any]) -> Outcome:
        interaction = Interaction(actor_id=actor_id, action=action, params=params)
        return self.apply_interaction(interaction)

    def _handle_gather(self, agent: AgentState, params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        resource = params["resource"]
        available = self.state.resources.get(agent.location, {}).get(resource, 0)
        if available <= 0:
            return "fail:no_resource", {}

        self.state.resources[agent.location][resource] -= 1
        agent.inventory[resource] = agent.inventory.get(resource, 0) + 1
        return "ok:gather", {"inventory": {resource: 1}, "resource_node": {agent.location: {resource: -1}}}

    def _handle_rest(self, agent: AgentState, params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        prev = agent.energy
        agent.energy = min(agent.energy + 1, 10)
        return "ok:rest", {"restored": agent.energy - prev}

    def _handle_move(self, agent: AgentState, params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        new_location = str(params["location"])
        if new_location not in self.state.resources:
            return "fail:unknown_location", {}
        old = agent.location
        agent.location = new_location
        return "ok:move", {"location": {"from": old, "to": new_location}}

    def _handle_transfer(self, agent: AgentState, params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        resource = str(params["resource"])
        amount = int(params["amount"])
        target = self.state.agents[str(params["target_id"])]
        agent.inventory[resource] = agent.inventory.get(resource, 0) - amount
        target.inventory[resource] = target.inventory.get(resource, 0) + amount
        return "ok:transfer", {"transfer": {"resource": resource, "amount": amount, "to": target.id}}

    def _handle_enqueue(self, agent: AgentState, params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        return "ok:enqueue", {"queue": {"queue_id": params.get("queue_id", "default"), "action": "enqueue"}}

    def _handle_service(self, agent: AgentState, params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        return "ok:service", {"queue": {"queue_id": params.get("queue_id", "default"), "action": "service"}}

    def apply_interaction(self, interaction: Interaction) -> Outcome:
        # lifecycle: pre_validate -> rule_validate -> resolve -> rule_after -> emit_event -> invariant_check
        self.validate_action(interaction.actor_id, interaction.action, interaction.params)

        agent = self.state.agents[interaction.actor_id]
        cost = self.spec.actions[interaction.action].cost
        before_energy = agent.energy
        agent.energy -= cost
        delta: Dict[str, Any] = {"energy": agent.energy - before_energy}

        handler = self._handlers.get(interaction.action)
        if handler is None:
            result, action_delta = "ok:noop", {}
        else:
            result, action_delta = handler(agent, interaction.params)
        delta.update(action_delta)

        for rule in self._rules:
            rule.after_action(self, interaction.actor_id, interaction.action, interaction.params, result)

        self.log.append(
            Event(
                tick=self.state.tick,
                actor_id=interaction.actor_id,
                action=interaction.action,
                payload=interaction.params,
                result=result,
            )
        )

        self._invariant_check()
        return Outcome(tick=self.state.tick, interaction=interaction, result=result, state_delta=delta)

    def end_tick(self) -> None:
        self.state.tick += 1

    def run_tick(self, decisions: Dict[str, Dict[str, Any]]) -> None:
        for actor_id, cmd in decisions.items():
            self.step_action(actor_id, cmd["action"], cmd.get("params", {}))
        self.end_tick()
