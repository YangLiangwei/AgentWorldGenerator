from __future__ import annotations

from typing import Any, Dict

from ..rendering.context import upgrade_render_context


def upgrade_render_context_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return upgrade_render_context(payload)


def validate_render_context(payload: Dict[str, Any]) -> None:
    version = payload.get("version")
    if version not in {"render-context.v0.1", "render-context.v0.2"}:
        raise ValueError(f"unsupported render context version: {version}")
    required = {"world_state_summary", "camera_view", "entities_visible", "local_resources", "recent_events", "style_profile", "continuity_tokens"}
    missing = [k for k in required if k not in payload]
    if missing:
        raise ValueError(f"invalid render context; missing fields: {missing}")
