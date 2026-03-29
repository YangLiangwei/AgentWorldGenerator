from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional


def _stable_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _sorted_inventory(inv: Dict[str, int]) -> Dict[str, int]:
    return {k: inv[k] for k in sorted(inv.keys())}


def _sorted_resources(resources: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
    return {loc: {k: resources[loc][k] for k in sorted(resources[loc].keys())} for loc in sorted(resources.keys())}


def build_render_context(
    observation: Dict[str, Any],
    *,
    agent_id: str,
    radius: int = 1,
    camera_profile: str = "topdown",
    style_profile: str = "sim-minimal-v1",
    recent_events: Optional[List[Dict[str, Any]]] = None,
    world_name: str = "generated-world",
    agent_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a stable render context that can be consumed by image-generation prompts.

    This is the protocol boundary between deterministic world state and generative rendering.
    """
    tick = int(observation.get("tick", 0))
    location = str(observation.get("location", "unknown"))
    energy = int(observation.get("energy", 0))
    inventory = _sorted_inventory(dict(observation.get("inventory", {})))
    resources = _sorted_resources(dict(observation.get("resources", {})))
    local_resources = resources.get(location, {})

    global_summary = {
        "world": world_name,
        "tick": tick,
        "visible_location": location,
        "resource_nodes": len(resources),
    }

    camera_view = {
        "profile": camera_profile,
        "focus_agent": agent_id,
        "radius": max(1, int(radius)),
        "location": location,
    }

    entities_visible = [
        {
            "id": agent_id,
            "kind": "agent",
            "location": location,
            "energy": energy,
            "inventory": inventory,
        }
    ]

    normalized_events = list(recent_events or [])

    normalized_profile = dict(agent_profile or {})

    continuity_source = (
        f"{world_name}|{tick}|{camera_profile}|{agent_id}|{location}|"
        f"{inventory}|{local_resources}|{normalized_events}|{normalized_profile}"
    )
    continuity_tokens = {
        "scene_token": _stable_hash(continuity_source),
        "agent_anchor": _stable_hash(f"agent:{agent_id}"),
        "style_anchor": _stable_hash(f"style:{style_profile}"),
    }

    return {
        "version": "render-context.v0.1",
        "world_state_summary": global_summary,
        "camera_view": camera_view,
        "entities_visible": entities_visible,
        "local_resources": local_resources,
        "recent_events": normalized_events,
        "style_profile": style_profile,
        "agent_profile": normalized_profile,
        "continuity_tokens": continuity_tokens,
    }
