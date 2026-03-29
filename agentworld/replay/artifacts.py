from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def snapshot_state(runtime: Any) -> Dict[str, Any]:
    return {
        "tick": runtime.state.tick,
        "agents": {
            aid: {
                "energy": a.energy,
                "location": a.location,
                "inventory": dict(a.inventory),
                "traits": dict(a.traits),
            }
            for aid, a in runtime.state.agents.items()
        },
        "resources": {loc: dict(pool) for loc, pool in runtime.state.resources.items()},
    }


def _write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows))


def write_run_artifacts(
    artifact_dir: str,
    *,
    events: List[Dict[str, Any]],
    snapshots: List[Dict[str, Any]],
    render_contexts: List[Dict[str, Any]],
    prompts: List[Dict[str, Any]],
) -> Dict[str, str]:
    out = Path(artifact_dir)
    out.mkdir(parents=True, exist_ok=True)

    p_events = out / "run.jsonl"
    p_states = out / "state_snapshots.jsonl"
    p_ctx = out / "render_context.jsonl"
    p_prompts = out / "prompt.jsonl"

    _write_jsonl(p_events, events)
    _write_jsonl(p_states, snapshots)
    _write_jsonl(p_ctx, render_contexts)
    _write_jsonl(p_prompts, prompts)

    return {
        "events": str(p_events),
        "states": str(p_states),
        "contexts": str(p_ctx),
        "prompts": str(p_prompts),
    }


def build_replay_html(artifact_dir: str, out_html: str) -> str:
    base = Path(artifact_dir)
    events = (base / "run.jsonl").read_text() if (base / "run.jsonl").exists() else ""
    states = (base / "state_snapshots.jsonl").read_text() if (base / "state_snapshots.jsonl").exists() else ""
    contexts = (base / "render_context.jsonl").read_text() if (base / "render_context.jsonl").exists() else ""
    prompts = (base / "prompt.jsonl").read_text() if (base / "prompt.jsonl").exists() else ""

    html = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>AgentWorld Replay</title>
<style>body{{font-family:system-ui;margin:20px}} pre{{white-space:pre-wrap;background:#f5f5f5;padding:10px}} .row{{display:flex;gap:16px}} .col{{flex:1}}</style>
</head><body>
<h2>AgentWorld Minimal Replay</h2>
<p>Use slider to inspect snapshots and related context/prompt.</p>
<input id='tick' type='range' min='0' max='0' value='0' style='width:100%'/><div id='tlabel'></div>
<div class='row'>
<div class='col'><h3>State</h3><pre id='state'></pre></div>
<div class='col'><h3>Events@Tick</h3><pre id='events'></pre></div>
</div>
<div class='row'>
<div class='col'><h3>Render Context</h3><pre id='ctx'></pre></div>
<div class='col'><h3>Prompt</h3><pre id='prompt'></pre></div>
</div>
<script>
const statesRaw = `{states}`.trim().split(/\n+/).filter(Boolean).map(x=>JSON.parse(x));
const eventsRaw = `{events}`.trim().split(/\n+/).filter(Boolean).map(x=>JSON.parse(x));
const ctxRaw = `{contexts}`.trim().split(/\n+/).filter(Boolean).map(x=>JSON.parse(x));
const promptRaw = `{prompts}`.trim().split(/\n+/).filter(Boolean).map(x=>JSON.parse(x));
const slider = document.getElementById('tick');
slider.max = Math.max(0, statesRaw.length-1);
function draw(i){{
  const st = statesRaw[i] || {{}};
  const tk = st.tick ?? i;
  document.getElementById('tlabel').textContent = `tick = ${{tk}}`;
  document.getElementById('state').textContent = JSON.stringify(st, null, 2);
  document.getElementById('events').textContent = JSON.stringify(eventsRaw.filter(e=>e.tick===tk), null, 2);
  document.getElementById('ctx').textContent = JSON.stringify(ctxRaw[i] || {{}}, null, 2);
  document.getElementById('prompt').textContent = (promptRaw[i]||{{}}).prompt || '';
}}
slider.addEventListener('input', ()=>draw(Number(slider.value)));
draw(0);
</script>
</body></html>"""

    Path(out_html).write_text(html)
    return out_html
