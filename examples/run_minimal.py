from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentworld.agents import RuleAgent
from agentworld.compiler import compile_scene
from agentworld.core import SimulationRuntime


if __name__ == "__main__":
    spec_path = Path(__file__).with_name("world_minimal.json")
    scene = json.loads(spec_path.read_text())
    spec = compile_scene(scene)
    runtime = SimulationRuntime(spec)
    agents = {aid: RuleAgent(aid) for aid in runtime.state.agents.keys()}

    for _ in range(5):
        decisions = {}
        for aid, ag in agents.items():
            ag.observe(runtime.observe(aid))
            d = ag.decide()
            decisions[aid] = {"action": d.action, "params": d.params}
        runtime.run_tick(decisions)

    print("tick=", runtime.state.tick)
    for aid, st in runtime.state.agents.items():
        print(aid, "energy=", st.energy, "inventory=", st.inventory)
    print("events=", len(runtime.log.all()))
