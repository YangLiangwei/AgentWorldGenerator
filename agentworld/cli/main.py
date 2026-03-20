from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..agents import RuleAgent
from ..compiler import compile_scene, draft_scene_ir_from_text
from ..core import SimulationRuntime
from ..rendering import build_image_prompt_from_context, build_render_context, build_render_spec
from ..validators import validate_world_report


def cmd_generate(args: argparse.Namespace) -> int:
    ir = draft_scene_ir_from_text(args.description)
    spec = compile_scene(ir)
    out = {
        "name": spec.name,
        "max_ticks": spec.max_ticks,
        "actions": {k: {"cost": v.cost, "params": v.params} for k, v in spec.actions.items()},
        "initial_state": {
            "tick": spec.initial_state.tick,
            "resources": spec.initial_state.resources,
            "agents": {
                aid: {
                    "energy": a.energy,
                    "location": a.location,
                    "inventory": a.inventory,
                    "traits": a.traits,
                }
                for aid, a in spec.initial_state.agents.items()
            },
        },
        "metrics": spec.metrics,
        "rules": spec.rules,
        "constraints": spec.constraints,
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"generated: {args.out}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.world).read_text())
    report = validate_world_report(data)
    for issue in report.issues:
        print(f"[{issue.level}] {issue.message}")
    print(f"summary: ok={report.ok} errors={report.errors} warnings={report.warnings}")
    return 0 if report.ok else 1


def cmd_run(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.world).read_text())
    report = validate_world_report(data)
    if not report.ok:
        for issue in report.issues:
            print(f"[{issue.level}] {issue.message}")
        print("run aborted: invalid world")
        return 1

    spec = compile_scene(data)
    runtime = SimulationRuntime(spec)
    agents = {aid: RuleAgent(aid) for aid in runtime.state.agents.keys()}

    ticks = min(args.ticks, spec.max_ticks)
    for _ in range(ticks):
        decisions = {}
        for aid, agent in agents.items():
            agent.observe(runtime.observe(aid))
            d = agent.decide()
            decisions[aid] = {"action": d.action, "params": d.params}
        runtime.run_tick(decisions)

    print(f"run: ticks={runtime.state.tick} agents={len(runtime.state.agents)} events={len(runtime.log.all())}")

    if args.log:
        Path(args.log).write_text(runtime.log.to_jsonl())
        print(f"log: {args.log}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.world).read_text())
    report = validate_world_report(data)
    if not report.ok:
        for issue in report.issues:
            print(f"[{issue.level}] {issue.message}")
        print("render aborted: invalid world")
        return 1

    spec = compile_scene(data)
    runtime = SimulationRuntime(spec)

    # Optional warmup so render reflects evolved state.
    warmup = max(0, min(args.ticks, spec.max_ticks))
    if warmup > 0:
        agents = {aid: RuleAgent(aid) for aid in runtime.state.agents.keys()}
        for _ in range(warmup):
            decisions = {}
            for aid, agent in agents.items():
                agent.observe(runtime.observe(aid))
                d = agent.decide()
                decisions[aid] = {"action": d.action, "params": d.params}
            runtime.run_tick(decisions)

    if args.agent not in runtime.state.agents:
        print(f"render aborted: unknown agent '{args.agent}'")
        return 1

    obs = runtime.observe(args.agent)
    render_spec = build_render_spec(obs, agent_id=args.agent, radius=args.radius)
    render_context = build_render_context(
        obs,
        agent_id=args.agent,
        radius=args.radius,
        camera_profile=args.camera_profile,
        style_profile=args.style_profile,
        world_name=spec.name,
    )
    prompt = build_image_prompt_from_context(render_context)

    if args.out:
        Path(args.out).write_text(json.dumps(render_spec, ensure_ascii=False, indent=2))
        print(f"render_spec: {args.out}")

    if args.context_out:
        Path(args.context_out).write_text(json.dumps(render_context, ensure_ascii=False, indent=2))
        print(f"render_context: {args.context_out}")

    if args.prompt_out:
        Path(args.prompt_out).write_text(prompt)
        print(f"prompt: {args.prompt_out}")
    else:
        print(prompt)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="awg", description="AgentWorldGenerator CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate world spec from one-line description")
    p_gen.add_argument("description")
    p_gen.add_argument("--out", default="world.generated.json")
    p_gen.set_defaults(func=cmd_generate)

    p_val = sub.add_parser("validate", help="Validate world spec json")
    p_val.add_argument("world")
    p_val.set_defaults(func=cmd_validate)

    p_run = sub.add_parser("run", help="Run a world with baseline rule agents")
    p_run.add_argument("world")
    p_run.add_argument("--ticks", type=int, default=20)
    p_run.add_argument("--log", default="")
    p_run.set_defaults(func=cmd_run)

    p_render = sub.add_parser("render", help="Build render spec and text2image prompt from agent observation")
    p_render.add_argument("world")
    p_render.add_argument("--agent", required=True)
    p_render.add_argument("--radius", type=int, default=1)
    p_render.add_argument("--camera-profile", default="topdown", choices=["topdown", "first_person", "cinematic"])
    p_render.add_argument("--style-profile", default="sim-minimal-v1")
    p_render.add_argument("--ticks", type=int, default=0, help="optional warmup ticks before render")
    p_render.add_argument("--out", default="")
    p_render.add_argument("--context-out", default="")
    p_render.add_argument("--prompt-out", default="")
    p_render.set_defaults(func=cmd_render)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
