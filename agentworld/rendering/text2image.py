from __future__ import annotations

from typing import Any, Dict

from .context import build_render_context


def build_render_spec(observation: Dict[str, Any], agent_id: str, radius: int = 1) -> Dict[str, Any]:
    """Convert observe output to a stable render spec for visualization pipelines."""
    location = observation.get("location", "unknown")
    resources = observation.get("resources", {})
    local_resources = resources.get(location, {})

    return {
        "style": "topdown-text-world",
        "camera": {"focus_agent": agent_id, "radius": radius},
        "scene": {
            "tick": observation.get("tick", 0),
            "location": location,
            "agent": {
                "id": agent_id,
                "energy": observation.get("energy", 0),
                "inventory": observation.get("inventory", {}),
            },
            "local_resources": local_resources,
        },
        "legend": {
            "energy": "agent stamina level",
            "local_resources": "available resources at current location",
        },
    }


def build_image_prompt(render_spec: Dict[str, Any]) -> str:
    """Build deterministic text prompt for downstream text-to-image generation."""
    scene = render_spec["scene"]
    agent = scene["agent"]
    local_resources = scene.get("local_resources", {})

    return (
        "Illustrate a clean top-down simulation scene. "
        f"Tick {scene['tick']}, location '{scene['location']}'. "
        f"Focus on agent {agent['id']} with energy {agent['energy']} and inventory {agent['inventory']}. "
        f"Show nearby resources: {local_resources}. "
        "Style: minimal UI overlay, clear labels, no fantasy embellishment, faithful to simulation state."
    )


def build_image_prompt_from_context(render_context: Dict[str, Any]) -> str:
    """Build deterministic text prompt from RenderContext v0.1."""
    summary = render_context["world_state_summary"]
    camera = render_context["camera_view"]
    entities = render_context.get("entities_visible", [])
    local_resources = render_context.get("local_resources", {})
    continuity = render_context.get("continuity_tokens", {})
    style_profile = render_context.get("style_profile", "sim-minimal-v1")
    profile = render_context.get("agent_profile", {})
    events = render_context.get("recent_events", [])

    focus_entity = entities[0] if entities else {"id": camera.get("focus_agent", "unknown"), "energy": 0, "inventory": {}}

    return (
        "Render a deterministic simulation frame. "
        f"World '{summary['world']}', tick {summary['tick']}, camera profile {camera['profile']} at location '{camera['location']}'. "
        f"Focus agent {focus_entity['id']} energy {focus_entity.get('energy', 0)} inventory {focus_entity.get('inventory', {})}. "
        f"Agent profile: role={profile.get('role', 'unknown')}, persona={profile.get('persona', 'n/a')}, "
        f"strategy={profile.get('strategy', 'n/a')}, visual_anchor={profile.get('visual_anchor', 'n/a')}. "
        f"Local resources: {local_resources}. "
        f"Recent events: {events}. "
        f"Style profile: {style_profile}. "
        "Preserve identity and scene continuity with tokens "
        f"scene={continuity.get('scene_token', '')}, agent={continuity.get('agent_anchor', '')}, style={continuity.get('style_anchor', '')}. "
        "No fantasy additions; stay faithful to world state."
    )


def build_render_context_and_prompt(observation: Dict[str, Any], agent_id: str, radius: int = 1) -> Dict[str, Any]:
    context = build_render_context(observation, agent_id=agent_id, radius=radius)
    return {"render_context": context, "prompt": build_image_prompt_from_context(context)}
