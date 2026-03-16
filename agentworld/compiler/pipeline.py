from __future__ import annotations

from typing import Any, Dict, List

from ..schema.world import WorldSpec


DEFAULT_ACTIONS = {
    "gather": {"cost": 1, "params": ["resource"]},
    "rest": {"cost": 0, "params": []},
}


def _compile_from_world_dsl(scene: Dict[str, Any]) -> Dict[str, Any]:
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
    text = description.lower()
    name = "service-world" if "service" in text or "餐厅" in description else "generated-world"
    has_manager = "manager" in text or "经理" in description

    entities = [
        {"id": "agent_role_1", "type": "agent", "location": "zone_a", "traits": {"role": "operator"}},
        {"id": "agent_role_2", "type": "agent", "location": "zone_a", "traits": {"role": "participant"}},
    ]
    if has_manager:
        entities.append(
            {"id": "agent_manager_1", "type": "agent", "location": "control", "traits": {"role": "manager"}}
        )

    return {
        "version": "0.2",
        "world": {"name": name, "max_ticks": 120},
        "entities": entities,
        "resource_nodes": [
            {"location": "zone_a", "resources": {"food": 20}},
            {"location": "zone_b", "resources": {"food": 50}},
        ],
    }


def compile_scene(scene: Dict[str, Any]) -> WorldSpec:
    if "initial_state" in scene and "actions" in scene:
        return WorldSpec.from_dict(scene)

    if "world" in scene and "entities" in scene:
        return WorldSpec.from_dict(_compile_from_world_dsl(scene))

    raise ValueError("Unsupported scene format")
