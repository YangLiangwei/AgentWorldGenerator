from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional


def _stable_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _sorted_inventory(inv: Dict[str, int]) -> Dict[str, int]:
    return {k: inv[k] for k in sorted(inv.keys())}


def _sorted_resources(resources: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
    return {loc: {k: resources[loc][k] for k in sorted(resources[loc].keys())} for loc in sorted(resources.keys())}


def _normalize_recent_events(recent_events: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for e in list(recent_events or []):
        tick = int(e.get("tick", 0))
        actor_id = str(e.get("actor_id", e.get("actor", "unknown")))
        action = str(e.get("action", "unknown"))
        result = str(e.get("result", "unknown"))
        target_id = e.get("target_id")
        tags = list(e.get("tags", []))
        if result.startswith("fail:") and "violation" not in tags:
            tags.append("violation")
        out.append(
            {
                "tick": tick,
                "actor_id": actor_id,
                "action": action,
                "result": result,
                "target_id": target_id,
                "tags": tags,
            }
        )
    return out


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
    """Build RenderContext v0.2 from deterministic world observation."""
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

    normalized_events = _normalize_recent_events(recent_events)
    normalized_profile = dict(agent_profile or {})

    continuity_tokens = {
        "identity_token": _stable_hash(f"agent:{agent_id}|profile:{normalized_profile}"),
        "scene_token": _stable_hash(
            f"world:{world_name}|tick:{tick}|camera:{camera_profile}|loc:{location}|res:{local_resources}"
        ),
        "history_token": _stable_hash(f"events:{normalized_events}"),
        "style_token": _stable_hash(f"style:{style_profile}"),
    }

    return {
        "version": "render-context.v0.2",
        "world_state_summary": global_summary,
        "camera_view": camera_view,
        "entities_visible": entities_visible,
        "local_resources": local_resources,
        "recent_events": normalized_events,
        "style_profile": style_profile,
        "agent_profile": normalized_profile,
        "continuity_tokens": continuity_tokens,
    }


def upgrade_render_context(render_context: Dict[str, Any]) -> Dict[str, Any]:
    """Upgrade v0.1 context payload to v0.2 (best-effort, deterministic)."""
    version = render_context.get("version")
    if version == "render-context.v0.2":
        return render_context

    if version == "render-context.v0.1":
        old_tokens = dict(render_context.get("continuity_tokens", {}))
        events = _normalize_recent_events(render_context.get("recent_events", []))
        upgraded = dict(render_context)
        upgraded["version"] = "render-context.v0.2"
        upgraded["recent_events"] = events
        upgraded["continuity_tokens"] = {
            "identity_token": old_tokens.get("agent_anchor", ""),
            "scene_token": old_tokens.get("scene_token", ""),
            "history_token": _stable_hash(f"events:{events}"),
            "style_token": old_tokens.get("style_anchor", ""),
        }
        return upgraded

    raise ValueError(f"Unsupported render context version: {version}")
