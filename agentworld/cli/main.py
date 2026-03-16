from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..compiler import compile_scene, draft_scene_ir_from_text
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

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
