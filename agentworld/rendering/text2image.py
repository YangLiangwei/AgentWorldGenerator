from __future__ import annotations

from typing import Any, Dict


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
