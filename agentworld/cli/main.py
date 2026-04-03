from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..agents import RuleAgent, build_profiles_from_world, load_profiles
from ..compiler import compile_scene, draft_scene_ir_from_text
from ..core import SimulationRuntime, validate_proposals
from ..orchestrator import Orchestrator, OrchestratorConfig, RunTask
from ..packs.dota_duel_lite import DotaDuelActionPack, propose_dota_actions
from ..rendering import build_image_prompt_from_context, build_render_context, build_render_spec
from ..replay import build_replay_html, load_jsonl, snapshot_state, summarize_events, write_run_artifacts
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

    profiles = load_profiles(args.profiles) if args.profiles else build_profiles_from_world(data)
    agents = {aid: RuleAgent(aid, profile=profiles.get(aid)) for aid in runtime.state.agents.keys()}

    ticks = min(args.ticks, spec.max_ticks)
    snapshots = []
    render_contexts = []
    prompts = []

    for _ in range(ticks):
        decisions = {}
        for aid, agent in agents.items():
            agent.observe(runtime.observe(aid))
            d = agent.decide()
            decisions[aid] = {"action": d.action, "params": d.params}
        runtime.run_tick(decisions)

        snapshots.append(snapshot_state(runtime))

        # Keep one canonical viewpoint for replay debugging
        focus_agent = sorted(runtime.state.agents.keys())[0]
        obs = runtime.observe(focus_agent)
        profile = profiles.get(focus_agent)
        ctx = build_render_context(
            obs,
            agent_id=focus_agent,
            radius=1,
            camera_profile="topdown",
            style_profile="sim-minimal-v1",
            world_name=spec.name,
            agent_profile=(
                {
                    "role": profile.role,
                    "persona": profile.persona,
                    "strategy": profile.strategy,
                    "visual_anchor": profile.visual_anchor,
                }
                if profile
                else None
            ),
        )
        render_contexts.append(ctx)
        prompts.append({"tick": runtime.state.tick, "agent_id": focus_agent, "prompt": build_image_prompt_from_context(ctx)})

    print(f"run: ticks={runtime.state.tick} agents={len(runtime.state.agents)} events={len(runtime.log.all())}")

    if args.log:
        Path(args.log).write_text(runtime.log.to_jsonl())
        print(f"log: {args.log}")

    if args.artifact_dir:
        events = [
            {
                "tick": e.tick,
                "actor_id": e.actor_id,
                "action": e.action,
                "payload": e.payload,
                "result": e.result,
            }
            for e in runtime.log.all()
        ]
        paths = write_run_artifacts(
            args.artifact_dir,
            events=events,
            snapshots=snapshots,
            render_contexts=render_contexts,
            prompts=prompts,
        )
        print(f"artifacts: {paths}")

    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    out = build_replay_html(args.artifact_dir, args.out)
    print(f"replay_html: {out}")
    return 0


