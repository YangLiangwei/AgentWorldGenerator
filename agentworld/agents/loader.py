from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .profile import AgentProfile, default_profile


def load_profiles(path: str) -> Dict[str, AgentProfile]:
    data = json.loads(Path(path).read_text())
    out: Dict[str, AgentProfile] = {}
    for agent_id, payload in data.items():
        out[agent_id] = AgentProfile.from_dict(agent_id, payload)
    return out


def build_profiles_from_world(world_data: dict) -> Dict[str, AgentProfile]:
    agents = world_data.get("initial_state", {}).get("agents", {})
    out: Dict[str, AgentProfile] = {}
    for agent_id, info in agents.items():
        traits = info.get("traits", {})
        role = traits.get("role", "participant")
        profile_data = traits.get("profile")
        if isinstance(profile_data, dict):
            out[agent_id] = AgentProfile.from_dict(agent_id, {"role": role, **profile_data})
        else:
            out[agent_id] = default_profile(agent_id, role=role)
    return out
