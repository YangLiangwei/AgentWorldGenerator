from __future__ import annotations

from typing import Any, Dict, List

from .spec import WorldSpec


DEFAULT_ACTIONS = {
    "gather": {"cost": 1, "params": ["resource"]},
    "rest": {"cost": 0, "params": []},
}


def _compile_from_world_dsl(scene: Dict[str, Any]) -> Dict[str, Any]:
    """Compile v0.2 world DSL into runtime WorldSpec dict.

    DSL shape:
      {
        "version": "0.2",
        "world": {"name": str, "max_ticks": int},
        "entities": [{"id": str, "type": "agent", "location": str, "energy": int}],
        "resource_nodes": [{"location": str, "resources": {"food": 10}}],
        "actions": {... optional ...},
        "metrics": [... optional ...]
      }
    """
    world = scene.get("world", {})
    entities: List[Dict[str, Any]] = scene.get("entities", [])
    resource_nodes: List[Dict[str, Any]] = scene.get("resource_nodes", [])

    agents: Dict[str, Dict[str, Any]] = {}
    for ent in entities:
        if ent.get("type", "agent") != "agent":
            continue
        aid = ent["id"]
        agents[aid] = {
            "energy": ent.get("energy", 10),
            "location": ent.get("location", "start"),
            "inventory": ent.get("inventory", {}),
            "traits": ent.get("traits", {}),
        }

    resources: Dict[str, Dict[str, int]] = {}
    for node in resource_nodes:
        loc = node["location"]
        resources[loc] = dict(node.get("resources", {}))

    return {
        "name": world.get("name", "generated-world"),
        "max_ticks": world.get("max_ticks", 100),
        "actions": scene.get("actions", DEFAULT_ACTIONS),
        "initial_state": {
            "tick": 0,
            "resources": resources,
            "agents": agents,
        },
        "metrics": scene.get("metrics", ["survival", "wealth", "stability"]),
    }


def draft_scene_ir_from_text(description: str) -> Dict[str, Any]:
    """Heuristic text->Scene IR draft.

    This is intentionally deterministic and lightweight for MVP.
    """
    text = description.lower()
    name = "service-world" if "service" in text or "餐厅" in description else "generated-world"
    has_manager = "manager" in text or "经理" in description

    entities = [
        {"id": "agent_waiter_1", "type": "agent", "location": "hall", "traits": {"job": "waiter"}},
        {"id": "agent_customer_1", "type": "agent", "location": "hall", "traits": {"job": "customer"}},
    ]
    if has_manager:
        entities.append(
            {"id": "agent_manager_1", "type": "agent", "location": "desk", "traits": {"job": "manager"}}
        )

    return {
        "version": "0.2",
        "world": {"name": name, "max_ticks": 120},
        "entities": entities,
        "resource_nodes": [
            {"location": "hall", "resources": {"food": 20}},
            {"location": "kitchen", "resources": {"food": 50}},
        ],
    }


def compile_scene(scene: Dict[str, Any]) -> WorldSpec:
    """Compile structured input into WorldSpec.

    Supports:
    - Legacy v0.1 runtime dict (already contains `initial_state` + `actions`)
    - v0.2 world DSL (`world` + `entities` + `resource_nodes`)
    """
    if "initial_state" in scene and "actions" in scene:
        return WorldSpec.from_dict(scene)

    if "world" in scene and "entities" in scene:
        return WorldSpec.from_dict(_compile_from_world_dsl(scene))

    raise ValueError("Unsupported scene format")
