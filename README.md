# AgentWorldGenerator

Agent-native simulation world engine + generator (MVP).

## Architecture

- `agentworld/core`: deterministic runtime (`observe/object/interaction/outcome`)
- `agentworld/schema`: declarative world schema + spec loading
- `agentworld/compiler`: scene pipeline (`text -> scene IR -> world spec`)
- `agentworld/validators`: static checks for generated worlds
- `agentworld/protocol`: protocol versions + upgrader/validator entrypoints (RenderContext + ActionSchema)
- `agentworld/cli`: command-line entry (`awg`)
- `agentworld/rules`: reusable rule middleware (queue/access/transfer)
- `agentworld/plugins`: plugin contracts + registry (RulePack/ActionPack/RenderPack)

## Atomic World Contract

Every generated world follows four atoms:
- **Observe**: read local state
- **Object**: everything is an object with state
- **Interaction**: only legal interactions can be submitted
- **Outcome**: state transitions are resolved by engine rules (not self-reported)

## Quickstart

```bash
python examples/run_minimal.py
python examples/compile_scene_demo.py
python -m unittest discover -s tests -q
```

## CLI (MVP)

```bash
python -m agentworld.cli.main generate "a university world with labs and students" --out world.generated.json
python -m agentworld.cli.main validate world.generated.json
python -m agentworld.cli.main run world.generated.json --ticks 30 --log run.jsonl --artifact-dir artifacts
python -m agentworld.cli.main diag artifacts
python -m agentworld.cli.main render world.generated.json --agent agent_professor_1 --ticks 10 --out render_spec.json --context-out render_context.json --prompt-out image_prompt.txt
```

`render_context.json` now follows **RenderContext v0.2** (`agentworld/rendering/render_context_v0_2.schema.json`),
with backward-compatible upgrade support for v0.1 payloads.

Current generator has deterministic IR presets for broad scene families:
- hospital / clinic
- university / lab
- service / restaurant
- generic fallback

AgentProfile v1 (current):
- compiler emits default `traits.profile` for generated agents
- `run` supports `--profiles <json>` override file
- `render` reads profile and injects identity anchors into RenderContext/prompt

## Notes

- `simworld/*` modules are kept as compatibility shims.
- Current text generation is deterministic heuristic draft; richer NL compilation is next.
