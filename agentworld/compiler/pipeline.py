from __future__ import annotations

from typing import Any, Dict, List

from ..schema.world import WorldSpec


DEFAULT_ACTIONS = {
    "gather": {"cost": 1, "params": ["resource"]},
    "rest": {"cost": 0, "params": []},
}

ROLE_LIBRARY: Dict[str, Dict[str, Any]] = {
    "operator": {"energy": 9, "traits": {"role": "operator"}},
    "participant": {"energy": 8, "traits": {"role": "participant"}},
    "manager": {"energy": 10, "traits": {"role": "manager"}},
    "receptionist": {"energy": 9, "traits": {"role": "receptionist"}},
    "cashier": {"energy": 8, "traits": {"role": "cashier"}},
    "guide": {"energy": 9, "traits": {"role": "guide"}},
    "doctor": {"energy": 9, "traits": {"role": "doctor"}},
    "professor": {"energy": 9, "traits": {"role": "professor"}},
    "student": {"energy": 8, "traits": {"role": "student"}},
    "researcher": {"energy": 8, "traits": {"role": "researcher"}},
}


def _compile_from_world_dsl(scene: Dict[str, Any]) -> Dict[str, Any]:
    world = scene.get("world", {})
    entities: List[Dict[str, Any]] = scene.get("entities", [])
    resource_nodes: List[Dict[str, Any]] = scene.get("resource_nodes", [])
    rules = scene.get("rules", {})

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

    metrics = scene.get("metrics", ["survival", "wealth", "stability"])
    if rules.get("queueing"):
        metrics = [*metrics, "queue_latency"]

    return {
        "name": world.get("name", "generated-world"),
        "max_ticks": world.get("max_ticks", 100),
        "actions": scene.get("actions", DEFAULT_ACTIONS),
        "initial_state": {
            "tick": 0,
            "resources": resources,
            "agents": agents,
        },
        "metrics": metrics,
        "rules": dict(rules),
        "constraints": list(scene.get("constraints", [])),
    }


def _build_ir(world_name: str, zones: List[str], roles: List[str]) -> Dict[str, Any]:
    entities: List[Dict[str, Any]] = []
    resource_nodes: List[Dict[str, Any]] = []

    for idx, role in enumerate(roles, start=1):
        tpl = ROLE_LIBRARY.get(role, ROLE_LIBRARY["participant"])
        traits = dict(tpl["traits"])
        traits["profile"] = {
            "role": role,
            "persona": "pragmatic" if role in {"participant", "student"} else "specialist",
            "strategy": "balanced",
            "visual_anchor": f"{role}-anchor",
            "allowed_actions": ["gather", "rest"],
        }
        entities.append(
            {
                "id": f"agent_{role}_{idx}",
                "type": "agent",
                "location": zones[min(idx - 1, len(zones) - 1)],
                "energy": tpl["energy"],
                "traits": traits,
            }
        )

    for z in zones:
        resource_nodes.append({"location": z, "resources": {"food": 20}})

    return {
        "version": "0.3-ir",
        "world": {"name": world_name, "max_ticks": 150},
        "entities": entities,
        "resource_nodes": resource_nodes,
        "rules": {"queueing": False, "access_control": False},
        "flows": [],
        "constraints": [],
    }


def draft_scene_ir_from_text(description: str) -> Dict[str, Any]:
    text = description.lower()

    if any(k in text for k in ["hospital", "医院", "clinic"]):
        ir = _build_ir(
            world_name="hospital-world",
            zones=["frontdesk", "cashier", "triage", "department_a", "department_b"],
            roles=["receptionist", "cashier", "guide", "doctor", "participant"],
        )
        ir["rules"]["queueing"] = True
        ir["rules"]["access_control"] = True
        ir["flows"] = ["checkin", "pay", "triage", "treat"]
        ir["constraints"] = [
            {"kind": "requires_role", "action": "treat", "roles": ["doctor"]},
            {"kind": "requires_role", "action": "pay", "roles": ["cashier", "participant"]},
        ]
        return ir

    if any(k in text for k in ["university", "大学", "lab", "课题组"]):
        ir = _build_ir(
            world_name="university-world",
            zones=["admission", "lecture_hall", "lab_alpha", "lab_beta"],
            roles=["professor", "student", "student", "researcher", "manager"],
        )
        ir["flows"] = ["enroll", "attend", "research"]
        ir["constraints"] = [
            {"kind": "requires_role", "action": "research", "roles": ["researcher", "professor", "student"]}
        ]
        return ir

    if any(k in text for k in ["service", "餐厅", "cafe", "restaurant"]):
        ir = _build_ir(
            world_name="service-world",
            zones=["hall", "counter", "kitchen"],
            roles=["operator", "participant", "manager"],
        )
        ir["flows"] = ["order", "serve", "pay"]
        return ir

    ir = _build_ir(world_name="generated-world", zones=["zone_a", "zone_b"], roles=["operator", "participant"])
    ir["flows"] = ["explore", "exchange"]
    return ir


def compile_scene(scene: Dict[str, Any]) -> WorldSpec:
    if "initial_state" in scene and "actions" in scene:
        return WorldSpec.from_dict(scene)

    if "world" in scene and "entities" in scene:
        return WorldSpec.from_dict(_compile_from_world_dsl(scene))

    raise ValueError("Unsupported scene format")
