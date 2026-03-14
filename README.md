# SimWorld MVP

Automatic Agent Simulation World Generator (MVP scaffold).

## Architecture (elegant, minimal)

1. **World Definition Layer** (`simworld/spec.py`)
   - Declarative world spec: entities/agents, actions, initial state, metrics.
2. **Simulation Runtime Layer** (`simworld/runtime.py`)
   - Deterministic `validate -> resolve -> log` tick execution.
3. **Agent Layer** (`simworld/agent.py`)
   - Unified `observe -> decide -> act` contract and baseline `RuleAgent`.
4. **Analytics/Event Layer** (`simworld/events.py`)
   - Append-only event log for replay and auditing.

### Generation Pipeline

`scenario text/dict -> Scene IR -> compiler -> WorldSpec -> Runtime`

Current MVP supports two compile paths in `simworld/compiler.py`:
- v0.1 runtime dict (`initial_state` + `actions`)
- v0.2 World DSL (`world` + `entities` + `resource_nodes`)

It also includes a deterministic text->Scene IR draft helper (`draft_scene_ir_from_text`) for rapid prototyping.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python examples/run_minimal.py
python -m unittest discover -s tests -q
```

## Atomic World Model (core contract)

SimWorld is being aligned to your four atomic primitives:
- **Observe**: `runtime.observe(agent_id)`
- **Object**: `runtime.get_object(object_id)`
- **Interaction**: `events.Interaction`
- **Outcome**: `events.Outcome` produced by runtime resolution

Rule: outcomes are resolved by the engine, never self-reported by agents.

## Why this structure

- Deterministic core for reproducibility.
- LLM-friendly edges (compiler/agent), not state authority.
- Event sourcing for replay, A/B diff, and explainability.