def cmd_diag(args: argparse.Namespace) -> int:
    events = load_jsonl(str(Path(args.artifact_dir) / "run.jsonl"))
    summary = summarize_events(events)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_orchestrate(args: argparse.Namespace) -> int:
    tasks_data = json.loads(Path(args.tasks).read_text())
    orch = Orchestrator(
        OrchestratorConfig(
            max_concurrency=args.max_concurrency,
            max_retries=args.max_retries,
            max_ticks_per_task=args.max_ticks,
        )
    )
    for t in tasks_data:
        orch.submit(
            RunTask(
                task_id=t["task_id"],
                world_path=t["world_path"],
                ticks=int(t.get("ticks", 20)),
                retries=int(t.get("retries", 1)),
                artifact_dir=t.get("artifact_dir", ""),
            )
        )
    results = orch.run_all()
    out = [r.__dict__ for r in results]
    if args.out:
        Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
        print(f"orchestrator_results: {args.out}")
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_play_step(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.world).read_text())
    spec = compile_scene(data)
    rt = SimulationRuntime(spec)
    DotaDuelActionPack().register_handlers(rt)

    if args.actor not in rt.state.agents or args.target not in rt.state.agents:
        print("play-step aborted: actor or target not found")
        return 1

    proposals = propose_dota_actions(rt, args.actor, args.target)
    proposals = validate_proposals(rt, args.actor, proposals)
    if not proposals:
        print("no valid proposals")
        return 1

    if args.select < 0 or args.select >= len(proposals):
        print(json.dumps([p.__dict__ for p in proposals], ensure_ascii=False, indent=2))
        return 0

    chosen = proposals[args.select]
    out = rt.step_action(args.actor, chosen.action, chosen.params)
    print(json.dumps({"chosen": chosen.__dict__, "outcome": out.result, "delta": out.state_delta}, ensure_ascii=False, indent=2))
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
    profiles = load_profiles(args.profiles) if args.profiles else build_profiles_from_world(data)

    # Optional warmup so render reflects evolved state.
    warmup = max(0, min(args.ticks, spec.max_ticks))
    if warmup > 0:
        agents = {aid: RuleAgent(aid, profile=profiles.get(aid)) for aid in runtime.state.agents.keys()}
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
    profile = profiles.get(args.agent)
    render_context = build_render_context(
        obs,
        agent_id=args.agent,
        radius=args.radius,
        camera_profile=args.camera_profile,
        style_profile=args.style_profile,
        world_name=spec.name,
        agent_profile=(
            {
                "role": profile.role,
                "persona": profile.persona,
                "strategy": profile.strategy,
                "visual_anchor": profile.visual_anchor,
            }
            if profile
            else None
        ),
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
    p_run.add_argument("--artifact-dir", default="", help="optional directory for replay/debug artifacts")
    p_run.add_argument("--profiles", default="", help="optional JSON file mapping agent_id -> AgentProfile")
    p_run.set_defaults(func=cmd_run)

    p_replay = sub.add_parser("replay", help="Build minimal HTML replay from run artifacts")
    p_replay.add_argument("artifact_dir")
    p_replay.add_argument("--out", default="replay.html")
    p_replay.set_defaults(func=cmd_replay)

    p_diag = sub.add_parser("diag", help="Summarize run diagnostics from artifacts")
    p_diag.add_argument("artifact_dir")
    p_diag.set_defaults(func=cmd_diag)

    p_orch = sub.add_parser("orchestrate", help="Run queued tasks with retries and quotas")
    p_orch.add_argument("tasks", help="json file containing task list")
    p_orch.add_argument("--max-concurrency", type=int, default=1)
    p_orch.add_argument("--max-retries", type=int, default=2)
    p_orch.add_argument("--max-ticks", type=int, default=1000)
    p_orch.add_argument("--out", default="")
    p_orch.set_defaults(func=cmd_orchestrate)

    p_step = sub.add_parser("play-step", help="NL-style control: propose 3 actions and optionally execute one (Dota pack demo)")
    p_step.add_argument("world")
    p_step.add_argument("--actor", required=True)
    p_step.add_argument("--target", required=True)
    p_step.add_argument("--nl", default="")
    p_step.add_argument("--select", type=int, default=-1, help="index of proposal to execute; -1 prints proposals only")
    p_step.set_defaults(func=cmd_play_step)

    p_render = sub.add_parser("render", help="Build render spec and text2image prompt from agent observation")
    p_render.add_argument("world")
    p_render.add_argument("--agent", required=True)
    p_render.add_argument("--radius", type=int, default=1)
    p_render.add_argument("--camera-profile", default="topdown", choices=["topdown", "first_person", "cinematic"])
    p_render.add_argument("--style-profile", default="sim-minimal-v1")
    p_render.add_argument("--ticks", type=int, default=0, help="optional warmup ticks before render")
    p_render.add_argument("--profiles", default="", help="optional JSON file mapping agent_id -> AgentProfile")
    p_render.add_argument("--out", default="")
    p_render.add_argument("--context-out", default="")
    p_render.add_argument("--prompt-out", default="")
    p_render.set_defaults(func=cmd_render)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
