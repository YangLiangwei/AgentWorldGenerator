from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentworld.compiler import compile_scene, draft_scene_ir_from_text


if __name__ == "__main__":
    # Example 1: compile from world DSL
    dsl_path = Path(__file__).with_name("world_dsl_v02.json")
    dsl = json.loads(dsl_path.read_text())
    spec = compile_scene(dsl)
    print("[DSL]", spec.name, "agents=", len(spec.initial_state.agents))

    # Example 2: compile from text -> IR -> spec
    text = "A service world with waiter, customer and manager roles"
    ir = draft_scene_ir_from_text(text)
    spec2 = compile_scene(ir)
    print("[TEXT]", spec2.name, "agents=", len(spec2.initial_state.agents))
