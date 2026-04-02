from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def load_jsonl(path: str) -> List[Dict]:
    p = Path(path)
    if not p.exists():
        return []
    rows: List[Dict] = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def summarize_events(events: List[Dict]) -> Dict:
    total = len(events)
    success = sum(1 for e in events if str(e.get("result", "")).startswith("ok:"))
    failures = [e for e in events if str(e.get("result", "")).startswith("fail:")]

    error_codes: Dict[str, int] = {}
    action_totals: Dict[str, int] = {}
    action_failures: Dict[str, int] = {}
    for e in events:
        action = str(e.get("action", "unknown"))
        action_totals[action] = action_totals.get(action, 0) + 1

    for e in failures:
        code = str(e.get("result", "fail:unknown"))
        action = str(e.get("action", "unknown"))
        error_codes[code] = error_codes.get(code, 0) + 1
        action_failures[action] = action_failures.get(action, 0) + 1

    ticks = {int(e.get("tick", 0)) for e in events}
    dead_tick_ratio = 0.0
    if ticks:
        alive_ticks = {int(e.get("tick", 0)) for e in events if str(e.get("result", "")).startswith("ok:")}
        dead_tick_ratio = len(ticks - alive_ticks) / len(ticks)

    top_failures = sorted(error_codes.items(), key=lambda kv: kv[1], reverse=True)[:5]

    action_stats = {
        a: {
            "total": action_totals.get(a, 0),
            "failures": action_failures.get(a, 0),
            "failure_rate": (action_failures.get(a, 0) / action_totals.get(a, 1)),
        }
        for a in sorted(action_totals.keys())
    }

    return {
        "total_actions": total,
        "success_actions": success,
        "failure_actions": len(failures),
        "success_rate": (success / total) if total else 0.0,
        "dead_tick_ratio": dead_tick_ratio,
        "error_codes": error_codes,
        "top_failures": top_failures,
        "action_stats": action_stats,
    }
