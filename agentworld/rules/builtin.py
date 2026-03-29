from __future__ import annotations

from typing import Any, Dict, List

from .base import RuleMiddleware


class QueueRule(RuleMiddleware):
    name = "queue"

    def __init__(self, queue_map: Dict[str, List[str]] | None = None) -> None:
        self.queues: Dict[str, List[str]] = dict(queue_map or {})

    def validate(self, runtime: Any, actor_id: str, action: str, params: Dict[str, Any]) -> None:
        if action == "service":
            qid = params.get("queue_id", "default")
            q = self.queues.get(qid, [])
            if not q or q[0] != actor_id:
                raise ValueError(f"queue violation: actor {actor_id} is not at head of queue '{qid}'")

    def after_action(self, runtime: Any, actor_id: str, action: str, params: Dict[str, Any], result: str) -> None:
        qid = params.get("queue_id", "default")
        if action == "enqueue" and result.startswith("ok:"):
            q = self.queues.setdefault(qid, [])
            if actor_id not in q:
                q.append(actor_id)
        if action == "service" and result.startswith("ok:"):
            q = self.queues.get(qid, [])
            if q and q[0] == actor_id:
                q.pop(0)


class AccessRule(RuleMiddleware):
    name = "access"

    def __init__(self, policies: Dict[str, List[str]] | None = None) -> None:
        # policy key format: "<action>@<location>" => allowed roles
        self.policies = dict(policies or {})

    def validate(self, runtime: Any, actor_id: str, action: str, params: Dict[str, Any]) -> None:
        actor = runtime.state.agents[actor_id]
        location = params.get("location", actor.location)
        key = f"{action}@{location}"
        allowed = self.policies.get(key)
        if not allowed:
            return
        role = actor.traits.get("role")
        if role not in set(allowed):
            raise ValueError(f"access denied: role '{role}' cannot do {action} at {location}")

    def after_action(self, runtime: Any, actor_id: str, action: str, params: Dict[str, Any], result: str) -> None:
        return None


class TransferRule(RuleMiddleware):
    name = "transfer"

    def validate(self, runtime: Any, actor_id: str, action: str, params: Dict[str, Any]) -> None:
        if action != "transfer":
            return
        resource = params.get("resource")
        amount = int(params.get("amount", 0))
        target_id = params.get("target_id")
        if not resource or amount <= 0 or not target_id:
            raise ValueError("transfer requires resource, positive amount, and target_id")
        if target_id not in runtime.state.agents:
            raise ValueError(f"unknown transfer target: {target_id}")

        actor = runtime.state.agents[actor_id]
        if actor.inventory.get(resource, 0) < amount:
            raise ValueError("transfer denied: insufficient inventory")

    def after_action(self, runtime: Any, actor_id: str, action: str, params: Dict[str, Any], result: str) -> None:
        return None
