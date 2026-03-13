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

Current MVP provides dict->`WorldSpec` compilation in `simworld/compiler.py` with TODO hooks for NL->IR.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python examples/run_minimal.py
python -m unittest discover -s tests -q
```

## Why this structure

- Deterministic core for reproducibility.
- LLM-friendly edges (compiler/agent), not state authority.
- Event sourcing for replay, A/B diff, and explainability.
